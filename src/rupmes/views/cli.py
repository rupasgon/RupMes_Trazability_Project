import argparse

from rupmes.controllers.db_controller import init_db


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rupmes")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init-db", help="Create tables and seed defaults")
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "init-db":
        init_db()
