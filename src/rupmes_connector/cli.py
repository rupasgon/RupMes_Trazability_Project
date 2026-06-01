from __future__ import annotations

import argparse
import logging

from rupmes_connector.config import load_configs
from rupmes_connector.service import MultiPipelineRunner, ProductionBridgeService


def _configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="RupMes production gateway")
    parser.add_argument("command", choices=["run", "run-once", "validate-config"])
    parser.add_argument("--config", required=True, help="Path to one config JSON or a directory of configs")
    args = parser.parse_args(argv)

    configs = load_configs(args.config)
    _configure_logging(configs[0].runtime.log_level)

    if args.command == "validate-config":
        print(f"Configuration is valid. Pipelines: {len(configs)}")
        return 0

    if len(configs) == 1:
        service = ProductionBridgeService(configs[0])
        if args.command == "run-once":
            processed = service.run_once()
            print(f"Rows transferred: {processed}")
            return 0
        service.run_forever()
        return 0

    runner = MultiPipelineRunner(configs)
    if args.command == "run-once":
        processed = runner.run_once()
        print(f"Rows transferred: {processed}")
        return 0

    runner.run_forever()
    return 0
