# Working together in this repo

This is the short version, for people. Your AI agent follows [CLAUDE.md](CLAUDE.md), which has every detail, so you don't need to memorise any of it.

## How it works

1. **[TASKS.md](TASKS.md) is the board.** Every piece of work is a task with an ID (T-007). Your agent claims a task before starting it, so nobody does the same work twice.
2. **Real work happens on your own branch** (for example `anna/T-007-stride-features`) and reaches `main` through a pull request that a teammate looks at first. Our team contract says we each keep to our own branches.
3. **`members/<you>/handoff.md` is where you left off**, one section per task you're on. Your agent rewrites it at every stopping point, so your next session, or a teammate, can pick up cold.
4. **`members/<you>/log.md` is your running record:** what you did, your CRediT roles, how AI was used and how it was checked. The paper's Author Contributions and AI-Assisted Work sections get written from these logs, and they make the Friday meeting log quick.
5. **[DECISIONS.md](DECISIONS.md)** holds what the group has decided, so no agent quietly changes course.
6. Those coordination files go straight onto `main`. Everything else goes through your branch. A pre-commit hook stops mistakes in either direction, and GitHub runs ruff on every pull request.

## One-time setup (about 5 minutes per computer)

The commands work in Git Bash or PowerShell on Windows and in Terminal on a Mac.

1. **Clone the repo** somewhere that is *not* synced by OneDrive, Dropbox or iCloud (sync tools and git fight over the same files):

   ```
   git clone https://github.com/Jsanson1/BMEN600_Group5.git
   cd BMEN600_Group5
   ```

   Already have a clone? `cd` into it and run `git switch main`, then `git pull`.

2. **Switch on the guardrails.** This setting lives in each clone, so every clone needs it once:

   ```
   git config core.hooksPath .githooks
   ```

3. **Make sure your commits carry your name**, using the email on your GitHub account:

   ```
   git config user.name "Your Name"
   git config user.email "you@example.com"
   ```

4. **Install ruff**, the formatter and linter we agreed on (use `python3` on a Mac if `python` isn't found):

   ```
   python -m pip install -r requirements-dev.txt
   ```

5. Optional: install the GitHub CLI (`gh`) and run `gh auth login`, so your agent can open pull requests for you.

Then mark your setup task (T-003 for Anna, T-004 for Yassien, T-005 for Jamie) as done. Your agent can do that for you.

## Every session

**Claude Code** (terminal, desktop app, or claude.ai/code): open the repo folder and type `/start`. To begin on a specific task, type `/start T-007`. When you stop, type `/handoff`.

**Claude with the repo attached, or any other AI agent:** paste this as your first message, with your name filled in:

```
I'm <your name> from BMEN 600 Group 5. Work in our repo
https://github.com/Jsanson1/BMEN600_Group5 and follow its CLAUDE.md exactly.
Do its start-of-session steps and report back before changing anything.
When we stop, do its handoff steps.
```

Then tell your agent what to work on, or pick from the list it gives you.

## Meetings

- **Before Friday's debrief:** ask your agent "Summarise my log.md entries since last Friday for the meeting log", and paste the result into the Google Doc.
- **After a meeting:** tell your agent what was agreed, for example "Add these tasks to the board: ..." or "Record this group decision in DECISIONS.md: ...". It puts them on `main` straight away, where everyone's agents will see them.

## Reviewing a teammate's pull request

Ask your agent: "Review pull request #12 against CLAUDE.md and its task, and run the code." Read its notes, look at the changes yourself, then approve or comment on GitHub. The reviewer is you, not the AI: the point is that you understand what went in, because everyone has to be able to explain the project in the final presentation.

## If something goes wrong

Ask your agent; CLAUDE.md section 10 covers the usual git problems. Two rules matter most: never force-push, and never delete or overwrite someone else's work. If in doubt, stop and ask in the WhatsApp group.

## Housekeeping

- The repo is public and it's graded. Don't commit course handouts, rubrics or slides, grades, peer feedback, personal information, passwords, or datasets.
- Files over 10 MB are blocked. Data goes in `data/raw/`, which git ignores.
- New team member? Copy `members/_template/` to `members/<first name>/`, fill in their name, add them to the table in CLAUDE.md section 1 (on a branch, by pull request), and invite them to the repo on GitHub.
