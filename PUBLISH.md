# Publishing GroundedOps to GitHub (Windows PowerShell)

These steps create a **public** `GroundedOps` repository on your GitHub account. Nothing is uploaded merely by opening this file or extracting the ZIP. Run them in PowerShell from the extracted `GroundedOps_LLM_RAG` directory.

## 1. Check quality and GitHub login

```powershell
python -m unittest discover -s tests -q
python -m groundedops evaluate
gh auth status
```

No API key is needed for these local checks. The unit test suite must say `OK`; the evaluation should show 8 cases on the included synthetic dataset. If `gh auth status` fails, use `gh auth login` first.

## 2. Create a commit and inspect the staged files

```powershell
git init -b main
git add .
git diff --cached --name-only
```

**Do not continue unless you recognize every staged file.** Check that no API keys, `.env` files, private customer documents, screenshots containing secrets, or personal data are included. New files in `/knowledge/` are ignored by default; the five bundled sample files are explicitly allowed. The repository is a public portfolio demo and should contain only synthetic/non-confidential sample data.

```powershell
git commit -m "Initial release: GroundedOps RAG with Gemini and evaluation"
```

If Git asks for identity, set it with `git config --global user.name "YOUR_GITHUB_NAME"` and `git config --global user.email "YOUR_GITHUB_EMAIL"`, then retry the commit.

## 3. Publish the project

```powershell
gh repo create chinmaygit-lab/GroundedOps --public --source=. --remote=origin --push --description "Evidence-first RAG app with Gemini, BM25 retrieval, citations, and evaluation"
```

GitHub CLI uploads the local committed files and prints the remote repository URL. This command works only if the repo name is available and your authenticated `gh` account can create repositories for `chinmaygit-lab`. If the repository already exists, do not overwrite it; inspect that repository and its remote before pushing.

Verify:

```powershell
gh repo view chinmaygit-lab/GroundedOps --web
```

Your README should load and `.github/workflows/ci.yml` should trigger automatic tests on push. The GitHub repository is **source code**, not a hosted version of the localhost web server. Review GitHub Actions results before citing the CI check as passed.

## Suggested application description

> GroundedOps — built a Python RAG application using BM25 document retrieval, evidence-linked prompts, Gemini API generation, a local browser UI and a reproducible 8-query synthetic retrieval evaluation. Implemented automated tests and GitHub Actions CI. Documented limits of citations and retrieval-only evaluation.

Do not claim that the project was deployed to a public server or achieved production-grade answer accuracy. Running it locally and publishing code is a valid public portfolio milestone, but completing an internship assignment depends on the employer's specific submission requirements.
