#!/usr/bin/env python3
"""Show which codecs a video or audio file uses, and where it will play.

Easiest: double-click this file and pick one or more files in the window that
opens, or drag files (or a folder) onto it.

From a terminal:
    python3 codec_checker.py video.mp4
    python3 codec_checker.py a.wmv b.mp4 song.mp3
    python3 codec_checker.py videos/           # every media file in a folder

Requires ffprobe (comes with ffmpeg) on PATH (https://ffmpeg.org/download.html).
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

MEDIA_EXTENSIONS = {
    ".mp4", ".m4v", ".mov", ".wmv", ".avi", ".mkv", ".webm", ".flv", ".mpg", ".mpeg",
    ".ts", ".m2ts", ".3gp", ".ogv", ".asf",
    ".mp3", ".wav", ".m4a", ".aac", ".ogg", ".oga", ".flac", ".wma", ".opus",
}

FRIENDLY_NAMES = {
    "h264": "H.264 / AVC", "hevc": "H.265 / HEVC", "av1": "AV1", "vp8": "VP8", "vp9": "VP9",
    "mpeg4": "MPEG-4 Part 2 (DivX/Xvid)", "mpeg2video": "MPEG-2", "mpeg1video": "MPEG-1",
    "wmv1": "Windows Media Video 7", "wmv2": "Windows Media Video 8",
    "wmv3": "Windows Media Video 9", "vc1": "VC-1", "prores": "Apple ProRes",
    "aac": "AAC", "mp3": "MP3", "opus": "Opus", "vorbis": "Vorbis", "flac": "FLAC",
    "ac3": "Dolby Digital (AC-3)", "eac3": "Dolby Digital Plus (E-AC-3)", "alac": "Apple Lossless",
    "wmav1": "Windows Media Audio 1", "wmav2": "Windows Media Audio 2", "wmapro": "WMA Pro",
    "pcm_s16le": "PCM (uncompressed WAV)", "pcm_s24le": "PCM 24-bit (uncompressed WAV)",
}

# Codecs that play almost everywhere: phones, all browsers, TVs, Windows, Mac.
UNIVERSAL_VIDEO = {"h264"}
UNIVERSAL_AUDIO = {"aac", "mp3", "pcm_s16le"}
UNIVERSAL_CONTAINERS = {".mp4", ".m4v", ".m4a", ".mp3", ".wav"}


def launched_from_explorer():
    """True when Windows opened a fresh console for us (double-click or drag-and-drop)."""
    return os.name == "nt" and "PROMPT" not in os.environ


def pick_files():
    """Ask for files with a file-picker window, or by typing a path if that's unavailable."""
    try:
        import tkinter
        from tkinter import filedialog
        root = tkinter.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        files = filedialog.askopenfilenames(
            title="Choose video or audio file(s) to check",
            filetypes=[("Media files", " ".join("*" + e for e in sorted(MEDIA_EXTENSIONS))),
                       ("All files", "*.*")])
        root.destroy()
        return list(files)
    except Exception:
        path = input("Drag a file (or folder) here and press Enter: ").strip().strip('"')
        return [path] if path else []


def find_inputs(paths):
    files = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            files.extend(f for f in sorted(p.iterdir()) if f.is_file() and f.suffix.lower() in MEDIA_EXTENSIONS)
        elif p.is_file():
            files.append(p)
        else:
            print(f"skip: {p} not found", file=sys.stderr)
    return files


def friendly(codec):
    return FRIENDLY_NAMES.get(codec, codec or "unknown")


def human_size(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.1f} {unit}" if unit != "B" else f"{n} B"
        n /= 1024


