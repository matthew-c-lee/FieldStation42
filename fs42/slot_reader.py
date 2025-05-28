from datetime import datetime
from fs42.types.models import StationConfig
import copy

from fs42 import timings

class SlotReader():

    @staticmethod
    def get_tag(conf: StationConfig, when:datetime):
        response = None
        slot = SlotReader.get_slot(conf, when)
        if slot and "tags" in slot:
            tags = slot['tags']
            
            if type(tags) is list:
                if len(tags) == 1 or when.minute < 30:
                    response = tags[0]
                else:
                    response = tags[1]
            else:
                response = tags

        return response
    
    @staticmethod
    def get_tag_from_slot(slot, when:datetime):
        response = None
        if slot and "tags" in slot:
            tags = slot['tags']
            
            if type(tags) is list:
                if len(tags) == 1 or when.minute < 30:
                    response = tags[0]
                else:
                    response = tags[1]
            else:
                response = tags

        return response

    @staticmethod
    def get_slot(conf: StationConfig, when:datetime):
        day_str = timings.DAYS[when.weekday()]
        slot_number = str(when.hour)
        response = None
        day = getattr(conf, day_str)
        if day:
            if slot_number in day:
                response = day[slot_number]
                
        return response
    
    @staticmethod
    def smooth_tags(conf):
        #this function smooths tags through slot boundaries - so if not specified
        last_tag = None
        smoothed = copy.deepcopy(conf)
        for day_index in timings.DAYS:
            for slot_index in timings.OPERATING_HOURS:
                slot_index = str(slot_index)
                day = getattr(conf, day_index)
                if slot_index in day:
                    if 'tags' in day[slot_index]:
                        last_tag = day[slot_index]
                    elif 'continued' in day[slot_index]:
                        if day[slot_index]['continued'] == True:
                            smoothed_day = getattr(day_index, slot_index)
                            smoothed_day['tags'] = last_tag['tags']
        return smoothed
