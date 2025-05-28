import json
import logging
from fs42.slot_reader import SlotReader
import glob
from pathlib import Path
from fs42.types.models import (
    StationConfig,
    ServerConfig,
)


class StationManager(object):

    __we_are_all_one = {}
    
    stations: list[StationConfig] = []

    filechecks = ["sign_off_video", "off_air_video", "standby_image"]

    main_config = Path("confs/main_config.json")

    # NOTE: This is the borg singleton pattern - __we_are_all_one
    def __new__(cls, *args, **kwargs):
        obj = super(StationManager, cls).__new__(cls, *args, **kwargs)
        obj.__dict__ = cls.__we_are_all_one
        return obj
    
    def __init__(self):
        if not len(self.stations):
            self.server_conf = ServerConfig()
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
        return self.server_conf.day_parts

    def load_main_config(self):
        _l = logging.getLogger("STATIONMANAGER")
        if not StationManager.main_config.exists():
            # skip, no overrides
            return
        
        with open(StationManager.main_config) as file:
            try:
                data = json.load(file)

                self.server_conf = ServerConfig(**data)
                
                # if "channel_socket" in data:
                #     self.server_conf["channel_socket"] = data["channel_socket"]
                # if "status_socket" in data:
                #     self.server_conf["status_socket"] = data["status_socket"]
                # if "day_parts" in data:
                #     new_parts = {}
                #     for key in data["day_parts"]:
                #         start_hour = data["day_parts"][key]["start_hour"]
                #         end_hour = data["day_parts"][key]["end_hour"]
                #         if end_hour > start_hour:
                #             new_parts[key] = range(start_hour, end_hour)
                #         else:
                #             #wraps midnight - manually build the list of hours
                #             hours = []
                #             hour = start_hour
                #             while hour <= 23:
                #                 hours.append(hour)
                #                 hour+=1
                #             hour = 0
                #             while hour <= end_hour:
                #                 hours.append(hour)
                #                 hour+=1
                #             new_parts[key] = hours
                #     self.server_conf["day_parts"] = new_parts

            except Exception as e:
                print(e)
                _l.exception(e)
                _l.error(f"Error loading main config overrides from {StationManager.main_config}")
                exit(-1)
    

    def load_json_stations(self): 
        _l = logging.getLogger("STATIONMANAGER")
        config_files = glob.glob("confs/*.json")
        station_buffer = []
        for file_path in config_files:
            if file_path == StationManager.main_config:
                continue

            with open(file_path) as file:
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
                    _l.error(f"Error loading station configuration: {file_path}")
                    _l.exception(e)
                    _l.error("*" * 60)
                    exit(-1)

        self.stations = sorted(station_buffer, key=lambda station: station.channel_number)

