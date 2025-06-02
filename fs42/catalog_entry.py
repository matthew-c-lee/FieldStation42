import os
from pathlib import Path
from fs42.schedule_hint import DayPartHint
from pathlib import Path
from pydantic import BaseModel, field_validator, computed_field

class MatchingContentNotFound(Exception):
    pass

class NoFillerContentFound(Exception):
    pass

# class CatalogEntry:
#     def __init__(self, path: Path, duration, tag: str, hints=[]):
#         self.path = path
#         #get the show name from the path
#         self.title = path.stem
#         self.duration = duration
#         self.tag = tag
#         self.count = 0
#         self.hints = hints

#     def __repr__(self):
#         return (
#             f"CatalogEntry("
#             f"path={self.path!r}, "
#             f"duration={self.duration!r}, "
#             f"tag={self.tag!r}, "
#             f"hints={self.hints!r})"
#         )

#     def __str__(self):
#         hints = list(map(str, self.hints))
#         return f"{self.title:<20.20} | {self.tag:<10.10} | {self.duration:<8.1f} | {hints} | {self.path}"
    



class CatalogEntry(BaseModel):
    path: Path
    duration: float
    tag: str
    hints: list[DayPartHint] = []

    count: int = 0

    @computed_field(repr=False)
    @property
    def title(self) -> str:
        return self.path.stem

    def __str__(self):
        hints_str = list(map(str, self.hints))
        return f"{self.title:<20.20} | {self.tag:<10.10} | {self.duration:<8.1f} | {hints_str} | {self.path}"
