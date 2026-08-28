from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from app.config import ConfigurationError, load_config
from app.input import CaseInputError, load_case
from app.models import OutputMode
from app.orchestration.runner import run_critique
from app.providers import MockProvider, OpenAIProvider, ProviderError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m app", description="Educational psychology debate lab")
    subparsers = parser.add_subparsers(dest="command", required=True)
    criticize = subparsers.add_parser("criticize", help="Analyze and debate a case")
    criticize.add_argument("--case", required=True, help="Filename inside input/")
    criticize.add_argument("--mode", choices=[mode.value for mode in OutputMode])
    criticize.add_argument("--rounds", type=int)
    criticize.add_argument("--provider", choices=["openai", "mock"], help="Override configured provider")
    criticize.add_argument("--root", type=Path, default=Path("."), help=argparse.SUPPRESS)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    try:
        config = load_config(root / "config/settings.yaml", root / "config/agents.yaml")
        case = load_case(args.case, root / "input")
        if args.rounds is not None and args.rounds < 1:
            raise ConfigurationError("--rounds must be at least 1")
        provider_name = args.provider or config.llm.provider
        provider = (
            MockProvider()
            if provider_name == "mock"
            else OpenAIProvider(
                config.llm.model,
                config.llm.temperature,
                config.llm.max_output_tokens,
            )
        )
        result = asyncio.run(
            run_critique(
                case=case,
                config=config,
                provider=provider,
                mode=OutputMode(args.mode) if args.mode else None,
                rounds=args.rounds,
                root=root,
            )
        )
    except (ConfigurationError, CaseInputError, ProviderError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    print(f"Run completed: {result.state.run_id}")
    for path in (
        result.outputs.analyse,
        result.outputs.consulting,
        result.outputs.markdown_log,
        result.outputs.json_trace,
    ):
        if path:
            print(path)
    return 0
