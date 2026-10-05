# Agent protocol: BMEN 600 Group 5

You are one of several AI agents working in this repository. Each team member runs their own agents (Claude Code in a terminal, the desktop app or the web, Claude with this repo attached, sometimes another tool), on their own machines and often at the same time. None of you can see each other's conversations. **The files in this repository are the only shared memory.** They are how you learn what the others did and how you tell them what you did. Follow this protocol exactly.

This repo is **public** and it is **graded**: the README, code, organisation and commit history are marked with the Midterm Research Plan (due Fri Oct 16) and the Final Project (due Fri Dec 4). Write everything as if the instructors will read it.

## 1. Who you work for

| Member | Short name | Their branches | Their files |
|---|---|---|---|
| Jamie Sanson | `jamie` | `jamie/...` | `members/jamie/` |
| Anna Klygina | `anna` | `anna/...` | `members/anna/` |
| Yassien Tawfik | `yassien` | `yassien/...` | `members/yassien/` |

Before anything else, establish which member you are working for: from what your human has told you, or from `git config user.name`. If it is still unclear, ask: "Which team member am I working for?" Never guess. You act for that one person, and you edit only their files, branches and tasks.

Commits are authored by your human, so their contribution stays identifiable (the rubric checks this), and every commit you make credits the AI in a trailer. The exact wording of the trailer does not matter (`Co-Authored-By: Claude <noreply@anthropic.com>`, or whatever your tool adds by default), as long as it names the tool:

    git commit -m "[T-007] Add stride segmentation" -m "Co-Authored-By: Claude <noreply@anthropic.com>"

If `git config user.name` is not your human (common in cloud sessions), ask them once for the name and email they use on GitHub and pass `--author="Name <email>"`.

## 2. The files you coordinate through

| File | What it holds | Who edits it |
|---|---|---|
| `TASKS.md` | Deadlines and the task board. Claims happen here. | Anyone, one task at a time |
| `DECISIONS.md` | What the group has decided. Append-only. | Appended when your human says the group decided something |
| `members/<short>/handoff.md` | That member's current state, one section per active task. | Only that member's agents |
| `members/<short>/log.md` | That member's history: work done, CRediT roles, AI use, how it was verified. Append-only. The paper's Author Contributions and AI-Assisted Work sections are written from these. | Only that member's agents |

Times in these files are Calgary time (`TZ=America/Edmonton date`).

## 3. Two lanes: the rule everything else depends on

- **Coordination lane: commit directly on `main` and push immediately.** Only the four kinds of file above: `TASKS.md`, `DECISIONS.md`, `members/*/handoff.md`, `members/*/log.md`. Pushing them straight away is what lets every other agent see them on its next pull.
- **Work lane: your own branch, merged into `main` by pull request.** Everything else: code, notebooks, README, report material, figures, config files such as `.gitignore` or `pyproject.toml`, and this file. Branch name `<short>/<task-id>-<slug>`, where the slug is two or three words from the task title, lowercase and hyphenated: `anna/T-007-project-structure`. The team contract says we each keep to our own branches.

Never commit coordination files on a work branch, and never commit work files directly on `main`. The pre-commit hook blocks both once it is switched on (section 4, step 3), and prints `repo checks: OK` when a commit passes.

## 4. Start of every session

Claude Code users can type `/start` (or `/start T-007` to also claim a task). Otherwise:

1. **Look before touching anything.** Run `git status -sb` and `git stash list`. If there are uncommitted or stashed changes, work out whose they are. Your human's unfinished work from an earlier session: commit it on its branch (`[T-007] WIP ...`) and push it. Anything you cannot explain: stop and ask. Never discard, reset or overwrite it.
2. **Get current.** `git switch main && git pull --rebase`
3. **One-time setup, if missing.** `git config core.hooksPath` should print `.githooks`; if it does not, run `git config core.hooksPath .githooks`. `ruff --version` should work; if it does not, run `python -m pip install -r requirements-dev.txt` (`python3` on a Mac); if you cannot install it where the commits are made, say so and move on, GitHub runs the same checks. If your human's setup task on the board (T-003, T-004 or T-005) is still `todo` and the hook is on, set it to `done` on `main` and say so.
4. **Read**, in this order: `TASKS.md`; `DECISIONS.md`; your human's `members/<short>/handoff.md`; the other members' `handoff.md` files (look for `@<short>`); `git log --oneline -15`. If your human's own folder is missing, create it by copying `members/_template/` and filling in their name (coordination lane). If another member's folder is missing, skip it and mention that in your report.
5. **Report to your human**, in about ten lines:

   ```
   Next deadline: <next course deadline from the table in TASKS.md, with days left; plus your human's earliest open due date, if sooner>
   Since your last session: <merged pull requests, claims, decisions since the latest entry in your human's log.md; or "nothing new">
   For you: <@mentions in teammates' handoffs, review requests; or "nothing">
   Your tasks: <ID, title, status>
   Unclaimed: <up to 3 task IDs with titles; or "none">
   Suggested next step: <one concrete action>
   ```

   Then wait for them to choose, unless they already told you what to do.

