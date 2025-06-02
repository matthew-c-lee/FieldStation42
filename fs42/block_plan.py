from pydantic import BaseModel
from pathlib import Path


class BlockPlanEntry(BaseModel):
    path: Path
    skip: float
    duration: float

    def __str__(self):
        return f"PlanEntry: {self.path} skip={self.skip} duration={self.duration}"