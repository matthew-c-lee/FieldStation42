from integration_test.test_utils import generate_catalog
from fs42.config.config import update_config
from pathlib import Path

import field_player
import station_42

update_config(
    config_dir=Path("integration_test/confs"),
    runtime_dir=Path("integration_test/runtime")
)

def test_field_player():
    generate_catalog()

    station_42.start_catalog(graphical_interface=False, rebuild_catalog=True, add_week=True)


if __name__ == "__main__":
    test_field_player()
    field_player.main_loop(transition_fn=field_player.short_change_effect)