Pull again before every claim, before every push to `main`, and whenever you have been idle for an hour or more. The others keep moving.

## 5. Claiming a task

Never start work that is not claimed. A task can be claimed when its `owner` is `-` or your human and its `status` is `todo`. A task with another owner is theirs, even if it looks abandoned: ask your human to check with them. A task whose title says *after T-xxx* can be claimed, but only for the parts that do not depend on T-xxx; say what is waiting under *Blocked* in your handoff.

1. `git switch main && git pull --rebase`
2. In `TASKS.md`, find the task and edit only its metadata line: `owner` = your short name, `status: doing`, `branch` = the branch you are about to create, `updated` = today (`date +%F`). If the task does not exist yet, add it at the end of the board with the next unused ID. IDs are permanent: never renumber or reuse one that has been pushed.
3. `git add TASKS.md && git commit -m "[T-007] Claim (anna)" -m "Co-Authored-By: Claude <noreply@anthropic.com>" && git push`
4. If the push is rejected, someone else pushed first. Run `git pull --rebase`.
   - No conflict: run `git push` again.
   - Conflict in `TASKS.md`: open it. During a rebase, the block above the `=======` line is what is already on GitHub and the block below it is yours. If the GitHub side shows that someone else claimed your task, you lost the race: run `git rebase --skip` (this drops your claim and keeps theirs), tell your human, and pick something else. Otherwise (usually two new tasks added at the end at the same moment) keep both sides, give yours the next free ID, delete the marker lines, then `git add TASKS.md && git rebase --continue && git push`.
5. Create your branch from the fresh `main` and publish it: `git switch -c anna/T-007-project-structure && git push -u origin anna/T-007-project-structure`

Statuses: `todo` (not started; if it has an owner, it is assigned to them), `doing`, `review` (finished; pull request open, or waiting for your human to open it, see their handoff), `done` (merged), `blocked` (say why in your handoff), `decide` (needs a group decision: never start it, raise it with your human).

## 6. Doing the work

- Stay inside your task. If you have to touch a file that another open task is changing (check the `branch` fields on the board), say so under *For teammates* in your handoff and in your pull request.
- Commit small and often (`[T-007] what changed`). Push your branch at every stopping point: nothing should exist on only one machine.
- Keep your branch current by merging `main` into it: `git fetch origin && git merge origin/main`. Do not rebase a branch you have already pushed; that needs a force-push, and force-pushing is blocked.
- Python: run `ruff check --fix <files>` and then `ruff format <files>` before committing (that order; the lint fixes can leave gaps the formatter then wants to close). The hook and GitHub run the same checks.
- New Python package: add it to `requirements.txt` in the same commit.
- Data: never commit datasets. Raw data goes in `data/raw/`, which git ignores except for its `README.md`; write the download steps, licence and version in that README.

## 7. Stopping, finishing, handing off

Claude Code users: `/handoff`. Do this at every natural stopping point, and before your session ends whenever you changed anything. Sessions end without warning (usage limits, closed laptops), so do not save it for the very end.

1. **On your work branch:** commit everything and push. `git status -sb` must show nothing to commit and nothing ahead.
2. **If the task is finished:** open a pull request into `main` titled `[T-007] <summary>`, with `gh pr create --base main` if the GitHub CLI works, or by giving your human the link `https://github.com/Jsanson1/BMEN600_Group5/compare/main...<branch>?expand=1` together with a title and description to paste. In the description: what changed, how you verified it, what is *not* verified, which script produces which output, and who should review it.
3. **Coordination update, on `main`:** `git switch main && git pull --rebase`, then:
   - `TASKS.md`: update your task's `status` and `updated` (the `branch` field keeps the branch name; the pull request link goes in your handoff).
   - `members/<short>/handoff.md`: rewrite your section for this task, using the format at the top of the file. A task's section is deleted only once it is `done` (merged); until then its *Next* says what is left (open the pull request, get the review, merge, mark done, delete the branch). Leave other sections alone; another of your human's sessions may own them. This file is current state, not history.
   - `members/<short>/log.md`: append one entry at the bottom, using the format at the top of the file. Be specific and honest about AI use and verification.
4. `git add TASKS.md members/<short>/ && git commit -m "[T-007] Handoff (anna)" -m "Co-Authored-By: Claude <noreply@anthropic.com>" && git push`. If rejected: `git pull --rebase`, then push.
5. `git switch -` to go back to your branch if the work continues; otherwise stay on `main`. Tell your human, in three lines: what got done, what is next, and anything a teammate needs to know.

