#!/usr/bin/env python3
"""Put your own sound on a video using ffmpeg.

The new audio always ends exactly when the video ends:
  - audio shorter than the video -> it loops until the video is over
  - audio longer than the video  -> it is cut off at the end of the video

Easiest: double-click this file and pick the video, then the sound, in the
windows that open. Or select both files and drag them onto this file together.

From a terminal:
    python3 add_audio.py video.mp4 music.mp3                  # -> video_with_audio.mp4
    python3 add_audio.py video.wmv music.wav -o final.mp4
    python3 add_audio.py video.mp4 music.mp3 --keep-original  # mix with the video's own sound
    python3 add_audio.py video.mp4 music.mp3 --volume 0.5 --fade-out 2

Requires ffmpeg and ffprobe on PATH (https://ffmpeg.org/download.html).
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Video codecs that can be copied into an .mp4 untouched (fast, no quality loss).
COPYABLE_VIDEO = {"h264", "hevc", "mpeg4", "av1"}

AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".oga", ".flac", ".wma", ".opus"}


def launched_from_explorer():
    """True when Windows opened a fresh console for us (double-click or drag-and-drop)."""
    return os.name == "nt" and "PROMPT" not in os.environ


def pick_file(title, filetypes):
    """Ask for one file with a file-picker window, or by typing a path if that's unavailable."""
    try:
        import tkinter
        from tkinter import filedialog
        root = tkinter.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        path = filedialog.askopenfilename(title=title, filetypes=filetypes + [("All files", "*.*")])
        root.destroy()
        return path
    except Exception:
        return input(f"{title} - drag the file here and press Enter: ").strip().strip('"')


def free_name(path):
    """path, or path with (2), (3), ... added if it already exists."""
    n = 2
    candidate = path
    while candidate.exists():
        candidate = path.with_name(f"{path.stem} ({n}){path.suffix}")
        n += 1
    return candidate


def probe(path, entries, stream=None):
    cmd = ["ffprobe", "-v", "error"]
    if stream:
        cmd += ["-select_streams", stream]
    cmd += ["-show_entries", entries, "-of", "default=noprint_wrappers=1:nokey=1", str(path)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip().splitlines()


def main():
    parser = argparse.ArgumentParser(description="Add (and loop) your own audio on a video.")
    parser.add_argument("video", nargs="?", help="input video (mp4, wmv, mov, avi, mkv, ...)")
    parser.add_argument("audio", nargs="?", help="your sound (mp3, wav, m4a, ogg, ...)")
    parser.add_argument("-o", "--output", help="output .mp4 (default: <video>_with_audio.mp4)")
    parser.add_argument("--keep-original", action="store_true",
                        help="mix your sound with the video's original sound instead of replacing it")
    parser.add_argument("--volume", type=float, default=1.0,
                        help="volume of your sound, e.g. 0.5 = half, 2 = double (default 1)")
    parser.add_argument("--fade-out", type=float, default=0,
                        help="fade the sound out over the last N seconds (default 0 = no fade)")
    parser.add_argument("--audio-bitrate", default="192k", help="AAC bitrate (default 192k)")
    parser.add_argument("--overwrite", action="store_true", help="replace the output file if it exists")
    args = parser.parse_args()

    for tool in ("ffmpeg", "ffprobe"):
        if shutil.which(tool) is None:
            sys.exit(f"error: {tool} not found on PATH. Install ffmpeg from https://ffmpeg.org/download.html")

    if not args.video:
        args.video = pick_file("Step 1 of 2: choose the VIDEO",
                               [("Videos", "*.mp4 *.wmv *.mov *.avi *.mkv *.m4v *.webm")])
        if not args.video:
            sys.exit("no video chosen")
    if not args.audio:
        args.audio = pick_file("Step 2 of 2: choose your SOUND",
                               [("Audio", " ".join("*" + e for e in sorted(AUDIO_EXTENSIONS)))])
        if not args.audio:
            sys.exit("no sound chosen")

    video, audio = Path(args.video), Path(args.audio)
    # Dragging two files onto the script passes them in any order.
    if video.suffix.lower() in AUDIO_EXTENSIONS and audio.suffix.lower() not in AUDIO_EXTENSIONS:
        video, audio = audio, video
    for p in (video, audio):
        if not p.is_file():
            sys.exit(f"error: {p} not found")

    output = Path(args.output) if args.output else video.with_name(f"{video.stem}_with_audio.mp4")
    if output.exists() and not args.overwrite and not args.output:
        output = free_name(output)
    if output.exists() and not args.overwrite:
        sys.exit(f"error: {output} already exists (use --overwrite)")

    try:
        duration = float(probe(video, "format=duration")[0])
    except (IndexError, ValueError):
        sys.exit(f"error: could not read the length of {video}")
    video_codec = (probe(video, "stream=codec_name", "v:0") or [""])[0]
    video_has_audio = bool(probe(video, "stream=index", "a"))

    # Build the audio filter: volume -> optional fade -> optional mix with original.
    chain = f"[1:a]volume={args.volume}"
    if args.fade_out > 0:
        start = max(0.0, duration - args.fade_out)
        chain += f",afade=t=out:st={start:.3f}:d={args.fade_out}"
    if args.keep_original and video_has_audio:
        chain += "[new];[0:a][new]amix=inputs=2:duration=first:normalize=0"
    elif args.keep_original:
        print("note: the video has no sound of its own, so only your audio is used")
    chain += "[aout]"

    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-stats",
        "-y" if args.overwrite else "-n",
        "-i", str(video),
        "-stream_loop", "-1", "-i", str(audio),  # repeat the audio forever...
        "-filter_complex", chain,
        "-map", "0:v:0", "-map", "[aout]",
        "-t", f"{duration:.3f}",                  # ...and stop at the video's length
    ]
    if video_codec in COPYABLE_VIDEO:
        cmd += ["-c:v", "copy"]
    else:
        cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "23", "-pix_fmt", "yuv420p",
                "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2"]
    cmd += ["-c:a", "aac", "-b:a", args.audio_bitrate, "-movflags", "+faststart", str(output)]

    print(f"{video} + {audio} -> {output} ({duration:.1f}s)")
    if subprocess.run(cmd).returncode != 0:
        sys.exit("error: ffmpeg failed")
    print("done")


def run():
    pause = len(sys.argv) == 1 or launched_from_explorer()
    code = 0
    try:
        main()
    except SystemExit as e:
        if isinstance(e.code, str):
            print(e.code, file=sys.stderr)
            code = 1
        else:
            code = e.code or 0
    except KeyboardInterrupt:
        code = 1
    except Exception:
        import traceback
        traceback.print_exc()
        code = 1
    if pause:
        input("\nPress Enter to close...")
    sys.exit(code)


if __name__ == "__main__":
    run()
