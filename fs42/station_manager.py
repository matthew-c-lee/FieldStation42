import json
import logging
import os
from fs42.slot_reader import SlotReader
import glob
from pathlib import Path
from pydantic import BaseModel, Field, model_validator

class StationConfig(BaseModel):
    channel_number: int
    network_name: str
    
    catalog_path: Path
    content_dir: Path
    commercial_dir: Path
    bump_dir: Path

    network_type: str = "standard"
    schedule_increment: float = 30.0
    break_strategy: str = "standard"
    commercial_free: bool = False
    clip_shows: list[str] = []
    break_duration: int = 120

    sign_off_video: Path
    off_air_video: Path
    standby_image: Path

    @model_validator(mode="after")
    def validate_all_files_exist(self):
        required_fields = ["sign_off_video", "off_air_video", "standby_image"]

        for field in required_fields:
            path = getattr(self, field, None)
            if not path or not path.exists():
                raise FileNotFoundError(f"{field} is missing or does not exist: {path}")
        return self
    
class MainConfig(BaseModel):
    channel_socket
    pass

class DayInfo(BaseModel):
    start_hour: int
    end_hour: int

    @model_validator(mode="after")
    def validate_hours(self):
        if not (0 <= self.start_hour <= 23):
            raise ValueError("start_hour must be between 0 and 23")
        if not (0 <= self.end_hour <= 23):
            raise ValueError("end_hour must be between 0 and 23")
        return self
    
    @property
    def hours(self) -> list[int]:
        """Returns the list of hours this day part covers, including wraparound."""
        if self.end_hour > self.start_hour:
            return list(range(self.start_hour, self.end_hour))
        return list(range(self.start_hour, 24)) + list(range(0, self.end_hour))


class StationManager(object):

    __we_are_all_one = {}
    
    stations: list[StationConfig] = []

    overwatch = {"network_type": "standard",
                "schedule_increment": 30,  
                "break_strategy": "standard",
                "commercial_free": False,
                "clip_shows": [],
                "break_duration": 120}

    filechecks = ["sign_off_video", "off_air_video", "standby_image"]

    main_config = Path("confs/main_config.json")

    # NOTE: This is the borg singleton pattern - __we_are_all_one
    def __new__(cls, *args, **kwargs):
        obj = super(StationManager, cls).__new__(cls, *args, **kwargs)
        obj.__dict__ = cls.__we_are_all_one
        return obj
    
    def __init__(self):
        if not len(self.stations):
            self.server_conf = {"channel_socket": "runtime/channel.socket",
                                "status_socket": "runtime/play_status.socket",
                                "day_parts" : {
                                    "morning"  : range(6,10),
                                    "daytime"  : range(10,18),
                                    "prime"    : range(18,23),
                                    "late"     : [23,0, 1, 2],
                                    "overnight": range(2, 6) 
                                    }
                                }
            self.load_main_config()
            self.load_json_stations()
        
        for i in range(len(self.stations)):
            station = self.stations[i]
            if station.network_type == "standard":
                self.stations[i] = SlotReader.smooth_tags(station)

    def station_by_name(self, name):
        for station in self.stations:
            if station.network_name == name:
                return station
        return None
    
    def station_by_channel(self, channel):
        for station in self.stations:
            if station.channel_number == channel:
                return station
        return None

    def index_from_channel(self, channel):
        index = 0
        for station in self.stations:
            if station.channel_number == channel:
                return index
            index+=1
        return None

    def get_day_parts(self):
        return self.server_conf["day_parts"]

    def load_main_config(self):
        _l = logging.getLogger("STATIONMANAGER")
        if StationManager.main_config.exists:
            with open(StationManager.main_config) as file:
                try:
                    data = json.load(file)

                    main_config = MainConfig(**data)
                    
                    if "channel_socket" in data:
                        self.server_conf["channel_socket"] = data["channel_socket"]
                    if "status_socket" in data:
                        self.server_conf["status_socket"] = data["status_socket"]
                    if "day_parts" in data:
                        new_parts = {}
                        for key in data["day_parts"]:
                            start_hour = data["day_parts"][key]["start_hour"]
                            end_hour = data["day_parts"][key]["end_hour"]
                            if end_hour > start_hour:
                                new_parts[key] = range(start_hour, end_hour)
                            else:
                                #wraps midnight - manually build the list of hours
                                hours = []
                                hour = start_hour
                                while hour <= 23:
                                    hours.append(hour)
                                    hour+=1
                                hour = 0
                                while hour <= end_hour:
                                    hours.append(hour)
                                    hour+=1
                                new_parts[key] = hours
                        self.server_conf["day_parts"] = new_parts

                except Exception as e:
                    print(e)
                    _l.exception(e)
                    _l.error(f"Error loading main config overrides from {StationManager.main_config}")
                    exit(-1)
        # else skip, no over rides

    def load_json_stations(self): 
        _l = logging.getLogger("STATIONMANAGER")
        config_files = glob.glob("confs/*.json")
        station_buffer = []
        for file_name in config_files:
            if file_name != StationManager.main_config:
                with open(file_name) as file:
                    try:
                        data = json.load(file)
                        station_config = StationConfig(**data['station_conf'])

                        #set defaults for optionals
                        # for key in StationManager.overwatch:
                        #     if key not in data['station_conf']:
                        #         data['station_conf'][key] = StationManager.overwatch[key]

                        # for required_file in StationManager.filechecks:
                        #     if required_file in data['station_conf']:
                        #         if not os.path.exists(data['station_conf'][required_file]):
                        #             _l.error("*" * 60)
                        #             _l.error(f"Error while checking configuration for {file_name}")
                        #             _l.error(f"The filepath specified for {required_file} does not exist: {data['station_conf'][required_file]}")
                        #             _l.error("*" * 60)
                        #             exit(-1)

                        station_buffer.append(station_config)
                    except Exception as e:
                        _l.error("*" * 60)
                        _l.error(f"Error loading station configuration: {file_name}")
                        _l.exception(e)
                        _l.error("*" * 60)
                        exit(-1)

        self.stations = sorted(station_buffer, key=lambda station: station.channel_number)

