"""Command-line interface for the cryptogram solver."""

from __future__ import annotations

import argparse

from ..service import solve_cryptogram, solve_file


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Solve simple substitution cryptograms"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    inline = subparsers.add_parser("text", help="Solve a ciphertext provided via CLI")
    inline.add_argument(
        "ciphertext", help="Ciphertext to solve; use quotes for multi-word input"
    )
    inline.add_argument("--clue", help="Optional hint or author clue", default=None)

    file_cmd = subparsers.add_parser("file", help="Solve a ciphertext stored in a file")
    file_cmd.add_argument(
        "path", help="Path to a UTF-8 text file containing the ciphertext"
    )
    file_cmd.add_argument("--clue", help="Optional hint or author clue", default=None)

    return parser


def _run_text(ciphertext: str, clue: str | None) -> None:
    solution = solve_cryptogram(ciphertext, clue=clue)
    print(solution.format_summary())


def _run_file(path: str, clue: str | None) -> None:
    solution = solve_file(path, clue=clue)
    print(solution.format_summary())


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "text":
        _run_text(args.ciphertext, args.clue)
    else:
        _run_file(args.path, args.clue)


if __name__ == "__main__":  # pragma: no cover
    main()
