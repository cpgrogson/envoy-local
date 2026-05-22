"""Write rendered Envoy configs to disk or stdout."""

import os
import sys
from pathlib import Path
from typing import Optional

import yaml

from envoy_local.config import EnvoyConfig
from envoy_local.renderer import render


DEFAULT_OUTPUT_FILENAME = "envoy.yaml"


def write_config(
    config: EnvoyConfig,
    output_dir: Optional[str] = None,
    filename: str = DEFAULT_OUTPUT_FILENAME,
    stdout: bool = False,
) -> Optional[Path]:
    """Render an EnvoyConfig and write it to a file or stdout.

    Args:
        config: The EnvoyConfig to render.
        output_dir: Directory where the config file will be written.
                    Defaults to the current working directory.
        filename: Name of the output file. Defaults to 'envoy.yaml'.
        stdout: If True, write to stdout instead of a file.

    Returns:
        The Path of the written file, or None if written to stdout.
    """
    rendered = render(config)

    if stdout:
        sys.stdout.write(rendered)
        sys.stdout.flush()
        return None

    base_dir = Path(output_dir) if output_dir else Path.cwd()
    base_dir.mkdir(parents=True, exist_ok=True)

    output_path = base_dir / filename
    output_path.write_text(rendered, encoding="utf-8")
    return output_path


def load_config_from_file(path: str) -> dict:
    """Load a raw YAML config from disk and return it as a dict.

    Args:
        path: Path to the YAML file.

    Returns:
        Parsed YAML content as a dictionary.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file cannot be parsed as valid YAML.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with file_path.open("r", encoding="utf-8") as fh:
        try:
            data = yaml.safe_load(fh)
        except yaml.YAMLError as exc:
            raise ValueError(f"Invalid YAML in {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError(f"Expected a YAML mapping at the top level, got: {type(data)}")

    return data
