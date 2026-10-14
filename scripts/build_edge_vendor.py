"""Create a portable dependency folder for the RupMES Edge Windows package."""

from __future__ import annotations

import argparse
import importlib.metadata as metadata
import json
import shutil
import sys
import sysconfig
from pathlib import Path

from packaging.requirements import Requirement


ROOT_REQUIREMENTS = ("fastapi", "uvicorn", "pydantic", "cryptography", "asyncua")


def normalized(name: str) -> str:
    return name.lower().replace("-", "_").replace(".", "_")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--destination", required=True, type=Path)
    arguments = parser.parse_args()

    site_packages = Path(sysconfig.get_paths()["purelib"]).resolve()
    distributions = {normalized(item.metadata["Name"]): item for item in metadata.distributions()}
    pending = list(ROOT_REQUIREMENTS)
    selected = {}

    while pending:
        name = pending.pop()
        key = normalized(name)
        if key in selected:
            continue
        distribution = distributions.get(key)
        if distribution is None:
            raise RuntimeError(f"Required installed distribution is missing: {name}")
        selected[key] = distribution
        for raw_requirement in distribution.requires or []:
            requirement = Requirement(raw_requirement)
            if requirement.marker and not requirement.marker.evaluate():
                continue
            pending.append(requirement.name)

    if arguments.destination.exists():
        shutil.rmtree(arguments.destination)
    arguments.destination.mkdir(parents=True)

    for distribution in selected.values():
        for file in distribution.files or []:
            source = distribution.locate_file(file).resolve()
            if not source.is_file():
                continue
            try:
                relative = source.relative_to(site_packages)
            except ValueError:
                continue
            target = arguments.destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

    (arguments.destination / "runtime.json").write_text(
        json.dumps({"python_major_minor": f"{sys.version_info.major}.{sys.version_info.minor}"}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Bundled {len(selected)} Python distributions for Python {sys.version_info.major}.{sys.version_info.minor}.")


if __name__ == "__main__":
    main()
