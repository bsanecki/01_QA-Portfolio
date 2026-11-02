# Git - Notes for a QA Tester (Basics)

## 1. Starting a Project

```bash
git init
```
Creates a new, empty Git repository in the current folder. Used when starting a project from scratch (e.g. your own testing portfolio).

```bash
git clone https://github.com/user/repo.git
```
Copies an existing repository from GitHub (or another server) to your computer, along with its full history. This is the most common starting operation — you're joining an existing project.

---

## 2. Checking Repository Status

```bash
git status
```
Shows what's currently going on: which files have been changed, which are staged and ready to be committed, and which are not yet tracked by Git. This is the **most frequently used** command — it's good practice to check `status` before every next step.

```bash
git log
```
Shows the commit history — who changed what, and when, along with each commit's message. Useful for reviewing what happened in the project earlier, e.g. when a given bug was introduced.

```bash
git diff
```
Shows exactly **what has changed** in the files compared to the last commit — line by line (what was added, what was removed). Very useful during code review or before committing your own changes.

---

## 3. Saving Changes

```bash
git add filename.txt
```
Adds a file to the so-called **staging area** — marking it as ready to be included in the next commit. You can also add everything at once:
```bash
git add .
```

```bash
git commit -m "Description of changes"
```
Saves all staged changes as a new point in the project's history, together with a description of what was done.

**Typical workflow:**
```bash
git add .
git commit -m "Add login test cases"
```

---

## 4. Working With a Remote Repository

```bash
git push
```
Sends your local commits to the server (e.g. GitHub), so others can see them too.

```bash
git pull
```
Fetches the latest changes from the server **and immediately merges** them into your local branch. It is effectively `git fetch` + `git merge`.

```bash
git fetch
```
Fetches the latest changes from the server but **does not merge** them automatically — you can review what has changed before deciding to bring it into your own code.

> **`pull` vs `fetch`:** `pull` = fetch and apply immediately. `fetch` = only fetch, and let you decide.

---

## 5. Working With Branches

```bash
git branch
```
Lists all branches in the repository and marks the one you're currently on.

```bash
git branch branch-name
```
Creates a new branch (without switching to it).

```bash
git switch branch-name
```
Switches you to the specified branch. You can also create and switch to a new branch in a single command:
```bash
git switch -c new-branch
```

```bash
git merge branch-name
```
Merges the specified branch into the one you're currently on — e.g. bringing your changes from `feature/login-tests` into `main`.

**Typical branch workflow:**
```bash
git switch -c feature/new-test-cases
# ... work on the changes ...
git add .
git commit -m "Add new test cases for checkout"
git switch main
git merge feature/new-test-cases
```

---

## 6. Undoing Changes

```bash
git restore filename.txt
```
Reverts unsaved (uncommitted) changes in a file back to the state from the last commit — essentially "undo what I just changed in this file."

```bash
git reset
```
Undoes changes added with `git add` (removing files from the staging area), but **does not remove** the actual changes in the files — they're still there, just no longer marked for commit.

> **Difference:** `restore` reverts changes to a file's content. `reset` undoes what was added via `git add`, without touching the file contents themselves.

---

## 7. Stash — Temporarily Setting Changes Aside

```bash
git stash
```
Temporarily "stashes away" your uncommitted changes, so you can, for example, switch to another branch without committing unfinished work.

```bash
git stash pop
```
Restores the most recently stashed changes back into your working directory.

**Typical scenario:** you're in the middle of working on something, but urgently need to switch to another branch to check something:
```bash
git stash
git switch main
# ... checking something on main ...
git switch feature/my-branch
git stash pop
```

---

## 8. Other Useful Commands

```bash
git remote -v
```
Shows which remote repository (e.g. GitHub) your local repository is connected to — useful for checking exactly where `git push` will actually send your changes.

```bash
git log --oneline
```
A condensed version of `git log` — one commit per line. Much more convenient for a quick overview of history than the full `git log`.

---

## 9. The .gitignore File

`.gitignore` is not a command — it's a file in the repository listing which files and folders Git should **not track** (e.g. temporary files, login credentials, folders such as `node_modules`). This is very commonly needed in practice, to avoid accidentally committing something that shouldn't be in the repository.

Example `.gitignore` contents:
```
node_modules/
.env
*.log
```

---

## 10. Commit Message Conventions

A commit message should be short, specific, and written in the imperative mood, describing what the commit does rather than what was done. For example:

```
Add test cases for password reset
Fix broken login test
Update README with setup instructions
```

Vague messages such as `"changes"` or `"fix"` should be avoided, as they provide no useful information about the actual content of the commit — either to teammates reviewing the history or to the author themselves at a later point in time.
