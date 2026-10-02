#!/bin/sh
# Repository guardrails for BMEN 600 Group 5.
#
#   sh tools/repo_checks.sh staged      run by .githooks/pre-commit before every commit
#   sh tools/repo_checks.sh all         run by GitHub Actions on every push to main and pull request
#   sh tools/repo_checks.sh pr <base>   run by GitHub Actions on pull requests (two-lane rule)
#
# "staged" checks what is about to be committed:
#   1. the two-lane rule: on main, only coordination files; on any other branch, none
#   2. no merge-conflict markers
#   3. no file larger than MAX_MB megabytes
#   4. no files that look like secrets (.env, private keys)
#   5. ruff lint and format on staged Python files and notebooks
#      (skipped with a note when ruff is not installed; GitHub still checks)
# "all" runs checks 2 to 4 on every tracked file. GitHub runs ruff itself.
# "pr" fails if a pull request changes coordination files, which belong on main.
#
# Plain POSIX sh on purpose, so it behaves the same in Git Bash on Windows,
# on macOS and on Linux. In a real emergency, and only with your human's OK,
# a commit can skip these checks with: git commit --no-verify

MAX_MB=10
mode=${1:-staged}
status=0
nl='
'

block() {
	status=1
	printf '\nBLOCKED: %s\n' "$1" >&2
	if [ -n "$2" ]; then printf '%s' "$2" >&2; fi
	if [ -n "$3" ]; then printf '%s\n' "$3" >&2; fi
}

is_coordination() {
	case "$1" in
	TASKS.md | DECISIONS.md | members/*/handoff.md | members/*/log.md) return 0 ;;
	*) return 1 ;;
	esac
}

case "$mode" in
staged)
	changed=$(git -c core.quotepath=off diff --cached --name-only --no-renames)
	content=$(git -c core.quotepath=off diff --cached --name-only --no-renames --diff-filter=AM)
	;;
all)
	changed=""
	content=$(git -c core.quotepath=off ls-files)
	;;
pr)
	if [ -z "$2" ]; then
		echo "usage: sh tools/repo_checks.sh pr <base commit>" >&2
		exit 2
	fi
	changed=$(git -c core.quotepath=off diff --name-only --no-renames "$2" HEAD) || exit 2
	content=""
	;;
*)
	echo "usage: sh tools/repo_checks.sh [staged | all | pr <base commit>]" >&2
	exit 2
	;;
esac

# 1. Two-lane rule.
lane_files=""
if [ "$mode" = staged ]; then
	# Skip while git is finishing a merge, rebase, cherry-pick or revert: those
	# commits legitimately carry changes from the other lane.
	busy=no
	for marker in MERGE_HEAD CHERRY_PICK_HEAD REVERT_HEAD rebase-merge rebase-apply; do
		if [ -e "$(git rev-parse --git-path "$marker")" ]; then busy=yes; fi
	done
	branch=$(git symbolic-ref --quiet --short HEAD 2>/dev/null)
	if [ "$busy" = no ] && [ -n "$branch" ]; then
		while IFS= read -r f; do
			[ -z "$f" ] && continue
			if [ "$branch" = main ]; then
				is_coordination "$f" || lane_files="$lane_files    $f$nl"
			else
				is_coordination "$f" && lane_files="$lane_files    $f$nl"
			fi
		done <<EOF
$changed
EOF
		if [ -n "$lane_files" ] && [ "$branch" = main ]; then
			block "work files committed directly on main:" "$lane_files" \
"Only TASKS.md, DECISIONS.md and members/<name>/handoff.md or log.md go straight on main.
Move this work to your own branch (your uncommitted changes come with you):
    git switch -c <name>/<task-id>-<slug>
then commit there. See CLAUDE.md section 3."
		elif [ -n "$lane_files" ]; then
			block "coordination files committed on branch '$branch':" "$lane_files" \