**Merging pull requests** (`DECISIONS.md` D-003): a teammate looks at it first (their agent can do a first-pass review, their human approves), the checks must be green, then the author merges. A tiny docs or typo fix can be self-merged; say so in the pull request. After merging: set the task to `status: done`, delete its handoff section, and delete the branch.

## 8. Hard rules

1. **Never force-push, and never rewrite history that is on GitHub**: no `--force`, no rebasing pushed branches, no resetting `main`. A rejected push means pull, then push.
2. **Never delete, revert or overwrite someone else's work**, including uncommitted changes you did not make. If something looks wrong, tell your human.
3. **Never edit another member's `members/<them>/` files.** Leave them a note under *For teammates* in your own handoff (`@anna: ...`).
4. **Never work on a task owned by someone else** without their OK, relayed by your human.
5. **Never change or delete a `DECISIONS.md` entry.** The group decides, by majority (team contract); agents only record. A new entry can supersede an old one, and must say which.
6. **Do not edit the shared rules** (`CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, `.claude/`, `.githooks/`, `tools/`, `.github/`) unless your human asks, and then only on a branch with a pull request the others can see.
7. **This repo is public.** Never commit course handouts, rubrics or slides (they are the instructors' copyright), grades, peer evaluations, anything about disagreements inside the team, personal or health information, passwords, tokens or `.env` files.
8. **Nothing over 10 MB.** The hook blocks it.
9. **Never bypass the hook** (`--no-verify`) without your human's explicit OK, and say why in the commit message.

## 9. Research integrity

The course allows AI tools but forbids using them "to fabricate sources, results, or other contributions", and fabricated or misrepresented references put the literature criterion of the rubric at zero.

1. **Never add a reference you have not checked.** Confirm that the DOI or URL resolves to that exact paper, that authors, title, year and venue match, and that the paper actually supports the sentence citing it. If you cannot, mark it `[UNVERIFIED]` and tell your human. Citations use IEEE style.
2. **Every number, table and figure in a report comes from code in this repo.** Never type a result in by hand. Keep track of which script produces which output; the README has to say so.
3. **Separate what you checked from what you assume** in handoffs, logs and pull requests. "Not verified" is a fine thing to write. A confident sentence nobody can trace is not.
4. **Log AI use as you go**, in `log.md`: which tool, what it did, and how a human checked it (or that they have not yet).
5. **Do not bury negative or unexpected results.** Report them plainly.
6. **Respect the dataset's terms.** Record its licence and version wherever it is used.

## 10. When something goes wrong

- **Push rejected:** `git pull --rebase`, then push. Never `--force`.
- **Rebase conflict:** in `TASKS.md`, follow section 5. In your own files, combine both sides. In anyone else's file or in shared code, run `git rebase --abort` and ask your human. Never resolve a conflict by deleting the other side unless you are sure it is obsolete, and never commit conflict markers (the hook blocks them).
- **The hook says you are committing work files on `main`:** move to a branch, and your uncommitted changes come along: `git switch -c <short>/<task-id>-<slug>`, then commit there.
- **The hook says you are committing coordination files on a branch:** unstage them with `git reset -q -- TASKS.md members/`, commit the rest, then make the coordination edit on `main` (section 7, step 3).
- **You committed on `main` by mistake and have not pushed:** save the commit on a branch with `git branch <short>/<task-id>-<slug>`, then ask your human before moving `main` back.
- **A teammate's entry on the board or in their handoff looks stale or wrong:** do not edit it. Mention it under *For teammates* in your handoff and tell your human.
- **git says "Operation not permitted" or "could not lock config file" while you work on your human's computer through a folder link:** git uses temporary lock files, and your tool cannot delete them until your human allows deletion inside the repo folder. Ask for that permission (your tool has a request for it), then retry the same command. Never work around it by copying the repo somewhere else.

## 11. Where things are

- `README.md`: the project's front page (graded: research question, dataset access, file map, how to run).
- `CONTRIBUTING.md`: this process, written for the humans.
- `TASKS.md`, `DECISIONS.md`, `members/`: coordination (sections 2 and 3).
- `.claude/skills/start/` and `.claude/skills/handoff/`: the `/start` and `/handoff` commands; they point back to sections 4, 5 and 7 here.
- `.githooks/pre-commit` and `tools/repo_checks.sh`: the commit guardrails. `.github/workflows/checks.yml`: the same checks plus ruff, run by GitHub on every pull request and every push to `main`.
- `pyproject.toml`: ruff settings. `requirements-dev.txt`: the pinned ruff version.
- Project code and data folders: being set up under T-007.
