# GroundedOps — RAG & LLM Evaluation Lab

**Portfolio-ready, offline-first retrieval-augmented generation demo for operations knowledge.** Built to demonstrate Python engineering, local document indexing, BM25 retrieval, source evidence, model integration and reproducible evaluation.

GroundedOps is not a newly trained foundation model. It is an LLM-powered application. It **does not claim** human-level accuracy or universal protection against prompt injection.

## Features

- Index local `.md`, `.txt`, `.csv`, `.json` documents with deterministic chunking and BM25 retrieval.
- **Retrieval-only mode** works with **zero API keys**. This mode shows evidence but **does not generate LLM answers**.
- Optional real LLM generation through **local Ollama** (no cloud API key) or **Gemini API** (requires a separate developer API key).
- Browser interface at localhost with question-answering, source snippets, scores, and retrieval evaluation.
- 8-question synthetic ground-truth benchmark; calculates retrieval recall@4. It **does not** measure hallucination rates or prove citation faithfulness.
- Strict 600-character question limit, local-only server, no write tools, hidden files ignored, payload-size limit, simple same-origin check.
- Pure Python standard library, no web dependencies. Optional local model uses Ollama.

## Quickstart — Windows PowerShell

For the web interface, start this command in the same terminal where your Gemini key is configured if using Gemini. If the page shows `Loading` permanently, hard-refresh with Ctrl+F5 after restarting the server.


Inside the extracted `GroundedOps_LLM_RAG` folder:

```powershell
python -m groundedops evaluate
python -m groundedops ask "Who approves agent task completion?"
python -m groundedops serve
```

Open **http://127.0.0.1:8090**. This default mode retrieves evidence without invoking an LLM. Python **3.10+** required. The tests need no API keys.

## Optional local LLM using Ollama

Install [Ollama](https://ollama.com/download), then in a terminal:

```powershell
ollama pull llama3.2:3b
```

Then from the project folder:

```powershell
python -m groundedops serve --provider ollama
```

Ollama must be running locally on `127.0.0.1:11434`. The demo sends only the retrieved passages and question to your **local** Ollama service. Model download requires storage and network; generation depends on RAM/CPU/GPU. You may choose another installed model with `$env:OLLAMA_MODEL="your-model"`.

## Gemini cloud generation (tested with the real API)

Get a **Gemini API key**, not a project number, at [Google AI Studio](https://aistudio.google.com/api-keys). The app reads the key from the `GEMINI_API_KEY` environment variable; it never needs a key inside a source file. The key is only available in the current terminal unless you configure it otherwise.

From PowerShell, in this project's folder:

```powershell
$Secret = Read-Host "Paste your Gemini API key" -AsSecureString
$Ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($Secret)
try {
    $env:GEMINI_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($Ptr).Trim()
} finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($Ptr)
}
if ($env:GEMINI_API_KEY.Length -lt 20 -or $env:GEMINI_API_KEY -match '\s') {
    throw "Paste the complete API key, not a project ID or script"
}
$env:GEMINI_MODEL = "gemini-3.5-flash-lite"
python -m groundedops serve --provider gemini
```

Open **http://127.0.0.1:8090** and ask `Who approves agent task completion?`. The default Gemini model is `gemini-3.5-flash-lite` in v0.1.2; use `$env:GEMINI_MODEL="another-supported-model-id"` if your account needs a different model. A model 404 indicates that the selected model ID may not be available to that API project. The exact available models and billing/quota are controlled by Google.

**Privacy:** In Gemini mode, the question and retrieved document passages are transmitted to Google's API. Use only documents you are authorized to send; do not submit confidential data. Never commit API keys, secrets, local `.env` files, terminal captures containing keys, or private documents.

## Add your own knowledge

Copy small files into `knowledge/` or specify another directory:

```powershell
python -m groundedops serve --docs "C:\path\to\your\nonconfidential\docs"
```

A non-sensitive CSV task export can be placed here. Each row is flattened into searchable text. Restart the service after adding files. The index lives in memory; **nothing is uploaded by retrieval-only mode**.

Limits: individual files up to 300 KB, CSV max 1000 records, knowledge collections are intended to be small. Retrieval uses keyword ranking rather than semantic embeddings. It does not provide multi-tenant authentication or production-scale indexing.

## Architecture

`local docs → safe loader → overlapping chunks → BM25 retriever → top passages → grounding prompt → Ollama/Gemini → answer + evidence`.

All sources displayed in the UI come from retrieval, not invented by the model. **A retrieved source is not proof that every generated assertion is supported.** The prompt instructs the model to abstain on missing evidence, but no enforcement of factual correctness is claimed.

## Evaluation & quality

```powershell
python -m unittest discover -s tests -v
python -m groundedops evaluate
```

`examples/evaluation.json` contains eight synthetic query/source labels. Report the measured `retrieval_recall_at_4` with its dataset size; **do not interpret this as model answer accuracy**. Replace synthetic examples with held-out real evaluation cases to assess meaningful retrieval quality.

## What's deliberately out of scope

Production authentication, semantic vector embeddings, PDF OCR, streaming tokens, reliable agent tool execution, permission escalation, hallucination evaluation, prompt-injection guarantees, secrets vault and deployment hardening. They are future work, not implemented features.

## Internship relevance

Demonstrates LLM/RAG prototyping, Python APIs, data-processing basics, retrieval evaluation, prompt constraints, user-facing integration and honest reporting. This project is independent of other portfolio repositories.

The included policies and tasks are **synthetic**; no company data is present. This is an independent engineering demo, not affiliated with employers in any internship listing.

## GitHub publishing

See [PUBLISH.md](PUBLISH.md) for tested GitHub CLI commands and the privacy checklist. The `knowledge/` directory tracks only the bundled synthetic examples by default; new local documents are ignored.

## License

MIT — see LICENSE.