def human_time(seconds):
    seconds = int(round(seconds))
    h, rest = divmod(seconds, 3600)
    m, s = divmod(rest, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def kbps(value):
    try:
        return f"{int(value) // 1000} kb/s"
    except (TypeError, ValueError):
        return None


def fps(rate):
    try:
        num, den = rate.split("/")
        value = float(num) / float(den)
        return f"{value:.3f}".rstrip("0").rstrip(".") + " fps"
    except (AttributeError, ValueError, ZeroDivisionError):
        return None


def check(path):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)],
        capture_output=True, text=True)
    print("=" * 60)
    print(path.name)
    print("=" * 60)
    if result.returncode != 0:
        print("  Could not read this file - it may be damaged or not a media file.")
        print(f"  ({result.stderr.strip().splitlines()[-1] if result.stderr.strip() else 'unknown error'})")
        return

    info = json.loads(result.stdout)
    fmt = info.get("format", {})
    streams = info.get("streams", [])
    videos = [s for s in streams if s.get("codec_type") == "video"
              and not s.get("disposition", {}).get("attached_pic")]
    audios = [s for s in streams if s.get("codec_type") == "audio"]
    subs = [s for s in streams if s.get("codec_type") == "subtitle"]

    container = fmt.get("format_long_name", fmt.get("format_name", "unknown"))
    if "mp4" in fmt.get("format_name", "") and path.suffix.lower() in {".mp4", ".m4v", ".m4a"}:
        container = "MPEG-4 (MP4)"
    print(f"  Container : {container}")
    if fmt.get("duration"):
        print(f"  Length    : {human_time(float(fmt['duration']))}")
    print(f"  Size      : {human_size(path.stat().st_size)}")
    if kbps(fmt.get("bit_rate")):
        print(f"  Bitrate   : {kbps(fmt.get('bit_rate'))}")

    for i, v in enumerate(videos, 1):
        label = "Video" if len(videos) == 1 else f"Video {i}"
        details = [f"{v.get('width')}x{v.get('height')}" if v.get("width") else None,
                   fps(v.get("avg_frame_rate")), v.get("profile"), v.get("pix_fmt"),
                   kbps(v.get("bit_rate"))]
        print(f"  {label:<10}: {friendly(v.get('codec_name'))}  ({', '.join(d for d in details if d)})")
    if not videos and not audios:
        print("  No video or audio streams found.")
    elif not videos and path.suffix.lower() not in {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".oga",
                                                     ".flac", ".wma", ".opus"}:
        print("  Video     : none")

    for i, a in enumerate(audios, 1):
        label = "Audio" if len(audios) == 1 else f"Audio {i}"
        channels = {1: "mono", 2: "stereo", 6: "5.1", 8: "7.1"}.get(a.get("channels"), f"{a.get('channels')} ch")
        rate = f"{int(a['sample_rate']) / 1000:g} kHz" if a.get("sample_rate") else None
        lang = a.get("tags", {}).get("language")
        details = [channels, rate, kbps(a.get("bit_rate")), lang if lang and lang != "und" else None]
        print(f"  {label:<10}: {friendly(a.get('codec_name'))}  ({', '.join(d for d in details if d)})")
    if videos and not audios:
        print("  Audio     : none (silent video)")
    if subs:
        print(f"  Subtitles : {len(subs)} track(s)")

    # Verdict
    vcodecs = {v.get("codec_name") for v in videos}
    acodecs = {a.get("codec_name") for a in audios}
    container_ok = path.suffix.lower() in UNIVERSAL_CONTAINERS
    problems = []
    if vcodecs - UNIVERSAL_VIDEO:
        problems.append(f"video codec {', '.join(friendly(c) for c in vcodecs - UNIVERSAL_VIDEO)}")
    if acodecs - UNIVERSAL_AUDIO:
        problems.append(f"audio codec {', '.join(friendly(c) for c in acodecs - UNIVERSAL_AUDIO)}")
    if not container_ok:
        problems.append(f"{path.suffix.lower() or 'unknown'} file type")
    if any(v.get("pix_fmt") not in (None, "yuv420p", "yuvj420p") for v in videos if v.get("codec_name") == "h264"):
        problems.append("unusual colour format (not yuv420p)")

    print()
    if not problems:
        print("  OK: plays almost everywhere (phones, browsers, Windows, Mac, TVs).")
    else:
        print(f"  May not play everywhere because of: {'; '.join(problems)}.")
        if videos:
            print("  Tip: convert to MP4 (H.264 + AAC, yuv420p) for the widest support,")
            print("       e.g. with wmv_to_mp4.py for WMV files.")
        else:
            print("  Tip: MP3 or AAC (.m4a) audio plays almost everywhere.")


def main():
    parser = argparse.ArgumentParser(description="Show the codecs used by video/audio files.")
    parser.add_argument("inputs", nargs="*", help="media files and/or folders containing them")
    args = parser.parse_args()

    if shutil.which("ffprobe") is None:
        sys.exit("error: ffprobe not found on PATH. Install ffmpeg from https://ffmpeg.org/download.html")

    if not args.inputs:
        args.inputs = pick_files()
        if not args.inputs:
            sys.exit("no files chosen")

    files = find_inputs(args.inputs)
    if not files:
        sys.exit("error: no media files found")
    for f in files:
        check(f)
        print()


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
