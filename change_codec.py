#!/usr/bin/env python3
"""Re-encode videos to a different codec: H.264, H.265/HEVC, VP9 or AV1.

Easiest: double-click this file, pick your video(s), then type the number of
the codec you want. Or drag videos (or a folder) onto it.

From a terminal:
    python3 change_codec.py video.mkv                    # -> video_h264.mp4
    python3 change_codec.py video.mp4 --codec h265       # smaller file, same quality
    python3 change_codec.py videos/ --codec vp9 -o out/  # every video in a folder
    python3 change_codec.py video.avi --crf 18           # higher quality

Requires ffmpeg and ffprobe on PATH (https://ffmpeg.org/download.html).
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

VIDEO_EXTENSIONS = {".mp4", ".m4v", ".mov", ".wmv", ".avi", ".mkv", ".webm", ".flv", ".mpg",
                    ".mpeg", ".ts", ".m2ts", ".3gp", ".ogv", ".asf"}

# name -> settings. "crf" is the default quality (lower = better and bigger).
CODECS = {
    "h264": {
        "label": "H.264 / AVC   - plays everywhere (recommended)",
        "probe_names": {"h264"}, "ext": ".mp4", "crf": 23,
        "encoders": [("libx264", ["-preset", "medium"])],
        "extra": ["-pix_fmt", "yuv420p"],
    },
    "h265": {
        "label": "H.265 / HEVC  - about half the size, newer devices only",
        "probe_names": {"hevc"}, "ext": ".mp4", "crf": 28,
        "encoders": [("libx265", ["-preset", "medium"])],
        "extra": ["-pix_fmt", "yuv420p", "-tag:v", "hvc1"],  # hvc1 tag so Apple devices play it
    },
    "vp9": {
        "label": "VP9           - for the web / YouTube, saved as .webm",
        "probe_names": {"vp9"}, "ext": ".webm", "crf": 31,
        "encoders": [("libvpx-vp9", ["-b:v", "0", "-row-mt", "1", "-deadline", "good", "-cpu-used", "2"])],
        "extra": ["-pix_fmt", "yuv420p"],
    },
    "av1": {
        "label": "AV1           - smallest files, slow to encode, newest devices",
        "probe_names": {"av1"}, "ext": ".mp4", "crf": 35,
        "encoders": [("libsvtav1", ["-preset", "8"]),
                     ("libaom-av1", ["-cpu-used", "6", "-row-mt", "1", "-b:v", "0"])],
        "extra": ["-pix_fmt", "yuv420p"],
    },
}

# Audio codecs that can be copied into each output container without re-encoding.
COPYABLE_AUDIO = {".mp4": {"aac", "mp3", "ac3", "eac3", "alac"}, ".webm": {"opus", "vorbis"}}


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
            title="Choose video(s) to re-encode",
            filetypes=[("Videos", " ".join("*" + e for e in sorted(VIDEO_EXTENSIONS))), ("All files", "*.*")])
        root.destroy()
        return list(files)
    except Exception:
        path = input("Drag a video (or folder) here and press Enter: ").strip().strip('"')
        return [path] if path else []


def ask_codec():
    names = list(CODECS)
    print("Which codec do you want?")
    for i, name in enumerate(names, 1):
        print(f"  {i}) {CODECS[name]['label']}")
    while True:
        answer = input("Type a number and press Enter (just Enter = 1): ").strip().lower()
        if not answer:
            return names[0]
        if answer.isdigit() and 1 <= int(answer) <= len(names):
            return names[int(answer) - 1]
        if answer in CODECS:
            return answer
        print("  Please type one of the numbers above.")


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


def probe(path, entries, stream):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", stream, "-show_entries", entries,
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True)
    return result.stdout.strip().splitlines()


def available_encoder(codec):
    listing = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True).stdout
    names = {line.split()[1] for line in listing.splitlines() if len(line.split()) > 1}
    for encoder, options in CODECS[codec]["encoders"]:
        if encoder in names:
            return encoder, options
    return None, None


def convert(src, dst, codec, encoder, options, crf, audio_bitrate):
    settings = CODECS[codec]
    audio_codecs = probe(src, "stream=codec_name", "a")
    if not audio_codecs:
        audio = []
    elif all(a in COPYABLE_AUDIO[settings["ext"]] for a in audio_codecs):
        audio = ["-c:a", "copy"]
    elif settings["ext"] == ".webm":
        audio = ["-c:a", "libopus", "-b:a", audio_bitrate]
    else:
        audio = ["-c:a", "aac", "-b:a", audio_bitrate]

    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-stats", "-n",
        "-i", str(src),
        "-map", "0:v:0", "-map", "0:a?",
        "-c:v", encoder, *options, "-crf", str(crf), *settings["extra"],
        # yuv420p needs even width and height
        "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
        *audio,
    ]
    if settings["ext"] == ".mp4":
        cmd += ["-movflags", "+faststart"]
    cmd.append(str(dst))
    return subprocess.run(cmd).returncode == 0


def main():
    parser = argparse.ArgumentParser(description="Re-encode videos to another codec.")
    parser.add_argument("inputs", nargs="*", help="video files and/or folders containing them")
    parser.add_argument("-c", "--codec", choices=list(CODECS), help="target codec (default: h264)")
    parser.add_argument("-o", "--out-dir", help="output folder (default: next to each input)")
    parser.add_argument("--crf", type=int, help="quality, lower = better and bigger "
                        "(defaults: h264 23, h265 28, vp9 31, av1 35)")
    parser.add_argument("--audio-bitrate", default="192k", help="bitrate if audio must be re-encoded (default 192k)")
    parser.add_argument("--force", action="store_true", help="re-encode even if a video already uses that codec")
    args = parser.parse_args()

    for tool in ("ffmpeg", "ffprobe"):
        if shutil.which(tool) is None:
            sys.exit(f"error: {tool} not found on PATH. Install ffmpeg from https://ffmpeg.org/download.html")

    interactive = not args.inputs
    if interactive:
        args.inputs = pick_files()
        if not args.inputs:
            sys.exit("no files chosen")
    files = find_inputs(args.inputs)
    if not files:
        sys.exit("error: no video files found")

    if args.codec is None:
        args.codec = ask_codec() if interactive or launched_from_explorer() else "h264"
    settings = CODECS[args.codec]
    crf = args.crf if args.crf is not None else settings["crf"]

    encoder, options = available_encoder(args.codec)
    if encoder is None:
        wanted = " or ".join(e for e, _ in settings["encoders"])
        sys.exit(f"error: your ffmpeg can't encode {args.codec} (needs {wanted}). "
                 "Install a full ffmpeg build from https://ffmpeg.org/download.html")

    print(f"\nEncoding to {args.codec} with {encoder}, quality (crf) {crf}\n")
    failed = []
    for i, src in enumerate(files, 1):
        current = (probe(src, "stream=codec_name", "v:0") or ["none"])[0]
        if current in settings["probe_names"] and not args.force:
            print(f"[{i}/{len(files)}] skip {src.name}: already {args.codec} (use --force to re-encode anyway)")
            continue
        out_dir = Path(args.out_dir) if args.out_dir else src.parent
        out_dir.mkdir(parents=True, exist_ok=True)
        dst = free_name(out_dir / f"{src.stem}_{args.codec}{settings['ext']}")
        print(f"[{i}/{len(files)}] {src.name} ({current}) -> {dst.name}")
        if not convert(src, dst, args.codec, encoder, options, crf, args.audio_bitrate):
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
