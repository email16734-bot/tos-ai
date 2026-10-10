#!/usr/bin/env python3
"""Convert WMV videos to MP4 (H.264 + AAC) using ffmpeg.

Easiest: double-click this file and pick your .wmv files in the window that
opens, or drag .wmv files (or a folder) onto it.

From a terminal:
    python3 wmv_to_mp4.py input.wmv                 # -> input.mp4 next to it
    python3 wmv_to_mp4.py videos/ -o converted/     # every .wmv in a folder
    python3 wmv_to_mp4.py a.wmv b.wmv --crf 20 --preset slow --overwrite

Requires ffmpeg on PATH (https://ffmpeg.org/download.html).
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def launched_from_explorer():
    """True when Windows opened a fresh console for us (double-click or drag-and-drop)."""
    return os.name == "nt" and "PROMPT" not in os.environ


def pick_files():
    """Ask for .wmv files with a file-picker window, or by typing paths if that's unavailable."""
    try:
        import tkinter
        from tkinter import filedialog
        root = tkinter.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        files = filedialog.askopenfilenames(
            title="Choose WMV video(s) to convert",
            filetypes=[("WMV videos", "*.wmv *.WMV"), ("All files", "*.*")])
        root.destroy()
        return list(files)
    except Exception:
        path = input("Drag a .wmv file (or folder) here and press Enter: ").strip().strip('"')
        return [path] if path else []


def find_inputs(paths, recursive):
    files = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            pattern = "**/*" if recursive else "*"
            files.extend(f for f in sorted(p.glob(pattern)) if f.is_file() and f.suffix.lower() == ".wmv")
        elif p.is_file():
            files.append(p)
        else:
            print(f"skip: {p} not found", file=sys.stderr)
    return files


def output_path(src, out_dir, base_dir):
    if out_dir is None:
        return src.with_suffix(".mp4")
    rel = src.relative_to(base_dir) if base_dir and src.is_relative_to(base_dir) else Path(src.name)
    return Path(out_dir) / rel.with_suffix(".mp4")


def convert(src, dst, crf, preset, audio_bitrate, overwrite):
    dst.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-stats",
        "-y" if overwrite else "-n",
        "-i", str(src),
        "-map", "0:v:0?", "-map", "0:a?",
        "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
        "-pix_fmt", "yuv420p",
        # libx264 with yuv420p needs even dimensions
        "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
        "-c:a", "aac", "-b:a", audio_bitrate,
        "-movflags", "+faststart",
        str(dst),
    ]
    return subprocess.run(cmd).returncode == 0


def main():
    parser = argparse.ArgumentParser(description="Convert WMV files to MP4.")
    parser.add_argument("inputs", nargs="*", help=".wmv files and/or folders containing them")
    parser.add_argument("-o", "--out-dir", help="output folder (default: next to each input)")
    parser.add_argument("-r", "--recursive", action="store_true", help="search folders recursively")
    parser.add_argument("--crf", type=int, default=23, help="quality, 0-51, lower = better (default 23)")
    parser.add_argument("--preset", default="medium",
                        help="x264 speed/size preset: ultrafast..veryslow (default medium)")
    parser.add_argument("--audio-bitrate", default="192k", help="AAC bitrate (default 192k)")
    parser.add_argument("--overwrite", action="store_true", help="replace existing .mp4 files")
    args = parser.parse_args()

    if shutil.which("ffmpeg") is None:
        sys.exit("error: ffmpeg not found on PATH. Install it from https://ffmpeg.org/download.html")

    if not args.inputs:
        args.inputs = pick_files()
        if not args.inputs:
            sys.exit("no files chosen")

    files = find_inputs(args.inputs, args.recursive)
    if not files:
        sys.exit("error: no .wmv files found")

    base_dir = Path(args.inputs[0]) if len(args.inputs) == 1 and Path(args.inputs[0]).is_dir() else None
    failed = []
    for i, src in enumerate(files, 1):
        dst = output_path(src, args.out_dir, base_dir)
        if dst.exists() and not args.overwrite:
            print(f"[{i}/{len(files)}] skip {src} ({dst} exists, use --overwrite)")
            continue
        print(f"[{i}/{len(files)}] {src} -> {dst}")
        if not convert(src, dst, args.crf, args.preset, args.audio_bitrate, args.overwrite):
            failed.append(src)

    if failed:
        print(f"\n{len(failed)} file(s) failed:", file=sys.stderr)
        for f in failed:
            print(f"  {f}", file=sys.stderr)
        sys.exit(1)
    print("\ndone")


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
