"""Turn an audio file into the page's music bed.

    python3 music.py theme.mp3

Writes audio/theme.m4a and audio/theme.ogg. The page fetches exactly one of
them — whichever its browser says it can decode — and only once the seal is
broken, so neither is in the cold load.

Three things it does that matter:

  loudness   Normalised to -18 LUFS, which is quiet. This plays under a page
             nobody opened for the music; a track at its mastered level arrives
             like a shout. The volume the page sets on top of this is a further
             cut, not a correction for a file that is too loud.

  trim       Silence at either end is cut, because the file loops. A second of
             room tone at the end is a second of nothing every time round.

  fade       A short fade at the head and tail, so the wrap is a dip rather than
             a click. Audio is less forgiving than video here: a discontinuity
             in a waveform is an audible pop, not a soft cut.

The result is mono unless --stereo is passed. Nobody is listening to a wedding
page in headphones for the imaging, and mono is most of the file size back.
"""

import argparse
import os
import shutil
import subprocess
import sys


def ffmpeg():
    found = shutil.which("ffmpeg")
    if found:
        return found
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def duration(ff, path):
    out = subprocess.run([ff, "-hide_banner", "-i", path],
                         capture_output=True, text=True).stderr
    for line in out.splitlines():
        if "Duration:" in line:
            hms = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = hms.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", help="the audio file to use")
    ap.add_argument("--name", default="theme", help="output base name")
    ap.add_argument("--out", default="audio", help="where the encodes land")
    ap.add_argument("--lufs", type=float, default=-18.0,
                    help="target loudness; lower is quieter (default -18)")
    ap.add_argument("--stereo", action="store_true", help="keep both channels")
    ap.add_argument("--kbps", type=int, default=72,
                    help="AAC bitrate (default 72 mono / use ~112 for stereo)")
    ap.add_argument("--fade", type=float, default=0.6,
                    help="seconds of fade at each end, for the loop join")
    args = ap.parse_args()

    ff = ffmpeg()
    if not os.path.exists(args.source):
        sys.exit("no such file: " + args.source)

    dur = duration(ff, args.source)
    if not dur:
        sys.exit("could not read a duration out of that file")

    # silenceremove trims the head; reversing to trim the tail is the usual
    # trick, since the filter only ever works forwards.
    chain = [
        "silenceremove=start_periods=1:start_silence=0.1:start_threshold=-50dB",
        "areverse",
        "silenceremove=start_periods=1:start_silence=0.1:start_threshold=-50dB",
        "areverse",
        "loudnorm=I=%.1f:TP=-2.0:LRA=11" % args.lufs,
        "afade=t=in:st=0:d=%.2f" % args.fade,
        # the tail fade is placed from the end, so it needs the trimmed length;
        # close enough to use the source's, since only silence was removed
        "afade=t=out:st=%.2f:d=%.2f" % (max(0, dur - args.fade), args.fade),
    ]
    if not args.stereo:
        chain.insert(0, "pan=mono|c0=0.5*c0+0.5*c1")

    os.makedirs(args.out, exist_ok=True)
    m4a = os.path.join(args.out, args.name + ".m4a")
    ogg = os.path.join(args.out, args.name + ".ogg")
    af = ",".join(chain)

    print("encoding  aac %dk" % args.kbps)
    subprocess.run([ff, "-v", "error", "-y", "-i", args.source, "-vn",
                    "-af", af, "-c:a", "aac", "-b:a", "%dk" % args.kbps,
                    "-movflags", "+faststart", m4a], check=True)

    print("encoding  opus %dk" % max(48, args.kbps - 16))
    subprocess.run([ff, "-v", "error", "-y", "-i", args.source, "-vn",
                    "-af", af, "-c:a", "libopus",
                    "-b:a", "%dk" % max(48, args.kbps - 16), ogg], check=True)

    for p in (m4a, ogg):
        print("%-24s %6d KB  %5.1fs" % (p, os.path.getsize(p) // 1024,
                                        duration(ff, p) or 0))
    print("\nthe page looks for audio/%s — nothing else to change" % args.name)


if __name__ == "__main__":
    main()
