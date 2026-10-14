from __future__ import annotations

import argparse
import asyncio
import os


def main() -> None:
    parser = argparse.ArgumentParser(description="RupMES Edge local dashboard")
    subcommands = parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser("simulator", help="Run the local OPC UA simulator")
    dashboard = subcommands.add_parser("dashboard", help="Run the local dashboard")
    dashboard.add_argument("--config", help="Path to a validated edge JSON configuration")
    dashboard.add_argument("--host", help="Override the configuration bind host")
    dashboard.add_argument("--port", type=int, help="Override the configuration port")
    arguments = parser.parse_args()

    if arguments.command == "simulator":
        from rupmes_edge.simulator import run_simulator

        asyncio.run(run_simulator())
        return

    from rupmes_edge.app import create_app
    from rupmes_edge.config import default_config_path, demo_config, load_config
    import uvicorn

    configured_path = default_config_path()
    use_external_config = bool(arguments.config or os.getenv("RUPMES_EDGE_CONFIG") or configured_path.exists())
    config = load_config(arguments.config or configured_path) if use_external_config else demo_config()
    uvicorn.run(create_app(config), host=arguments.host or config.admin.bind_host, port=arguments.port or config.admin.port, reload=False)


if __name__ == "__main__":
    main()
