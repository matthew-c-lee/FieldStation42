import subprocess
from pathlib import Path
import shutil
from dataclasses import dataclass

# Constants
RESOLUTION = "2x2"
FPS = 1

@dataclass
class VideoEntry:
    duration: float
    color: str

def run_ffmpeg(output_file: Path, color: str, duration: float, extension: str):
    cmd = [
        "ffmpeg",
        "-y",
        "-f", "lavfi",
        "-i", f"color=c={color}:s={RESOLUTION}:d={duration}",
        "-r", str(FPS),
    ]

    match extension:
        case ".mp4":
            cmd += [
                "-c:v", "libx264",
                "-crf", "51",
                "-tune", "zerolatency",
                "-x264-params", "keyint=1",
                "-preset", "ultrafast",
            ]
        case ".webm":
            cmd += ["-c:v", "libvpx", "-b:v", "1M"]
        case ".mkv":
            cmd += ["-c:v", "libx264", "-crf", "30", "-preset", "ultrafast"]
        case _:
            raise ValueError(f"Unsupported video extension: {extension}")

    cmd.append(str(output_file))
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def try_parse_leaf(node) -> VideoEntry | None:
    if isinstance(node, dict) and {"duration", "color"} <= set(node.keys()):
        return VideoEntry(
            duration=node["duration"],
            color=node["color"]
        )
    return None

def walk(node: dict, path: Path):
    path.mkdir(parents=True, exist_ok=True)

    for node_name, value in node.items():
        if isinstance(value, dict) and {"duration", "color"} <= set(value.keys()):
            file_name = node_name
            output_file = path / file_name
            ext = output_file.suffix.lower()

            duration = value["duration"]
            color = value["color"]

            print(f"  -> Generating {output_file} ({duration}s, {color})")
            run_ffmpeg(output_file, color, duration, ext)

        elif isinstance(value, dict):
            walk(value, path / node_name)

def generate_catalog(catalog: dict, output_dir: Path):
    if output_dir.exists():
        print(f"Cleaning up existing output directory: {output_dir}")
        shutil.rmtree(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating catalog to {output_dir} from provided dictionary...")
    walk(catalog["catalog"], output_dir)
    print("Done.")
