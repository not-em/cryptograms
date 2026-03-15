"""Command-line interface for the cryptogram solver."""

from __future__ import annotations

import argparse
from pathlib import Path

from ..service import encrypt_cryptogram, solve_cryptogram


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Solve simple substitution cryptograms"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    decrypt_cmd = subparsers.add_parser(
        "decrypt", help="Solve a ciphertext (string or file path)"
    )
    decrypt_cmd.add_argument(
        "input", help="Ciphertext to solve, or path to a UTF-8 file containing it"
    )
    decrypt_cmd.add_argument(
        "--clue", help="Optional hint or author clue", default=None
    )

    encrypt_cmd = subparsers.add_parser(
        "encrypt", help="Encrypt plaintext with a random substitution cipher"
    )
    encrypt_cmd.add_argument(
        "plaintext", help="Plaintext to encrypt; use quotes for multi-word input"
    )
    encrypt_cmd.add_argument(
        "--seed", type=int, default=None, help="Integer seed for reproducible output"
    )

    return parser


def _run_decrypt(input: str, clue: str | None) -> None:
    p = Path(input)
    ciphertext = p.read_text(encoding="utf-8-sig") if p.is_file() else input
    solution = solve_cryptogram(ciphertext, clue=clue)
    print(solution.format_summary())


def _run_encrypt(plaintext: str, seed: int | None) -> None:
    ciphertext = encrypt_cryptogram(plaintext, seed=seed)
    print(ciphertext)


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "decrypt":
        _run_decrypt(args.input, args.clue)
    else:
        _run_encrypt(args.plaintext, args.seed)


if __name__ == "__main__":  # pragma: no cover
    main()
