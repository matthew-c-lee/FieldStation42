import json
from fs42.schedule_hint import TagHintReader
class StationManager(object):
    __we_are_all_one = {}
    stations = []

    overwatch = {"network_type": "standard",
                "schedule_increment": 30,
                "break_strategy": "standard",
                "commercial_free": False,
                "clip_shows": [],
                "break_duration": 120}

    # NOTE: This is the borg singleton pattern - __we_are_all_one
    def __new__(cls, *args, **kwargs):
        obj = super(StationManager, cls).__new__(cls, *args, **kwargs)
        obj.__dict__ = cls.__we_are_all_one
        return obj
    
    def __init__(self):
        if not len(self.stations):
            self.load_json_stations()
            self.server_conf = {"channel_socket": "runtime/channel.socket",
                                "status_socket": "runtime/play_status.socket"}
        for i in  range(len(self.stations)):
            station = self.stations[i]
            if station['network_type'] == "standard":
                self.stations[i] = TagHintReader.smooth_tags(station)

    def station_by_name(self, name):
        for station in self.stations:
            if station["network_name"] == name:
                return station
        return None
    
    def station_by_channel(self, channel):
        for station in self.stations:
            if station["channel_number"] == channel:
                return station
        return None

    def index_from_channel(self, channel):
        index = 0
        for station in self.stations:
            if station["channel_number"] == channel:
                return index
            index+=1
        return None


    def load_json_stations(self):
        import glob


        cfiles = glob.glob("confs/*.json")
        station_buffer = []
        for fname in cfiles:
            print(f"Loading configuration for: {fname}")
            with open(fname) as f:
                try:
                    d = json.load(f)
                    #set defaults for optionals
                    for key in StationManager.overwatch:
                        if key not in d['station_conf']:
                            d['station_conf'][key] = StationManager.overwatch[key]

                    station_buffer.append(d['station_conf'])
                except Exception as e:
                    print(f"Error loading station configuration: {fname}")
                    print(e)
                    exit(1)

        self.stations = sorted(station_buffer, key=lambda station: station['channel_number'])

