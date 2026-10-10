#!/usr/bin/env python3
"""Convert MKV videos to MP4, or other videos to MKV.

  MKV -> MP4: video and audio are copied without re-encoding when MP4 supports
              them (fast, no quality loss); anything else is converted. All audio
              tracks (languages) and text subtitles are kept.
  other -> MKV: everything is copied as-is (MKV can hold any codec), so it's
              almost instant and lossless.

The direction is picked automatically from the file type: .mkv files become
.mp4, everything else becomes .mkv. Use --to mp4 / --to mkv to force it.

Easiest: double-click this file and pick your video(s), or drag videos (or a
folder) onto it.

From a terminal:
    python3 mkv_converter.py movie.mkv              # -> movie.mp4
    python3 mkv_converter.py clip.mp4               # -> clip.mkv
    python3 mkv_converter.py shows/ -o converted/   # every video in a folder

Requires ffmpeg and ffprobe on PATH (https://ffmpeg.org/download.html).
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

VIDEO_EXTENSIONS = {".mkv", ".mp4", ".m4v", ".mov", ".wmv", ".avi", ".webm", ".flv", ".mpg",
                    ".mpeg", ".ts", ".m2ts", ".3gp", ".ogv", ".asf"}

# What MP4 can hold as-is (and that plays widely).
MP4_VIDEO_COPY = {"h264", "hevc", "av1", "mpeg4"}
MP4_AUDIO_COPY = {"aac", "mp3", "ac3", "eac3", "alac"}
MP4_TEXT_SUBS = {"subrip", "ass", "ssa", "mov_text", "webvtt", "text"}


def launched_from_explorer():
    """True when Windows opened a fresh console for us (double-click or drag-and-drop)."""
    return os.name == "nt" and "PROMPT" not in os.environ


def pick_files():
    """Ask for videos with a file-picker window, or by typing a path if that's unavailable."""
    try:
        import tkinter
        from tkinter import filedialog
        root = tkinter.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        files = filedialog.askopenfilenames(
            title="Choose video(s): MKV files become MP4, others become MKV",
            filetypes=[("MKV videos", "*.mkv *.MKV"),
                       ("All videos", " ".join("*" + e for e in sorted(VIDEO_EXTENSIONS))),
                       ("All files", "*.*")])
        root.destroy()
        return list(files)
    except Exception:
        path = input("Drag a video (or folder) here and press Enter: ").strip().strip('"')
        return [path] if path else []


def find_inputs(paths):
    files = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            files.extend(f for f in sorted(p.iterdir()) if f.is_file() and f.suffix.lower() in VIDEO_EXTENSIONS)
        elif p.is_file():
            files.append(p)
        else:
            print(f"skip: {p} not found", file=sys.stderr)
    return files


def free_name(path):
    """path, or path with (2), (3), ... added if it already exists."""
    n = 2
    candidate = path
    while candidate.exists():
        candidate = path.with_name(f"{path.stem} ({n}){path.suffix}")
        n += 1
    return candidate


def streams_of(path):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-of", "json", str(path)],
                            capture_output=True, text=True)
    if result.returncode != 0:
        return None
    return json.loads(result.stdout).get("streams", [])


def mp4_command(src, dst, streams, crf, audio_bitrate):
    """Build an ffmpeg command for MKV (or anything) -> MP4, copying what MP4 supports."""
    videos = [s for s in streams if s["codec_type"] == "video"
              and not s.get("disposition", {}).get("attached_pic")]
    audios = [s for s in streams if s["codec_type"] == "audio"]
    subs = [s for s in streams if s["codec_type"] == "subtitle"]

    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-stats", "-n", "-i", str(src)]
    notes = []

    if videos:
        v = videos[0]
        cmd += ["-map", f"0:{v['index']}"]
        if v.get("codec_name") in MP4_VIDEO_COPY:
            cmd += ["-c:v", "copy"]
            if v.get("codec_name") == "hevc":
                cmd += ["-tag:v", "hvc1"]  # so Apple devices recognise it
        else:
            notes.append(f"video {v.get('codec_name')} -> H.264 (re-encoding, this takes a while)")
            cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", str(crf), "-pix_fmt", "yuv420p",
                    "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2"]

    for out_i, a in enumerate(audios):
        cmd += ["-map", f"0:{a['index']}"]
        if a.get("codec_name") in MP4_AUDIO_COPY:
            cmd += [f"-c:a:{out_i}", "copy"]
        else:
            notes.append(f"audio track {out_i + 1} {a.get('codec_name')} -> AAC")
            cmd += [f"-c:a:{out_i}", "aac", f"-b:a:{out_i}", audio_bitrate]

    kept_subs = [s for s in subs if s.get("codec_name") in MP4_TEXT_SUBS]
    dropped = len(subs) - len(kept_subs)
    for s in kept_subs:
        cmd += ["-map", f"0:{s['index']}"]
    if kept_subs:
        cmd += ["-c:s", "mov_text"]
    if dropped:
        notes.append(f"{dropped} picture-based subtitle track(s) dropped (MP4 can't hold them)")

    cmd += ["-movflags", "+faststart", str(dst)]
    return cmd, notes


def mkv_command(src, dst):
    """Anything -> MKV: copy every stream untouched."""
    return ["ffmpeg", "-hide_banner", "-loglevel", "error", "-stats", "-n", "-i", str(src),
            "-map", "0", "-c", "copy", str(dst)], []


def main():
    parser = argparse.ArgumentParser(description="Convert MKV to MP4, or other videos to MKV.")
    parser.add_argument("inputs", nargs="*", help="video files and/or folders containing them")
    parser.add_argument("--to", choices=["mp4", "mkv"],
                        help="output type (default: .mkv files -> mp4, everything else -> mkv)")
    parser.add_argument("-o", "--out-dir", help="output folder (default: next to each input)")
    parser.add_argument("--crf", type=int, default=23,
                        help="quality if video must be re-encoded, lower = better (default 23)")
    parser.add_argument("--audio-bitrate", default="192k", help="bitrate if audio must be re-encoded (default 192k)")
    args = parser.parse_args()

    for tool in ("ffmpeg", "ffprobe"):
        if shutil.which(tool) is None:
            sys.exit(f"error: {tool} not found on PATH. Install ffmpeg from https://ffmpeg.org/download.html")

    if not args.inputs:
        args.inputs = pick_files()
        if not args.inputs:
            sys.exit("no files chosen")
    files = find_inputs(args.inputs)
    if not files:
        sys.exit("error: no video files found")

    failed = []
    for i, src in enumerate(files, 1):
        target = args.to or ("mp4" if src.suffix.lower() == ".mkv" else "mkv")
        if src.suffix.lower() == f".{target}":
            print(f"[{i}/{len(files)}] skip {src.name}: already .{target}")
            continue
        streams = streams_of(src)
        if streams is None:
            print(f"[{i}/{len(files)}] skip {src.name}: can't read it (damaged or not a video?)")
            failed.append(src)
            continue

        out_dir = Path(args.out_dir) if args.out_dir else src.parent
        out_dir.mkdir(parents=True, exist_ok=True)
        dst = free_name(out_dir / f"{src.stem}.{target}")
        if target == "mp4":
            cmd, notes = mp4_command(src, dst, streams, args.crf, args.audio_bitrate)
        else:
            cmd, notes = mkv_command(src, dst)

        print(f"[{i}/{len(files)}] {src.name} -> {dst.name}")
        for note in notes:
            print(f"      {note}")
        if subprocess.run(cmd).returncode != 0:
            failed.append(src)
            dst.unlink(missing_ok=True)

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
