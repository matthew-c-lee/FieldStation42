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
import multiprocessing

import field_player
import station_42
import random
import socket, json
from time import sleep
import subprocess, os, signal

GENERATE_TEST_CATALOG = bool(int(os.environ.get("GENERATE_TEST_CATALOG", "1")))

update_config(config_dir=Path("integration_test/confs"), runtime_dir=Path("integration_test/runtime"))
random.seed(1) # Make randomness deterministic

@pytest.fixture(scope="session")
def catalog_setup():
    # Setup
    with freeze_time(time_to_freeze=datetime(2025, 6, 3, 12, 0, 0)):
        if GENERATE_TEST_CATALOG:
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
                    },
                    "channel_2": {
                        "prime": {
                            "looney_tunes": {                       
                                "season_1": {
                                    "Looney Tunes S01E01.mp4": {"duration": 420, "color": "yellow"},
                                    "Looney Tunes S01E02.mp4": {"duration": 415, "color": "yellow"},
                                    "Looney Tunes S01E03.mp4": {"duration": 430, "color": "yellow"},
                                },
                                "season_2": {
                                    "Looney Tunes S02E01.mp4": {"duration": 425, "color": "yellow"},
                                    "Looney Tunes S02E02.mp4": {"duration": 428, "color": "yellow"},
                                },
                            },
                            "adventure_time": {                
                                "season_1": {
                                    "Adventure Time S01E01.mp4": {"duration": 660, "color": "pink"},
                                    "Adventure Time S01E02.mp4": {"duration": 655, "color": "pink"},
                                }
                            },
                        },
                        "commercials": {
                            "commercial_a.mp4": {"duration": 25, "color": "cyan"},
                            "commercial_b.mp4": {"duration": 15, "color": "cyan"},
                            "commercial_c.mp4": {"duration": 35, "color": "cyan"},
                        },
                        "bumps": {
                            "bump_a.mp4": {"duration": 5, "color": "orange"},
                            "bump_b.mp4": {"duration": 7, "color": "orange"},
                            "bump_c.mp4": {"duration": 6, "color": "orange"},
                        },
                    }
                }
            }
            generate_catalog(catalog=catalog, output_dir=Path("integration_test/catalog"))

        # This will result in a binary file "channel_1_schedule.bin"
        station_42.start_catalog(graphical_interface=False, rebuild_catalog=True)

        # Add the schedule
        station_42.start_catalog(graphical_interface=False, add_hour=True)

        yield

        station_42.start_catalog(graphical_interface=False, delete_schedules=True)

