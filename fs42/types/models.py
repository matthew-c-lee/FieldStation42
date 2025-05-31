from pathlib import Path
from pydantic import BaseModel, Field, model_validator, field_validator
from fs42.config.config import APP_CONFIG


class StationConfig(BaseModel):
    channel_number: int
    network_name: str
    
    catalog_path: Path
    schedule_path: Path | None = None
    content_dir: Path
    commercial_dir: Path
    bump_dir: Path
    
    play_sound: bool = False
    sound_to_play: Path | None = None

    sign_off_video: Path
    off_air_video: Path
    off_air_image: Path | None = None
    standby_image: Path | None = None

    monday: dict[str, dict] | None = None
    tuesday: dict[str, dict] | None = None
    wednesday: dict[str, dict] | None = None
    thursday: dict[str, dict] | None = None
    friday: dict[str, dict] | None = None
    saturday: dict[str, dict] | None = None
    sunday: dict[str, dict] | None = None
    
    panscan: int | None = None

    network_type: str = "standard"
    schedule_increment: float = 30.0
    break_strategy: str = "standard"
    commercial_free: bool = False
    clip_shows: list[str] = []
    break_duration: int = 120

    @model_validator(mode="after")
    def validate_all_files_exist(self):
        required_fields = ["sign_off_video", "off_air_video", "standby_image"]

        for field in required_fields:
            path = getattr(self, field, None)
            if not path or not path.exists():
                raise FileNotFoundError(f"{field} is missing or does not exist: {path}")
        return self
    
class ServerConfig(BaseModel):
    channel_socket: Path = APP_CONFIG.channel_socket_path
    status_socket: Path = APP_CONFIG.status_socket_path
    day_parts: dict[str, range | list[int]] = Field(default_factory=lambda: {
        "morning"   : range(6,10),
        "daytime"   : range(10,18),
        "prime"     : range(18,23),
        "late"      : [23,0, 1, 2],
        "overnight" : range(2, 6) 
    })

    @field_validator("day_parts", mode="before")
    @classmethod
    def parse_day_parts(cls, v):
        # Only process entries that are still raw dicts
        return {
            name: DayInfo(**conf).hours()
            if isinstance(conf, dict)
            else conf
            for name, conf in v.items()
        }
    
    model_config = {
        "arbitrary_types_allowed": True
    }

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
    
    def hours(self) -> range | list[int]:
        if self.end_hour > self.start_hour:
            return range(self.start_hour, self.end_hour)
        return list(range(self.start_hour, 24)) + list(range(0, self.end_hour + 1))
