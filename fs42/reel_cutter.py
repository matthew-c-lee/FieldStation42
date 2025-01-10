
from fs42.block_plan import BlockPlanEntry

class ReelCutter:
    @staticmethod
    def cut_reels_into_base(base_clip, reel_blocks, base_offset, base_duration, break_stratgy):
        entries = []
        break_count = 0

        if reel_blocks:
            break_count = len(reel_blocks)
        
        if break_count <= 1 or break_stratgy == 'end':
            # then don't cut the base at all
            entries.append(BlockPlanEntry(base_clip.path, base_offset, base_duration))
            for _block in reel_blocks:
                #and put the reel at the end if there is one
                entries += _block.make_plan()
        else:
            
            segment_duration = base_clip.duration / break_count
            offset = base_offset

            for i in range(break_count):
                entries.append(BlockPlanEntry(base_clip.path, offset, segment_duration))
                entries += reel_blocks[i].make_plan()
                offset += segment_duration

        return entries
    
    @staticmethod
    def cut_reels_into_clips(clips, reel_blocks, base_offset, base_duration, break_stategy):
        entries = []
        if reel_blocks:
            break_count = len(reel_blocks)
        else:
            break_count = 0
        if break_count <= 1 or break_stategy == 'end':
            # then don't cut the base at all
            for clip in clips:
                entries.append(BlockPlanEntry(clip.path, 0, clip.duration))
            for _block in reel_blocks:
                #and put the reel at the end if there is one
                entries += _block.make_plan()
        else:
            
            clips_per_segment = len(clips)/break_count

            for i in range(len(clips)):
                clip = clips[i]
                entries.append(BlockPlanEntry(clip.path, 0, clip.duration))
                if (i % clips_per_segment) == 0:
                    reel = reel_blocks.pop(0)
                    entries.append(BlockPlanEntry(clip.path, 0, clip.duration))
            
            while len(reel_blocks):
                reel = reel_blocks.pop(0)
                entries.append(BlockPlanEntry(clip.path, 0, clip.duration))                

        return entries