@freeze_time(time_to_freeze=datetime(2025, 6, 3, 12, 0, 0))
def test_catalog(catalog_setup):
    channel_binary_path: Path = Path("integration_test/catalog") / "channel_1.bin"
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

    with open(channel_schedule_binary_path, "rb") as file:
        channel_schedule_data = pickle.load(file)

    expected_channel_schedule_data = [
        LiquidBlock(content=CatalogEntry(path=Path('integration_test/catalog/channel_1/Avatar/prime/Avatar S01E01.mp4'), duration=1202.0, tag='Avatar', hints=[DayPartHint(part_name='prime')], count=0), start_time=datetime(2025, 6, 3, 0, 0), end_time=datetime(2025, 6, 3, 0, 30), title='Avatar S01E01', break_strategy='standard', bump_info={'start': None, 'end': None, 'dir': None}, reel_blocks=[ReelBlock(start_bump=CatalogEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_7.mp4'), duration=17.0, tag='bumps', hints=[], count=3), comms=[CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_7.mp4'), duration=22.0, tag='commercials', hints=[], count=6), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_2.mp4'), duration=17.0, tag='commercials', hints=[], count=6), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_1.mp4'), duration=32.0, tag='commercials', hints=[], count=5), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_3.mp4'), duration=62.0, tag='commercials', hints=[], count=5)], end_bump=CatalogEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_4.mp4'), duration=8.0, tag='bumps', hints=[], count=3)), ReelBlock(start_bump=CatalogEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_2.mp4'), duration=12.0, tag='bumps', hints=[], count=4), comms=[CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_8.mp4'), duration=12.0, tag='commercials', hints=[], count=6), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_6.mp4'), duration=18.0, tag='commercials', hints=[], count=5), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_5.mp4'), duration=24.0, tag='commercials', hints=[], count=5), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_4.mp4'), duration=47.0, tag='commercials', hints=[], count=5)], end_bump=CatalogEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_5.mp4'), duration=10.0, tag='bumps', hints=[], count=3)), ReelBlock(start_bump=CatalogEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_6.mp4'), duration=7.0, tag='bumps', hints=[], count=3), comms=[CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_1.mp4'), duration=32.0, tag='commercials', hints=[], count=5), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_7.mp4'), duration=22.0, tag='commercials', hints=[], count=6), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_5.mp4'), duration=24.0, tag='commercials', hints=[], count=5), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_3.mp4'), duration=62.0, tag='commercials', hints=[], count=5)], end_bump=CatalogEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_1.mp4'), duration=7.0, tag='bumps', hints=[], count=3)), ReelBlock(start_bump=CatalogEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_3.mp4'), duration=6.0, tag='bumps', hints=[], count=3), comms=[CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_6.mp4'), duration=18.0, tag='commercials', hints=[], count=5), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_8.mp4'), duration=12.0, tag='commercials', hints=[], count=6), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_4.mp4'), duration=47.0, tag='commercials', hints=[], count=5), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_2.mp4'), duration=17.0, tag='commercials', hints=[], count=6)], end_bump=CatalogEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_4.mp4'), duration=8.0, tag='bumps', hints=[], count=3)), ReelBlock(start_bump=None, comms=[CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_8.mp4'), duration=12.0, tag='commercials', hints=[], count=6), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_5.mp4'), duration=24.0, tag='commercials', hints=[], count=5), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_2.mp4'), duration=17.0, tag='commercials', hints=[], count=6)], end_bump=None)], plan=[BlockPlanEntry(path=Path('integration_test/catalog/channel_1/Avatar/prime/Avatar S01E01.mp4'), skip=0.0, duration=240.4), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_7.mp4'), skip=0.0, duration=17.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_7.mp4'), skip=0.0, duration=22.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_2.mp4'), skip=0.0, duration=17.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_1.mp4'), skip=0.0, duration=32.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_3.mp4'), skip=0.0, duration=62.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_4.mp4'), skip=0.0, duration=8.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/Avatar/prime/Avatar S01E01.mp4'), skip=240.4, duration=240.4), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_2.mp4'), skip=0.0, duration=12.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_8.mp4'), skip=0.0, duration=12.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_6.mp4'), skip=0.0, duration=18.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_5.mp4'), skip=0.0, duration=24.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_4.mp4'), skip=0.0, duration=47.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_5.mp4'), skip=0.0, duration=10.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/Avatar/prime/Avatar S01E01.mp4'), skip=480.8, duration=240.4), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_6.mp4'), skip=0.0, duration=7.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_1.mp4'), skip=0.0, duration=32.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_7.mp4'), skip=0.0, duration=22.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_5.mp4'), skip=0.0, duration=24.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_3.mp4'), skip=0.0, duration=62.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_1.mp4'), skip=0.0, duration=7.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/Avatar/prime/Avatar S01E01.mp4'), skip=721.2, duration=240.4), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_3.mp4'), skip=0.0, duration=6.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_6.mp4'), skip=0.0, duration=18.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_8.mp4'), skip=0.0, duration=12.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_4.mp4'), skip=0.0, duration=47.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_2.mp4'), skip=0.0, duration=17.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_4.mp4'), skip=0.0, duration=8.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/Avatar/prime/Avatar S01E01.mp4'), skip=961.6, duration=240.4), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_8.mp4'), skip=0.0, duration=12.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_5.mp4'), skip=0.0, duration=24.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_2.mp4'), skip=0.0, duration=17.0)], sequence_key='Avatar-prime', start_bump=None, end_bump=None, bump_override=None),
        LiquidBlock(content=CatalogEntry(path=Path('integration_test/catalog/channel_1/Avatar/prime/Avatar S01E02.mp4'), duration=1202.0, tag='Avatar', hints=[DayPartHint(part_name='prime')], count=0), start_time=datetime(2025, 6, 3, 0, 30), end_time=datetime(2025, 6, 3, 1, 0), title='Avatar S01E02', break_strategy='standard', bump_info={'start': None, 'end': None, 'dir': None}, reel_blocks=[ReelBlock(start_bump=CatalogEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_2.mp4'), duration=12.0, tag='bumps', hints=[], count=4), comms=[CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_7.mp4'), duration=22.0, tag='commercials', hints=[], count=6), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_3.mp4'), duration=62.0, tag='commercials', hints=[], count=5), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_2.mp4'), duration=17.0, tag='commercials', hints=[], count=6)], end_bump=CatalogEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_5.mp4'), duration=10.0, tag='bumps', hints=[], count=3)), ReelBlock(start_bump=CatalogEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_1.mp4'), duration=7.0, tag='bumps', hints=[], count=3), comms=[CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_1.mp4'), duration=32.0, tag='commercials', hints=[], count=5), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_8.mp4'), duration=12.0, tag='commercials', hints=[], count=6), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_3.mp4'), duration=62.0, tag='commercials', hints=[], count=5)], end_bump=CatalogEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_6.mp4'), duration=7.0, tag='bumps', hints=[], count=3)), ReelBlock(start_bump=CatalogEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_6.mp4'), duration=7.0, tag='bumps', hints=[], count=3), comms=[CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_7.mp4'), duration=22.0, tag='commercials', hints=[], count=6), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_6.mp4'), duration=18.0, tag='commercials', hints=[], count=5), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_4.mp4'), duration=47.0, tag='commercials', hints=[], count=5), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_5.mp4'), duration=24.0, tag='commercials', hints=[], count=5)], end_bump=CatalogEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_3.mp4'), duration=6.0, tag='bumps', hints=[], count=3)), ReelBlock(start_bump=CatalogEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_7.mp4'), duration=17.0, tag='bumps', hints=[], count=3), comms=[CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_8.mp4'), duration=12.0, tag='commercials', hints=[], count=6), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_1.mp4'), duration=32.0, tag='commercials', hints=[], count=5), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_5.mp4'), duration=24.0, tag='commercials', hints=[], count=5), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_2.mp4'), duration=17.0, tag='commercials', hints=[], count=6)], end_bump=CatalogEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_4.mp4'), duration=8.0, tag='bumps', hints=[], count=3)), ReelBlock(start_bump=CatalogEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_5.mp4'), duration=10.0, tag='bumps', hints=[], count=3), comms=[CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_6.mp4'), duration=18.0, tag='commercials', hints=[], count=5), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_7.mp4'), duration=22.0, tag='commercials', hints=[], count=6), CatalogEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_3.mp4'), duration=62.0, tag='commercials', hints=[], count=5)], end_bump=CatalogEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_1.mp4'), duration=7.0, tag='bumps', hints=[], count=3)), ReelBlock(start_bump=None, comms=[], end_bump=None)], plan=[BlockPlanEntry(path=Path('integration_test/catalog/channel_1/Avatar/prime/Avatar S01E02.mp4'), skip=0.0, duration=200.33333333333334), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_2.mp4'), skip=0.0, duration=12.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_7.mp4'), skip=0.0, duration=22.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_3.mp4'), skip=0.0, duration=62.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_2.mp4'), skip=0.0, duration=17.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_5.mp4'), skip=0.0, duration=10.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/Avatar/prime/Avatar S01E02.mp4'), skip=200.33333333333334, duration=200.33333333333334), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_1.mp4'), skip=0.0, duration=7.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_1.mp4'), skip=0.0, duration=32.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_8.mp4'), skip=0.0, duration=12.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_3.mp4'), skip=0.0, duration=62.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_6.mp4'), skip=0.0, duration=7.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/Avatar/prime/Avatar S01E02.mp4'), skip=400.6666666666667, duration=200.33333333333334), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_6.mp4'), skip=0.0, duration=7.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_7.mp4'), skip=0.0, duration=22.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_6.mp4'), skip=0.0, duration=18.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_4.mp4'), skip=0.0, duration=47.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_5.mp4'), skip=0.0, duration=24.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_3.mp4'), skip=0.0, duration=6.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/Avatar/prime/Avatar S01E02.mp4'), skip=601.0, duration=200.33333333333334), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_7.mp4'), skip=0.0, duration=17.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_8.mp4'), skip=0.0, duration=12.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_1.mp4'), skip=0.0, duration=32.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_5.mp4'), skip=0.0, duration=24.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_2.mp4'), skip=0.0, duration=17.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_4.mp4'), skip=0.0, duration=8.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/Avatar/prime/Avatar S01E02.mp4'), skip=801.3333333333334, duration=200.33333333333334), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_5.mp4'), skip=0.0, duration=10.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_6.mp4'), skip=0.0, duration=18.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_7.mp4'), skip=0.0, duration=22.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/commercials/commercial_3.mp4'), skip=0.0, duration=62.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/bumps/bump_1.mp4'), skip=0.0, duration=7.0), BlockPlanEntry(path=Path('integration_test/catalog/channel_1/Avatar/prime/Avatar S01E02.mp4'), skip=1001.6666666666667, duration=200.33333333333334)], sequence_key='Avatar-prime', start_bump=None, end_bump=None, bump_override=None)
    ]

    assert channel_schedule_data == expected_channel_schedule_data

