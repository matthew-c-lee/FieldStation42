from pathlib import Path
from typing import Any, Dict
from pydantic import BaseModel
import yaml

class _ConfigModel(BaseModel):
    config_dir: Path = Path("confs")         # default value
    runtime_dir: Path = Path("runtime")

    @property
    def channel_socket_path(self) -> Path:
        return self.runtime_dir / "channel.socket"

    @property
    def status_socket_path(self) -> Path:
        return self.runtime_dir / "play_status.socket"

# the singleton instance every module will import
APP_CONFIG = _ConfigModel()

def _deep_merge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(a.get(k), dict):
            _deep_merge(a[k], v)
        else:
            a[k] = v
    return a

def load_from_yaml(path: Path, *, overrides: Dict[str, Any] | None = None) -> None:
    """
    Re‑read the YAML file (and optional overrides) into the same object.
    Every module already holding APP_CONFIG will see the new values.
    """
    with open(path, "r") as f:
        data = yaml.safe_load(f)

    if overrides:
        data = _deep_merge(data, overrides)

    for key, value in data.items():
        setattr(APP_CONFIG, key, value)

def update_config(**patch: Any) -> None:
    """
    Mutate existing fields in place.  Example:

        update_config(config_dir=Path("integration_test/confs"))
    """
    for key, value in patch.items():
        setattr(APP_CONFIG, key, value)
