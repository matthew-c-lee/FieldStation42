import subprocess
import yaml
from pathlib import Path
import shutil
from dataclasses import dataclass

CATALOG_YAML = Path("integration_test/test_catalog.yaml")
OUTPUT_DIR = Path("integration_test/catalog")

RESOLUTION = "640x360"
FPS = 24

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

    # Handle different output formats
    match extension:
        case ".mp4":
            cmd += ["-c:v", "libx264", "-crf", "30", "-preset", "veryslow"]
        case ".webm":
            cmd += ["-c:v", "libvpx", "-b:v", "1M"]
        case ".mkv":
            cmd += ["-c:v", "libx264", "-crf", "30", "-preset", "veryslow"]
        case _:
            raise ValueError(f"Unsupported video extension: {extension}")

    cmd.append(str(output_file))
    subprocess.run(cmd, check=True)


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
            # key includes extension, e.g. "intro.mp4"
            file_name = node_name
            output_file = path / file_name
            ext = output_file.suffix.lower()

            duration = value["duration"]
            color = value["color"]

            print(f"  -> Generating {output_file} ({duration}s, {color})")

            run_ffmpeg(output_file, color, duration, ext)

        elif isinstance(value, dict):
            walk(value, path / node_name)

def generate_catalog():
    if OUTPUT_DIR.exists():
        print(f"Cleaning up existing output directory: {OUTPUT_DIR}")
        shutil.rmtree(OUTPUT_DIR)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(CATALOG_YAML, "r") as f:
        catalog = yaml.safe_load(f)

    print(f"Generating catalog from {CATALOG_YAML}...")
    walk(catalog["catalog"], OUTPUT_DIR)
    print("Done.")


if __name__ == "__main__":
    generate_catalog()
