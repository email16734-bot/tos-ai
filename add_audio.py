#!/usr/bin/env python3
"""Put your own sound on a video using ffmpeg.

The new audio always ends exactly when the video ends:
  - audio shorter than the video -> it loops until the video is over
  - audio longer than the video  -> it is cut off at the end of the video

Usage:
    python3 add_audio.py video.mp4 music.mp3                  # -> video_with_audio.mp4
    python3 add_audio.py video.wmv music.wav -o final.mp4
    python3 add_audio.py video.mp4 music.mp3 --keep-original  # mix with the video's own sound
    python3 add_audio.py video.mp4 music.mp3 --volume 0.5 --fade-out 2

Requires ffmpeg and ffprobe on PATH (https://ffmpeg.org/download.html).
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

# Video codecs that can be copied into an .mp4 untouched (fast, no quality loss).
COPYABLE_VIDEO = {"h264", "hevc", "mpeg4", "av1"}


def probe(path, entries, stream=None):
    cmd = ["ffprobe", "-v", "error"]
    if stream:
        cmd += ["-select_streams", stream]
    cmd += ["-show_entries", entries, "-of", "default=noprint_wrappers=1:nokey=1", str(path)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip().splitlines()


def main():
    parser = argparse.ArgumentParser(description="Add (and loop) your own audio on a video.")
    parser.add_argument("video", help="input video (mp4, wmv, mov, avi, mkv, ...)")
    parser.add_argument("audio", help="your sound (mp3, wav, m4a, ogg, ...)")
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

    video, audio = Path(args.video), Path(args.audio)
    for p in (video, audio):
        if not p.is_file():
            sys.exit(f"error: {p} not found")

    output = Path(args.output) if args.output else video.with_name(f"{video.stem}_with_audio.mp4")
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


if __name__ == "__main__":
    main()