@pytest.fixture(scope="session", autouse=False)
def xvfb_session():
    """Provide a running Xvfb for the entire test session."""
    proc = subprocess.Popen(
        ["Xvfb", ":98", "-screen", "0", "1280x720x24"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    os.environ["DISPLAY"] = ":98"
    sleep(1)  # give the server time to start
    try:
        yield
    finally:
        proc.send_signal(signal.SIGTERM)
        proc.wait()

def query_mpv(prop: str, sock_path="/tmp/mpvsocket", timeout=2):
    req = {"command": ["get_property", prop], "request_id": 1}
    with socket.socket(socket.AF_UNIX) as s:
        s.settimeout(timeout)
        s.connect(sock_path)
        s.sendall((json.dumps(req) + "\n").encode())

        # turn the socket into a file‑like object so we can readline()
        with s.makefile("r") as f:
            line = f.readline()          # one complete JSON object
            return json.loads(line)["data"]

@pytest.fixture
def freeze_dt(request):
    """Indirection target for @pytest.mark.parametrize(..., indirect=True)."""
    return request.param

def player_worker(ts: datetime):
    # ts is a datetime; freeze inside the child
    update_config(config_dir=Path("integration_test/confs"), runtime_dir=Path("integration_test/runtime"))

    with freeze_time(ts):
        field_player.main_loop(transition_fn=field_player.short_change_effect)

@pytest.fixture
def running_player(xvfb_session, catalog_setup, freeze_dt: datetime):
    update_config(config_dir=Path("integration_test/confs"), runtime_dir=Path("integration_test/runtime"))
    
    p = multiprocessing.Process(target=player_worker, args=(freeze_dt,), daemon=True)
    p.start()
    sleep(1)
    try:
        yield
    finally:
        p.join(timeout=0.2)
        if p.is_alive():
            p.kill()

@pytest.mark.parametrize("freeze_dt", [
    datetime(2025, 6, 3, 0, 5, 0),
], indirect=True)
def test_player(running_player):
    playing_path = query_mpv("path")
    print(playing_path)
    assert playing_path == "integration_test/catalog/channel_1/commercials/commercial_1.mp4"

    # Switch to channel 2
    socket_path = Path("integration_test/runtime/channel.socket")
    with open(socket_path, "w") as f:
        json.dump({"command": "direct", "channel": 2}, f)

    sleep(0.3)
        
    # Verify that it changed the channel
    playing_path = query_mpv("path")
    print(playing_path)
    
    assert playing_path == "integration_test/catalog/channel_2/commercials/commercial_c.mp4"

    # Switch to channel 2
    socket_path = Path("integration_test/runtime/channel.socket")
    with open(socket_path, "w") as f:
        json.dump({"command": "direct", "channel": 2}, f)
    

if __name__ == "__main__":
    update_config(config_dir=Path("integration_test/confs"), runtime_dir=Path("integration_test/runtime"))
    # test_field_player()
    # station_42.start_catalog(graphical_interface=False, rebuild_catalog=True)
    # station_42.start_catalog(graphical_interface=False, add_hour=True)
    # field_player.main_loop(transition_fn=field_player.short_change_effect)
    station_42.start_catalog(graphical_interface=True)
    # import shutil, sys, subprocess, os, signal
    # xvfb = subprocess.Popen(
    #     ["Xvfb", ":99", "-screen", "0", "1280x720x24"],
    #     stdout=subprocess.DEVNULL,
    #     stderr=subprocess.PIPE,
    # )
    # try:
    #     os.environ["DISPLAY"] = ":99"
    #     sleep(1)                         # give the server a moment
    #     field_player.main_loop(transition_fn=field_player.short_change_effect)
    # finally:
    #     xvfb.send_signal(signal.SIGTERM)
    #     stderr = xvfb.stderr.read().decode()
    #     xvfb.wait()
    #     if stderr:
    #         print("Xvfb stderr:\n", stderr)
