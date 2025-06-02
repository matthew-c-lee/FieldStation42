import datetime

from fs42.reel_cutter import ReelCutter
from fs42.block_plan import BlockPlanEntry
from pydantic import BaseModel, Field, model_validator
from typing import Any
from fs42.catalog_entry import CatalogEntry


# class LiquidBlock:
#     def __init__(self, content, start_time, end_time, title=None, break_strategy="standard", bump_info=None):
#         self.content = content
#         # the requested starting time
#         self.start_time = start_time
#         # the expected/requested end time
#         self.end_time = end_time
#         if title is None and type(content) is not list:
#             self.title = content.title
#         else:
#             self.title = title
#         self.reel_blocks = None
#         self.plan = None
#         self.break_strategy = break_strategy

#         self.sequence_key = None

#         self.start_bump = None
#         self.end_bump = None
#         self.bump_override = None

#         if bump_info:
#             if "start" in bump_info:
#                 self.start_bump = bump_info["start"]
#             if "end" in bump_info:
#                 self.end_bump = bump_info["end"]
#             if "dir" in bump_info:
#                 self.bump_override = bump_info["dir"]

#     def __str__(self):
#         return f"{self.start_time.strftime('%m/%d %H:%M')} - {self.end_time.strftime('%H:%M')} - {self.title}"

#     def content_duration(self):
#         return self.content.duration

#     def playback_duration(self):
#         return (self.end_time - self.start_time).seconds

#     def buffer_duration(self):
#         return self.playback_duration() - self.content_duration()

#     def make_plan(self, catalog: ShowCatalog):
#         # first, collect any reels (commercials and bumps) we might need to buffer to the requested duration
#         diff = self.playback_duration() - self.content_duration()

#         # is there a start bump?
#         if self.start_bump:
#             diff -= self.start_bump.duration

#         if self.end_bump:
#             diff -= self.end_bump.duration

#         self.reel_blocks = None
#         if diff < -2:
#             err = f"Schedule logic error: duration requested {self.playback_duration()} is less than content {self.content_duration()}"
#             err += f" for show named: {self.content.title}"
#             raise (ValueError(err))

#         if diff > 2:
#             self.reel_blocks = catalog.make_reel_fill(self.start_time, diff, bump_dir=self.bump_override)
#         else:
#             self.reel_blocks = []

#         self.plan = ReelCutter.cut_reels_into_base(
#             self.content,
#             self.reel_blocks,
#             0,
#             self.content_duration(),
#             self.break_strategy,
#             self.start_bump,
#             self.end_bump,
#         )

class ReelBlock(BaseModel):
    start_bump: CatalogEntry | None = None
    comms: list[CatalogEntry] | None = Field(default_factory=list)
    end_bump: CatalogEntry | None = None

    def __str__(self):
        return f"ReelBlock: {self.duration} {len(self.comms)}"

    @property
    def duration(self):
        dur = 0
        if self.start_bump is not None:
            dur += self.start_bump.duration
        for comm in self.comms:
            dur += comm.duration
        if self.end_bump is not None:
            dur += self.end_bump.duration
        return dur

    def make_plan(self):
        entries = []
        if self.start_bump is not None:
            entries.append(BlockPlanEntry(path=self.start_bump.path, skip=0, duration=self.start_bump.duration))
        for comm in self.comms:
            entries.append(BlockPlanEntry(path=comm.path, skip=0, duration=comm.duration))
        if self.end_bump is not None:
            entries.append(BlockPlanEntry(path=self.end_bump.path, skip=0, duration=self.end_bump.duration))
        return entries



