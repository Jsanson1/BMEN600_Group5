# Working together in this repo

This is the short version, for people. Your AI assistant follows [CLAUDE.md](CLAUDE.md), which has every detail, so you don't need to memorise any of it.

## How it works

1. **The writing happens in the shared Google Doc** ("BMEN 600 Group 5 – Midterm Research Plan (draft)", shared by Jamie). The repo is for code, results, figures and the list of checked references.
2. **[TASKS.md](TASKS.md) is the board.** Every piece of work is a task with an ID (T-007). Your assistant claims a task before starting it, so nobody does the same work twice.
3. **Code goes on your own branch** (for example `anna/T-007-stride-features`) and reaches `main` through a pull request that a teammate looks at first. Our team contract says we each keep to our own branches. Don't worry if those words are new: GitHub Desktop has a button for each step, and your assistant knows the routine.
4. **`members/<you>/handoff.md` is where you left off**, one section per task you're on. Your assistant rewrites it at every stopping point, so your next session, or a teammate, can pick up cold.
5. **`members/<you>/log.md` is your running record:** what you did, your CRediT roles, how AI was used and how it was checked. The report's Author Contributions and AI-Assisted Work sections get written from these, and they make the Friday meeting log quick.
6. **[DECISIONS.md](DECISIONS.md)** holds what the group has decided, so no assistant quietly changes course.
7. Those coordination files go straight onto `main`. Everything else goes through your branch. GitHub runs checks on every pull request, and an optional pre-commit hook runs the same checks on your computer.

## One-time setup (about 10 minutes)

Pick A or B. A needs no typing in a terminal.

**A. GitHub Desktop (recommended if you don't use a terminal)**

1. Install [GitHub Desktop](https://desktop.github.com/) and sign in with your GitHub account (the one that has access to this repo).
2. Click **File → Clone repository**, pick **Jsanson1/BMEN600_Group5**, and choose a folder that is **not** inside OneDrive, Dropbox or iCloud (for example `C:\Users\<you>\Documents\BMEN600_Group5` or `~/Documents/BMEN600_Group5`). Sync tools and git fight over the same files.
3. Open the Claude desktop app, click **+** → **Add folder**, and choose that folder.
4. Paste the message under "Every session" below. Your assistant checks the setup, sets your name on the commits, and, if it can, switches on the pre-commit hook. If it says it can't switch the hook on, that's fine; GitHub runs the same checks.

**B. Terminal**

```
git clone https://github.com/Jsanson1/BMEN600_Group5.git
cd BMEN600_Group5
git config core.hooksPath .githooks
git config user.name "Your Name"
git config user.email "you@example.com"
python -m pip install -r requirements-dev.txt
```

(`python3` on a Mac. The last line installs ruff, our code formatter.)

Then mark your setup task (T-003 for Anna, T-004 for Yassien) as done; your assistant does that for you on its first run.

## Every session

**Claude desktop app with the folder added:** paste this as your first message, with your name filled in:

```
I'm <your name> from BMEN 600 Group 5. This folder is our project repo.
Read CLAUDE.md in it and follow it exactly: do its start-of-session steps
and tell me where things stand before you change anything. When I say
we're done, do its handoff steps.
```

Then say what you want to work on, or pick from the list it gives you. When you stop, say "we're done for today" and it will save its handoff so the next session (yours or a teammate's) can carry on.

**Claude Code** (if you use it): open the repo folder and type `/start`, or `/start T-007` to begin on a task; type `/handoff` when you stop.

## Meetings

- **Before Friday's debrief:** ask your assistant "Summarise my log.md entries since last Friday for the meeting log", and paste the result into the meeting log.
- **After a meeting:** tell your assistant what was agreed, for example "Add these tasks to the board: ..." or "Record this group decision in DECISIONS.md: ...". It puts them on `main` straight away, where everyone's assistants will see them.

## Looking at a teammate's pull request

On github.com, open the repo, click **Pull requests**, open the one with your name in it, and read the **Files changed** tab. Ask your assistant "Review pull request #12 against CLAUDE.md and its task, and run the code" if you want a second pair of eyes. Then click **Review changes → Approve** (or leave a comment). The reviewer is you, not the AI: the point is that you understand what went in, because everyone has to be able to explain the project in the final presentation.

## If something goes wrong

Ask your assistant; CLAUDE.md section 10 covers the usual git problems. Two rules matter most: never force-push, and never delete or overwrite someone else's work. If in doubt, stop and ask in the WhatsApp group.

## Housekeeping

- The repo is public and it's graded. Don't commit course handouts, rubrics or slides, grades, peer feedback, personal information, passwords, or datasets.
- Files over 10 MB are blocked. Data goes in `data/raw/`, which git ignores.
- New team member? Copy `members/_template/` to `members/<first name>/`, fill in their name, add them to the table in CLAUDE.md section 1 (on a branch, by pull request), and invite them to the repo on GitHub.
