#!/usr/bin/env python3
"""Edit the real CUA browser recording into a demo and README GIFs.

Requires ffmpeg, ffprobe, and the locally captured docs/media/raw-ui-demo.mp4.
The raw recording is deliberately excluded from deliverables. No UI is faked.
"""
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / "docs" / "media"
WORK = ROOT / ".media-work"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
CROP = "crop=1174:758:94:175"
SCENES = [
    (0, 5, "Dead Letter Office  /  A local AI reading room"),
    (38, 13, "Ask about the loose ends"),
    (62, 16, "Follow a citation to the complete letter"),
    (92, 15, "Keep both accounts when witnesses disagree"),
    (107, 12, "Browse twelve original fictional letters"),
    (124, 10, "A relevant passage can say the answer is unknown"),
    (164, 7, "Read the evidence before drawing a conclusion"),
]


def run(*args):
    subprocess.run([str(value) for value in args], check=True)


def gif(source, name, start=0, duration=None, speed=1.0, width=960):
    select = ["-ss", str(start), "-i", source]
    if duration is not None:
        select += ["-t", str(duration)]
    filters = (f"setpts=PTS/{speed},fps=7,scale={width}:-1:flags=lanczos,split[a][b];"
               "[a]palettegen=max_colors=192:stats_mode=diff[p];"
               "[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle")
    run("ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *select,
        "-filter_complex", filters, "-loop", "0", "-gifflags", "+transdiff", MEDIA / name)


def main():
    WORK.mkdir(exist_ok=True)
    raw = MEDIA / "raw-ui-demo.mp4"
    if not raw.exists():
        raise SystemExit("Supply the real browser recording first; this script does not simulate an interface.")
    listing = []
    footer = WORK / "footer.txt"
    footer.write_text("ACTUAL BROWSER RECORDING  |  Edited for pace  |  Fictional archive  |  Local CPU")
    timeline = []
    offset = 0
    for index, (start, duration, title) in enumerate(SCENES):
        caption = WORK / f"caption-{index}.txt"
        caption.write_text(title)
        target = WORK / f"clip-{index:02d}.mp4"
        filters = (f"{CROP},pad=1280:896:53:66:color=0x211c29,"
                   f"drawtext=fontfile={FONT}:textfile={caption}:fontsize=25:fontcolor=0xe5dac9:x=53:y=21,"
                   f"drawtext=fontfile={FONT}:textfile={footer}:fontsize=16:fontcolor=0xb4a7bd:x=53:y=856")
        run("ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", start, "-i", raw, "-t", duration,
            "-vf", filters, "-an", "-r", "20", "-c:v", "libx264", "-preset", "fast", "-crf", "19",
            "-pix_fmt", "yuv420p", target)
        listing.append(f"file '{target.as_posix()}'")
        timeline.append({"raw_start": start, "duration": duration, "demo_start": offset, "caption": title})
        offset += duration
    concat = WORK / "clips.txt"
    concat.write_text("\n".join(listing) + "\n")
    demo = MEDIA / "demo.mp4"
    run("ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", concat,
        "-c", "copy", "-movflags", "+faststart", demo)
    run("ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", "42", "-i", raw,
        "-vf", CROP, "-frames:v", "1", MEDIA / "hero.png")
    gif(demo, "MASTER.gif", speed=2.6)
    gif(demo, "01-search.gif", start=5, duration=13)
    gif(demo, "02-evidence.gif", start=18, duration=16)
    gif(demo, "03-contradictions.gif", start=34, duration=15)
    gif(demo, "04-archive.gif", start=49, duration=12)
    (MEDIA / "capture-notes.json").write_text(json.dumps({
        "source": "Actual x11 browser recording performed through CUA; not reconstructed UI frames.",
        "raw_duration_seconds": 180, "crop": {"x": 94, "y": 175, "width": 1174, "height": 758},
        "edits": "Cuts remove idle time; browser/desktop chrome cropped; captions added outside the captured UI. No interface text/results altered.",
        "demo_seconds": offset, "master_gif_speed": 2.6, "scenes": timeline,
        "audio": "None. This is a silent demonstration.",
        "raw_in_deliverable": False,
    }, indent=2) + "\n")
    print(f"Created {offset}-second actual-UI demo and five GIFs in {MEDIA}")


if __name__ == "__main__":
    main()