class LiquidBlock(BaseModel):
    # ----- core data -----
    content: Any
    start_time: datetime.datetime
    end_time: datetime.datetime
    title: str | None = None
    break_strategy: str = "standard"
    bump_info: dict | None = None

    # runtime / mutable
    reel_blocks: list[ReelBlock] | None = Field(default=None, exclude=True)
    plan: list[BlockPlanEntry] | None = Field(default=None, exclude=True)

    # ← optional “private” runtime attrs
    sequence_key: str | None = Field(default=None, exclude=True)
    start_bump: CatalogEntry | None = Field(default=None, exclude=True)
    end_bump: CatalogEntry | None = Field(default=None, exclude=True)
    bump_override: CatalogEntry | None = Field(default=None, exclude=True)

    # -------------------------------------------------
    # Validation / derivation
    # -------------------------------------------------
    @model_validator(mode="after")
    def _fill_defaults(self) -> "LiquidBlock":
        # title fallback
        if self.title is None and not isinstance(self.content, list):
            self.title = getattr(self.content, "title", "<no‑title>")
        # pull bump_info keys, if provided
        if self.bump_info:
            self.start_bump = self.bump_info.get("start")
            self.end_bump = self.bump_info.get("end")
            self.bump_override = self.bump_info.get("dir")
        return self

    # -------------------------------------------------
    # Computed helpers (no mutation)
    # -------------------------------------------------
    def content_duration(self) -> int:
        return self.content.duration      # assumes `.duration` seconds

    def playback_duration(self) -> int:
        return int((self.end_time - self.start_time).total_seconds())

    def buffer_duration(self) -> int:
        return self.playback_duration() - self.content_duration()

    # -------------------------------------------------
    # Stateful method (mutates self.plan / reel_blocks)
    # -------------------------------------------------
    def make_plan(self, catalog) -> None:
        diff = self.playback_duration() - self.content_duration()

        if self.start_bump:
            diff -= self.start_bump.duration
        if self.end_bump:
            diff -= self.end_bump.duration

        if diff < -2:
            raise ValueError(
                f"Schedule error: requested {self.playback_duration()} "
                f"is shorter than content {self.content_duration()} "
                f"for title {self.title}"
            )

        if diff > 2:
            self.reel_blocks = catalog.make_reel_fill(
                self.start_time, diff, bump_dir=self.bump_override
            )
        else:
            self.reel_blocks = []

        self.plan = ReelCutter.cut_reels_into_base(
            self.content,
            self.reel_blocks,
            0,
            self.content_duration(),
            self.break_strategy,
            self.start_bump,
            self.end_bump,
        )

class LiquidClipBlock(LiquidBlock):
    def __str__(self):
        return f"{self.start_time.strftime('%m/%d %H:%M')} - {self.end_time.strftime('%H:%M')} - {self.title}"

    def content_duration(self):
        return sum(clip.duration for clip in self.content)

    def make_plan(self, catalog):
        self.plan = []
        # first, collect any reels (commercials and bumps) we might need to buffer to the requested duration
        diff = self.playback_duration() - self.content_duration()

        # is there a start bump?
        if self.start_bump:
            diff -= self.start_bump.duration

        if self.end_bump:
            diff -= self.end_bump.duration

        self.reel_blocks = None
        if diff < -2:
            err = f"Schedule logic error: duration requested {self.playback_duration()} is less than content {self.content_duration()}"
            err += f" for show named: {self.content.title}"
            raise ValueError(err)
        if diff > 2:
            self.reel_blocks = catalog.make_reel_fill(self.start_time, diff, bump_dir=self.bump_override)
        else:
            self.reel_blocks = []

        self.plan = ReelCutter.cut_reels_into_clips(
            self.content, self.reel_blocks, self.break_strategy, self.start_bump, self.end_bump
        )



class LiquidOffAirBlock(LiquidBlock):
    def make_plan(self, catalog):
        self.plan = []
        current_mark = self.start_time

        while current_mark < self.end_time:
            duration = self.content.duration
            current_mark += datetime.timedelta(seconds=duration)
            datetime.timedelta()
            if current_mark > self.end_time:
                # then we will clip it to end at end time
                delta = current_mark - self.end_time
                duration -= delta.total_seconds()

            self.plan.append(BlockPlanEntry(path=self.content.path, skip=0, duration=duration))


class LiquidLoopBlock(LiquidBlock):
    def make_plan(self, catalog):
        entries = []
        keep_going = True
        current_mark: datetime.datetime = self.start_time
        next_mark: datetime.datetime = None
        current_index = 0
        while keep_going:
            clip = self.content[current_index]
            next_mark = current_mark + datetime.timedelta(seconds=clip.duration)
            duration = clip.duration
            if next_mark < self.end_time:
                current_index += 1
                if current_index >= len(self.content):
                    current_index = 0
            else:
                keep_going = False
                duration = (self.end_time - current_mark).total_seconds()

            entries.append(BlockPlanEntry(path=clip.path, skip=0, duration=duration))

            current_mark = next_mark
        self.plan = entries


# class ReelBlock:
#     def __init__(self, start_bump=None, comms=[], end_bump=None):
#         self.start_bump = start_bump
#         self.comms = comms
#         self.end_bump = end_bump

#     def __str__(self):
#         return f"ReelBlock: {self.duration} {len(self.comms)}"

#     @property
#     def duration(self):
#         dur = 0
#         if self.start_bump is not None:
#             dur += self.start_bump.duration
#         for comm in self.comms:
#             dur += comm.duration
#         if self.end_bump is not None:
#             dur += self.end_bump.duration
#         return dur

#     def make_plan(self):
#         entries = []
#         if self.start_bump is not None:
#             entries.append(BlockPlanEntry(path=self.start_bump.path, skip=0, duration=self.start_bump.duration))
#         for comm in self.comms:
#             entries.append(BlockPlanEntry(path=comm.path, skip=0, duration=comm.duration))
#         if self.end_bump is not None:
#             entries.append(BlockPlanEntry(path=self.end_bump.path, skip=0, duration=self.end_bump.duration))
#         return entries
