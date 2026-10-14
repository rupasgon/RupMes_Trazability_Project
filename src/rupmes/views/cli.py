import argparse

from rupmes.controllers.db_controller import init_db
from rupmes.core.db import get_engine
from rupmes.services.erp_delivery import ErpDeliveryWorker, run_forever
from sqlalchemy.orm import sessionmaker


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rupmes")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init-db", help="Create tables and seed defaults")
    delivery_once = subparsers.add_parser("deliver-erp-once", help="Create and deliver pending ERP production batches")
    delivery_once.add_argument("--interval", type=int, default=30, help=argparse.SUPPRESS)
    delivery = subparsers.add_parser("deliver-erp", help="Run the ERP delivery worker")
    delivery.add_argument("--interval", type=int, default=30, help="Seconds between delivery cycles")
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "init-db":
        init_db()
    elif args.command == "deliver-erp-once":
        session = sessionmaker(get_engine(), future=True)()
        try:
            print(f"ERP batches delivered: {ErpDeliveryWorker(session).run_once()}")
        finally:
            session.close()
    elif args.command == "deliver-erp":
        run_forever(sessionmaker(get_engine(), future=True), args.interval)