"These are only edited on main, so everyone sees them straight away. Unstage them with
    git reset -q -- <file>
commit the rest here, then make the coordination edit on main (CLAUDE.md section 7)."
		fi
	fi
elif [ "$mode" = pr ]; then
	while IFS= read -r f; do
		[ -z "$f" ] && continue
		is_coordination "$f" && lane_files="$lane_files    $f$nl"
	done <<EOF
$changed
EOF
	if [ -n "$lane_files" ]; then
		block "this pull request changes coordination files:" "$lane_files" \
"Those are only edited directly on main (CLAUDE.md section 3). Remove these changes from
the branch, for example with: git checkout origin/main -- <file>, then commit and push."
	fi
fi

# 2 to 4. Conflict markers, file size, secrets.
big=""
markers=""
secrets=""
limit=$((MAX_MB * 1024 * 1024))
while IFS= read -r f; do
	[ -z "$f" ] && continue
	case "$f" in
	*.env.example) ;;
	.env | */.env | .env.* | */.env.*) secrets="$secrets    $f$nl" ;;
	*.pem | *.key | *.p12 | *.pfx | *id_rsa* | *id_ed25519*) secrets="$secrets    $f$nl" ;;
	esac
	size=$(git cat-file -s ":$f" 2>/dev/null) || continue
	if [ "$size" -gt "$limit" ]; then
		big="$big    $f ($((size / 1024 / 1024)) MB)$nl"
		continue
	fi
	hits=$(git cat-file -p ":$f" 2>/dev/null | grep -nIE '^(<{7}|>{7}|[|]{7})( |$)' | head -n 3)
	if [ -n "$hits" ]; then
		markers="$markers    $f$nl$(printf '%s\n' "$hits" | sed 's/^/        line /')$nl"
	fi
done <<EOF
$content
EOF

if [ -n "$big" ]; then
	block "files over $MAX_MB MB:" "$big" \
"Datasets belong in data/raw/, which git ignores; write down how to download them instead.
Take a file out of this commit with: git reset -q -- <file>
(if it is already committed: git rm --cached <file>)"
fi
if [ -n "$markers" ]; then
	block "merge-conflict markers left in:" "$markers" \
"Finish resolving the conflict in those files (keep the right lines and delete the
marker lines), then git add them again."
fi
if [ -n "$secrets" ]; then
	block "files that look like secrets:" "$secrets" \
"Never commit passwords, tokens or keys: this repository is public.
Take a file out of this commit with: git reset -q -- <file>
(if it is already committed: git rm --cached <file>)"
fi

# 5. Ruff on staged Python files and notebooks.
if [ "$mode" = staged ]; then
	set --
	while IFS= read -r f; do
		case "$f" in
		*.py | *.ipynb) if [ -f "$f" ]; then set -- "$@" "$f"; fi ;;
		esac
	done <<EOF
$content
EOF
	if [ "$#" -gt 0 ]; then
		if command -v ruff >/dev/null 2>&1; then
			ruff_ok=yes
			ruff check --force-exclude "$@" >&2 || ruff_ok=no
			ruff format --check --force-exclude "$@" >&2 || ruff_ok=no
			if [ "$ruff_ok" = no ]; then
				block "ruff found problems in the Python files being committed (details above)." "" \
"Fix them, stage them again and commit (lint fixes first, then the formatter):
    ruff check --fix <files>
    ruff format <files>
    git add <files>"
			fi
		else
			printf '%s\n' \
				"note: ruff is not installed, so Python style was not checked here (GitHub still checks it)." \
				"      Install it with: python -m pip install -r requirements-dev.txt" >&2
		fi
	fi
fi

if [ "$status" -ne 0 ]; then
	printf '\n%s\n' "Stopped by tools/repo_checks.sh ($mode). Fix the above and try again." >&2
elif [ "$mode" = staged ]; then
	echo "repo checks: OK" >&2
fi
exit "$status"
