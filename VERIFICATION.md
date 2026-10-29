# GroundedOps v0.1.2 — Verification and limitations

## Automated checks (local, Python 3.13)

- Unit/API tests: see `python -m unittest discover -s tests -q` output for current total.
- Retrieval evaluation: 8 hand-written synthetic cases, all expected source labels retrieved in the top four passages. This measures **source retrieval recall@4 on this example dataset**, not answer accuracy.
- The local UI serves its JavaScript separately and uses a restrictive Content-Security-Policy.
- Gemini/Ollama integration unit tests mock the external HTTP call; they do not invoke a live API.

## Observed by project user (October 2026)

- Gemini generated a cited response through the app using the `gemini-3.5-flash-lite` model and a valid Gemini API key.
- Browser display showed provider `gemini`, seven indexed passages, model-generated incident-response text, and retrieved evidence links.

## Limits

The example knowledge files are synthetic. The app is a local demo, not a publicly hosted or multi-user production service. Citations identify retrieved passages, not verified factual correctness. Cloud mode sends selected excerpts to Google's Gemini endpoint. Do not add confidential source data or API secrets to a public repository.
