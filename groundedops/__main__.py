"""CLI: python -m groundedops [serve|ask|evaluate]."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .engine import GroundedEngine
from .server import serve

PACKAGE_DIR = Path(__file__).resolve().parent
DEFAULT_DOCS = Path.cwd() / "knowledge" if (Path.cwd() / "knowledge").is_dir() else PACKAGE_DIR / "sample_knowledge"
DEFAULT_EVAL = Path.cwd() / "examples" / "evaluation.json" if (Path.cwd() / "examples" / "evaluation.json").exists() else PACKAGE_DIR / "sample_evaluation.json"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="GroundedOps — cite evidence from local operations documents")
    parser.add_argument("command", choices=["serve", "ask", "evaluate"])
    parser.add_argument("question", nargs="?")
    parser.add_argument("--docs", type=Path, default=DEFAULT_DOCS)
    parser.add_argument("--provider", choices=["retrieval", "ollama", "gemini"], default="retrieval")
    parser.add_argument("--port", type=int, default=8090)
    parser.add_argument("--eval-file", type=Path, default=DEFAULT_EVAL)
    args = parser.parse_args(argv)
    engine = GroundedEngine(args.docs, provider=args.provider)
    if args.command == "ask":
        if not args.question:
            parser.error("ask requires a question")
        print(json.dumps(engine.ask(args.question), indent=2))
    else:
        cases = json.loads(args.eval_file.read_text(encoding="utf-8"))
        if args.command == "evaluate":
            print(json.dumps(engine.evaluate(cases), indent=2))
        else:
            serve(engine, args.port, cases)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
