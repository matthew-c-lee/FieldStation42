from integration_test.test_utils import generate_catalog
from fs42.config.config import update_config
from pathlib import Path
import pytest
import pickle
from pprint import pprint
from fs42.schedule_hint import DayPartHint
from fs42.series import SeriesIndex, SequenceEntry
from fs42.catalog_entry import CatalogEntry
from fs42.liquid_blocks import LiquidBlock, ReelBlock
from datetime import datetime
from fs42.block_plan import BlockPlanEntry
from freezegun import freeze_time

import field_player
import station_42
import random


@pytest.fixture
def catalog_setup():
    # Setup
    update_config(config_dir=Path("integration_test/confs"), runtime_dir=Path("integration_test/runtime"))
    random.seed(1) # Make randomness deterministic

    yield

    # Teardown...
    station_42.start_catalog(graphical_interface=False, delete_schedules=True)

@freeze_time(time_to_freeze=datetime(2025, 6, 1, 12, 0, 0))
def test_field_player(catalog_setup):
    catalog = {
        "catalog": {
            "channel_1": {
                "prime": {
                    "show_1": {
                        "season_1": {"Rick and Morty S01E01.mp4": {"duration": 1200, "color": "blue"}, "Rick and Morty S01E02.mp4": {"duration": 1250, "color": "blue"}},
                        "season_2": {"Rick and Morty S02E01.mp4": {"duration": 1200, "color": "blue"}},
                    },
                    "spongebob": {"Spongebob S01E01.mp4": {"duration": 1200, "color": "blue"}, "Spongebob S01E02.mp4": {"duration": 1200, "color": "blue"}},
                },
                "Avatar": {
                    "prime": {
                        "Avatar S01E01.mp4": {"duration": 1200, "color": "red"},
                        "Avatar S01E02.mp4": {"duration": 1200, "color": "red"},
                        "Avatar S01E03.mp4": {"duration": 1200, "color": "red"},
                        "Avatar S01E04.mp4": {"duration": 1200, "color": "red"},
                    }
                },
                "commercials": {
                    "commercial_1.mp4": {"duration": 30, "color": "green"},
                    "commercial_2.mp4": {"duration": 15, "color": "green"},
                    "commercial_3.mp4": {"duration": 60, "color": "green"},
                    "commercial_4.mp4": {"duration": 45, "color": "green"},
                    "commercial_5.mp4": {"duration": 22, "color": "green"},
                    "commercial_6.mp4": {"duration": 16, "color": "green"},
                    "commercial_7.mp4": {"duration": 20, "color": "green"},
                    "commercial_8.mp4": {"duration": 10, "color": "green"},
                },
                "bumps": {
                    "bump_1.mp4": {"duration": 5, "color": "purple"},
                    "bump_2.mp4": {"duration": 10, "color": "purple"},
                    "bump_3.mp4": {"duration": 4, "color": "purple"},
                    "bump_4.mp4": {"duration": 6, "color": "purple"},
                    "bump_5.mp4": {"duration": 8, "color": "purple"},
                    "bump_6.mp4": {"duration": 5, "color": "purple"},
                    "bump_7.mp4": {"duration": 15, "color": "purple"},
                },
            }
        }
    }
    output_dir = Path("integration_test/catalog")
    generate_catalog(catalog=catalog, output_dir=output_dir)

    # station_42.start_catalog(delete_schedules=True)

    # This will result in a binary file "channel_1_schedule.bin"
    station_42.start_catalog(graphical_interface=False, rebuild_catalog=True)

    channel_binary_path: Path = output_dir / "channel_1.bin"
    channel_schedule_binary_path: Path = Path("integration_test/runtime") / "channel_1_schedule.bin"

    with open(channel_binary_path, "rb") as file:
        channel_data = pickle.load(file)

    expected_channel_data = {
        "clip_index": {
            "Avatar": [
                CatalogEntry(path=Path("integration_test/catalog/channel_1/Avatar/prime/Avatar S01E02.mp4"), duration=1202.0, tag="Avatar", hints=[DayPartHint(part_name="prime")]),
                CatalogEntry(path=Path("integration_test/catalog/channel_1/Avatar/prime/Avatar S01E04.mp4"), duration=1202.0, tag="Avatar", hints=[DayPartHint(part_name="prime")]),
                CatalogEntry(path=Path("integration_test/catalog/channel_1/Avatar/prime/Avatar S01E03.mp4"), duration=1202.0, tag="Avatar", hints=[DayPartHint(part_name="prime")]),
                CatalogEntry(path=Path("integration_test/catalog/channel_1/Avatar/prime/Avatar S01E01.mp4"), duration=1202.0, tag="Avatar", hints=[DayPartHint(part_name="prime")]),
            ],
            "Avatar-postbump": [],
            "Avatar-prebump": [],
            "bumps": [
                CatalogEntry(path=Path("integration_test/catalog/channel_1/bumps/bump_1.mp4"), duration=7.0, tag="bumps", hints=[]),
                CatalogEntry(path=Path("integration_test/catalog/channel_1/bumps/bump_7.mp4"), duration=17.0, tag="bumps", hints=[]),
                CatalogEntry(path=Path("integration_test/catalog/channel_1/bumps/bump_4.mp4"), duration=8.0, tag="bumps", hints=[]),
                CatalogEntry(path=Path("integration_test/catalog/channel_1/bumps/bump_5.mp4"), duration=10.0, tag="bumps", hints=[]),
                CatalogEntry(path=Path("integration_test/catalog/channel_1/bumps/bump_6.mp4"), duration=7.0, tag="bumps", hints=[]),
                CatalogEntry(path=Path("integration_test/catalog/channel_1/bumps/bump_2.mp4"), duration=12.0, tag="bumps", hints=[]),
                CatalogEntry(path=Path("integration_test/catalog/channel_1/bumps/bump_3.mp4"), duration=6.0, tag="bumps", hints=[]),
            ],
            "bumps-postbump": [],
            "bumps-prebump": [],
            "commercials": [
                CatalogEntry(path=Path("integration_test/catalog/channel_1/commercials/commercial_4.mp4"), duration=47.0, tag="commercials", hints=[]),
                CatalogEntry(path=Path("integration_test/catalog/channel_1/commercials/commercial_8.mp4"), duration=12.0, tag="commercials", hints=[]),
                CatalogEntry(path=Path("integration_test/catalog/channel_1/commercials/commercial_5.mp4"), duration=24.0, tag="commercials", hints=[]),
                CatalogEntry(path=Path("integration_test/catalog/channel_1/commercials/commercial_3.mp4"), duration=62.0, tag="commercials", hints=[]),
                CatalogEntry(path=Path("integration_test/catalog/channel_1/commercials/commercial_2.mp4"), duration=17.0, tag="commercials", hints=[]),
                CatalogEntry(path=Path("integration_test/catalog/channel_1/commercials/commercial_7.mp4"), duration=22.0, tag="commercials", hints=[]),
                CatalogEntry(path=Path("integration_test/catalog/channel_1/commercials/commercial_1.mp4"), duration=32.0, tag="commercials", hints=[]),
                CatalogEntry(path=Path("integration_test/catalog/channel_1/commercials/commercial_6.mp4"), duration=18.0, tag="commercials", hints=[]),
            ],
            "commercials-postbump": [],
            "commercials-prebump": [],
            "end_bumps": {},
            "off_air": CatalogEntry(path=Path("integration_test/runtime/off_air_pattern.mp4"), duration=182.23, tag="off_air", hints=[]),
            "prime": [
                CatalogEntry(path=Path("integration_test/catalog/channel_1/prime/spongebob/Spongebob S01E01.mp4"), duration=1202.0, tag="prime", hints=[]),
                CatalogEntry(path=Path("integration_test/catalog/channel_1/prime/spongebob/Spongebob S01E02.mp4"), duration=1202.0, tag="prime", hints=[]),
                CatalogEntry(path=Path("integration_test/catalog/channel_1/prime/show_1/season_2/Rick and Morty S02E01.mp4"), duration=1202.0, tag="prime", hints=[]),
                CatalogEntry(path=Path("integration_test/catalog/channel_1/prime/show_1/season_1/Rick and Morty S01E01.mp4"), duration=1202.0, tag="prime", hints=[]),
                CatalogEntry(path=Path("integration_test/catalog/channel_1/prime/show_1/season_1/Rick and Morty S01E02.mp4"), duration=1252.0, tag="prime", hints=[]),
            ],
            "prime-postbump": [],
            "prime-prebump": [],
            "sign_off": CatalogEntry(path=Path("integration_test/runtime/signoff.mp4"), duration=79.17, tag="sign_off", hints=[]),
            "start_bumps": {},
        },
        "sequences": {
            "Avatar-prime": SeriesIndex(
                tag_path="Avatar",
                start_point=0,
                end_point=1,
                _episodes=[
                    SequenceEntry(fpath=Path("integration_test/catalog/channel_1/Avatar/prime/Avatar S01E01.mp4"), next_scheduled=[], last_played=None),
                    SequenceEntry(fpath=Path("integration_test/catalog/channel_1/Avatar/prime/Avatar S01E02.mp4"), next_scheduled=[], last_played=None),
                    SequenceEntry(fpath=Path("integration_test/catalog/channel_1/Avatar/prime/Avatar S01E03.mp4"), next_scheduled=[], last_played=None),
                    SequenceEntry(fpath=Path("integration_test/catalog/channel_1/Avatar/prime/Avatar S01E04.mp4"), next_scheduled=[], last_played=None),
                ],
            )
        },
        "version": 0.1,
    }
    
    assert channel_data == expected_channel_data

    # Test catalog!
    station_42.start_catalog(graphical_interface=False, add_hour=True)

    with open(channel_schedule_binary_path, "rb") as file:
        channel_schedule_data = pickle.load(file)

    expected_channel_schedule_data = [
        LiquidBlock(content=CatalogEntry(path=Path('integration_test/catalog/channel_1/Avatar/prime/Avatar S01E01.mp4'), duration=1202.0, tag='Avatar', hints=[DayPartHint(part_name='prime')], count=0), start_time=datetime(2025, 6, 1, 0, 0), end_time=datetime(2025, 6, 1, 0, 30), title='Avatar S01E01', break_strategy='standard', bump_info={'start': None, 'end': None, 'dir': None}, reel_blocks=[ReelBlock(start_bump=CatalogEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_7.mp4'), duration=17.0, tag='bumps', hints=[], count=3), comms=[CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_7.mp4'), duration=22.0, tag='commercials', hints=[], count=6), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_2.mp4'), duration=17.0, tag='commercials', hints=[], count=6), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_1.mp4'), duration=32.0, tag='commercials', hints=[], count=5), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_3.mp4'), duration=62.0, tag='commercials', hints=[], count=5)], end_bump=CatalogEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_4.mp4'), duration=8.0, tag='bumps', hints=[], count=3)), ReelBlock(start_bump=CatalogEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_2.mp4'), duration=12.0, tag='bumps', hints=[], count=4), comms=[CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_8.mp4'), duration=12.0, tag='commercials', hints=[], count=6), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_6.mp4'), duration=18.0, tag='commercials', hints=[], count=5), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_5.mp4'), duration=24.0, tag='commercials', hints=[], count=5), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_4.mp4'), duration=47.0, tag='commercials', hints=[], count=5)], end_bump=CatalogEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_5.mp4'), duration=10.0, tag='bumps', hints=[], count=3)), ReelBlock(start_bump=CatalogEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_6.mp4'), duration=7.0, tag='bumps', hints=[], count=3), comms=[CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_1.mp4'), duration=32.0, tag='commercials', hints=[], count=5), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_7.mp4'), duration=22.0, tag='commercials', hints=[], count=6), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_5.mp4'), duration=24.0, tag='commercials', hints=[], count=5), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_3.mp4'), duration=62.0, tag='commercials', hints=[], count=5)], end_bump=CatalogEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_1.mp4'), duration=7.0, tag='bumps', hints=[], count=3)), ReelBlock(start_bump=CatalogEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_3.mp4'), duration=6.0, tag='bumps', hints=[], count=3), comms=[CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_6.mp4'), duration=18.0, tag='commercials', hints=[], count=5), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_8.mp4'), duration=12.0, tag='commercials', hints=[], count=6), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_4.mp4'), duration=47.0, tag='commercials', hints=[], count=5), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_2.mp4'), duration=17.0, tag='commercials', hints=[], count=6)], end_bump=CatalogEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_4.mp4'), duration=8.0, tag='bumps', hints=[], count=3)), ReelBlock(start_bump=None, comms=[CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_8.mp4'), duration=12.0, tag='commercials', hints=[], count=6), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_5.mp4'), duration=24.0, tag='commercials', hints=[], count=5), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_2.mp4'), duration=17.0, tag='commercials', hints=[], count=6)], end_bump=None)], plan=[BlockPlanEntry(path=Path('integration_test/catalog/channel_1/Avatar/prime/Avatar S01E01.mp4'), skip=0.0, duration=240.4), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_7.mp4'), skip=0.0, duration=17.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_7.mp4'), skip=0.0, duration=22.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_2.mp4'), skip=0.0, duration=17.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_1.mp4'), skip=0.0, duration=32.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_3.mp4'), skip=0.0, duration=62.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_4.mp4'), skip=0.0, duration=8.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/Avatar/prime/Avatar S01E01.mp4'), skip=240.4, duration=240.4), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_2.mp4'), skip=0.0, duration=12.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_8.mp4'), skip=0.0, duration=12.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_6.mp4'), skip=0.0, duration=18.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_5.mp4'), skip=0.0, duration=24.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_4.mp4'), skip=0.0, duration=47.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_5.mp4'), skip=0.0, duration=10.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/Avatar/prime/Avatar S01E01.mp4'), skip=480.8, duration=240.4), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_6.mp4'), skip=0.0, duration=7.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_1.mp4'), skip=0.0, duration=32.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_7.mp4'), skip=0.0, duration=22.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_5.mp4'), skip=0.0, duration=24.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_3.mp4'), skip=0.0, duration=62.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_1.mp4'), skip=0.0, duration=7.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/Avatar/prime/Avatar S01E01.mp4'), skip=721.2, duration=240.4), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_3.mp4'), skip=0.0, duration=6.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_6.mp4'), skip=0.0, duration=18.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_8.mp4'), skip=0.0, duration=12.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_4.mp4'), skip=0.0, duration=47.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_2.mp4'), skip=0.0, duration=17.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_4.mp4'), skip=0.0, duration=8.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/Avatar/prime/Avatar S01E01.mp4'), skip=961.6, duration=240.4), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_8.mp4'), skip=0.0, duration=12.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_5.mp4'), skip=0.0, duration=24.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_2.mp4'), skip=0.0, duration=17.0)], sequence_key='Avatar-prime', start_bump=None, end_bump=None, bump_override=None),
        LiquidBlock(content=CatalogEntry(path=Path('integration_test/catalog/channel_1/Avatar/prime/Avatar S01E02.mp4'), duration=1202.0, tag='Avatar', hints=[DayPartHint(part_name='prime')], count=0), start_time=datetime(2025, 6, 1, 0, 30), end_time=datetime(2025, 6, 1, 1, 0), title='Avatar S01E02', break_strategy='standard', bump_info={'start': None, 'end': None, 'dir': None}, reel_blocks=[ReelBlock(start_bump=CatalogEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_2.mp4'), duration=12.0, tag='bumps', hints=[], count=4), comms=[CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_7.mp4'), duration=22.0, tag='commercials', hints=[], count=6), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_3.mp4'), duration=62.0, tag='commercials', hints=[], count=5), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_2.mp4'), duration=17.0, tag='commercials', hints=[], count=6)], end_bump=CatalogEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_5.mp4'), duration=10.0, tag='bumps', hints=[], count=3)), ReelBlock(start_bump=CatalogEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_1.mp4'), duration=7.0, tag='bumps', hints=[], count=3), comms=[CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_1.mp4'), duration=32.0, tag='commercials', hints=[], count=5), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_8.mp4'), duration=12.0, tag='commercials', hints=[], count=6), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_3.mp4'), duration=62.0, tag='commercials', hints=[], count=5)], end_bump=CatalogEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_6.mp4'), duration=7.0, tag='bumps', hints=[], count=3)), ReelBlock(start_bump=CatalogEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_6.mp4'), duration=7.0, tag='bumps', hints=[], count=3), comms=[CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_7.mp4'), duration=22.0, tag='commercials', hints=[], count=6), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_6.mp4'), duration=18.0, tag='commercials', hints=[], count=5), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_4.mp4'), duration=47.0, tag='commercials', hints=[], count=5), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_5.mp4'), duration=24.0, tag='commercials', hints=[], count=5)], end_bump=CatalogEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_3.mp4'), duration=6.0, tag='bumps', hints=[], count=3)), ReelBlock(start_bump=CatalogEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_7.mp4'), duration=17.0, tag='bumps', hints=[], count=3), comms=[CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_8.mp4'), duration=12.0, tag='commercials', hints=[], count=6), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_1.mp4'), duration=32.0, tag='commercials', hints=[], count=5), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_5.mp4'), duration=24.0, tag='commercials', hints=[], count=5), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_2.mp4'), duration=17.0, tag='commercials', hints=[], count=6)], end_bump=CatalogEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_4.mp4'), duration=8.0, tag='bumps', hints=[], count=3)), ReelBlock(start_bump=CatalogEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_5.mp4'), duration=10.0, tag='bumps', hints=[], count=3), comms=[CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_6.mp4'), duration=18.0, tag='commercials', hints=[], count=5), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_7.mp4'), duration=22.0, tag='commercials', hints=[], count=6), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_3.mp4'), duration=62.0, tag='commercials', hints=[], count=5)], end_bump=CatalogEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_1.mp4'), duration=7.0, tag='bumps', hints=[], count=3)), ReelBlock(start_bump=None, comms=[], end_bump=None)], plan=[BlockPlanEntry(path=Path('integration_test/catalog/channel_1/Avatar/prime/Avatar S01E02.mp4'), skip=0.0, duration=200.33333333333334), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_2.mp4'), skip=0.0, duration=12.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_7.mp4'), skip=0.0, duration=22.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_3.mp4'), skip=0.0, duration=62.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_2.mp4'), skip=0.0, duration=17.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_5.mp4'), skip=0.0, duration=10.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/Avatar/prime/Avatar S01E02.mp4'), skip=200.33333333333334, duration=200.33333333333334), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_1.mp4'), skip=0.0, duration=7.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_1.mp4'), skip=0.0, duration=32.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_8.mp4'), skip=0.0, duration=12.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_3.mp4'), skip=0.0, duration=62.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_6.mp4'), skip=0.0, duration=7.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/Avatar/prime/Avatar S01E02.mp4'), skip=400.6666666666667, duration=200.33333333333334), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_6.mp4'), skip=0.0, duration=7.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_7.mp4'), skip=0.0, duration=22.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_6.mp4'), skip=0.0, duration=18.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_4.mp4'), skip=0.0, duration=47.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_5.mp4'), skip=0.0, duration=24.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_3.mp4'), skip=0.0, duration=6.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/Avatar/prime/Avatar S01E02.mp4'), skip=601.0, duration=200.33333333333334), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_7.mp4'), skip=0.0, duration=17.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_8.mp4'), skip=0.0, duration=12.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_1.mp4'), skip=0.0, duration=32.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_5.mp4'), skip=0.0, duration=24.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_2.mp4'), skip=0.0, duration=17.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_4.mp4'), skip=0.0, duration=8.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/Avatar/prime/Avatar S01E02.mp4'), skip=801.3333333333334, duration=200.33333333333334), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_5.mp4'), skip=0.0, duration=10.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_6.mp4'), skip=0.0, duration=18.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_7.mp4'), skip=0.0, duration=22.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_3.mp4'), skip=0.0, duration=62.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_1.mp4'), skip=0.0, duration=7.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/Avatar/prime/Avatar S01E02.mp4'), skip=1001.6666666666667, duration=200.33333333333334)], sequence_key='Avatar-prime', start_bump=None, end_bump=None, bump_override=None)
    ]

    assert channel_schedule_data == expected_channel_schedule_data


if __name__ == "__main__":
    update_config(config_dir=Path("integration_test/confs"), runtime_dir=Path("integration_test/runtime"))
    # test_field_player()
    # station_42.start_catalog(graphical_interface=False, rebuild_catalog=True)
    station_42.start_catalog(graphical_interface=False, add_hour=True)
    station_42.start_catalog(graphical_interface=True)
    # field_player.main_loop(transition_fn=field_player.short_change_effect)
