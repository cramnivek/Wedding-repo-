"""Turn a generated clip into a plate the page can play.

A video dropped in raw looks wrong next to the stills in two ways: it carries
its own colour rather than the page's, and it arrives at whatever size the
generator felt like. This does the same three things every time:

  1. cuts the watermark, crops to the shape the plate is actually rendered in,
     and scales to twice the widest CSS size the page ever gives it
  2. grades every frame through place.py's own ramp, using the same row from
     its JOBS table that graded the still — without this the colour visibly
     shifts at the moment the video swaps in for the picture
  3. encodes H.264 and VP9 at the same base name, because "every browser plays
     mp4" is not true and a Chromium built without the proprietary codecs
     decodes neither the file nor the reason it failed

Usage:

    python3 clip.py chamber incoming/chamber.mp4 --crop 720:720:230:0
    python3 clip.py vow     incoming/vow.mp4     --crop 720:720:280:0
    python3 clip.py ridge   incoming/ridge.mp4                 # no crop needed

Then add data-clip="img/<plate>" to that plate's <figure> and run
check/clip.cjs. The script prints the avc1 codec string at the end: if it
differs from the one in the page's <source type>, change the page, or a browser
without H.264 will download the mp4 before discovering it cannot play it.
"""

import argparse
import glob
import os
import shutil
import subprocess
import sys
import time

from PIL import Image, ImageEnhance

import place

# Twice the widest CSS width the page ever renders each plate at, measured by
# check/maxsize.cjs. Re-run it after a layout change rather than trusting these.
TARGETS = {
    "battlefield": 3200, "camp": 1152, "chamber": 748, "garments": 768,
    "hall": 1152, "hands": 608, "knight": 748, "rescue": 960, "ridge": 748,
    "sun": 832, "them-ink": 748, "us-1": 748, "us-2": 748, "vow": 832,
    "walk": 3200,
}

# Where the generator burns its sparkle, in source pixels. Same spot in every
# clip that has come back so far; check a frame before trusting it on a new one.
WATERMARK = "x=1134:y=573:w=52:h=54"


def ffmpeg():
    """Prefer a system ffmpeg; fall back to the one imageio ships, which is how
    this runs in a container with no ffmpeg of its own."""
    found = shutil.which("ffmpeg")
    if found:
        return found
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def grading(plate):
    """Pull the plate's own row out of place.py, so a clip is graded with
    exactly what graded the still it replaces."""
    for row in place.JOBS:
        if row[0] == plate:
            name, border, crop_top, keep, contrast, bright, longest = row
            return keep, contrast, bright
    sys.exit("no row for %r in place.py's JOBS" % plate)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plate", help="plate name, as it appears in place.py's JOBS")
    ap.add_argument("source", help="the generated clip")
    ap.add_argument("--crop", help="ffmpeg crop as W:H:X:Y, in source pixels — "
                                   "use it to match the shape the plate renders in")
    ap.add_argument("--delogo", action="store_true",
                    help="paint out the watermark. Unnecessary when --crop "
                         "already excludes it, which is usually cheaper")
    ap.add_argument("--size", type=int, help="override the measured target width")
    ap.add_argument("--out", default="img", help="where the encodes land")
    args = ap.parse_args()

    ff = ffmpeg()
    keep, contrast, bright = grading(args.plate)
    target = args.size or TARGETS.get(args.plate)
    if not target:
        sys.exit("no measured target for %r — pass --size" % args.plate)

    # delogo before crop: its coordinates are in source pixels, and cropping
    # first would move the mark out from under the box.
    chain = []
    if args.delogo:
        chain.append("delogo=" + WATERMARK)
    if args.crop:
        chain.append("crop=" + args.crop)
    # min() so a source already narrower than the target is left alone rather
    # than upscaled — enlarging a crop invents nothing and costs bytes. -2 keeps
    # the other axis even, which H.264 requires.
    chain.append("scale='min(%d,iw)':-2" % target)

    work = os.path.join(os.path.dirname(os.path.abspath(args.source)) or ".",
                        "_clipwork_" + args.plate)
    if os.path.isdir(work):
        shutil.rmtree(work)
    os.makedirs(work)

    print("decoding  %s" % ",".join(chain))
    subprocess.run([ff, "-v", "error", "-y", "-i", args.source,
                    "-vf", ",".join(chain), "-q:v", "2",
                    os.path.join(work, "%04d.png")], check=True)

    frames = sorted(glob.glob(os.path.join(work, "*.png")))
    if not frames:
        sys.exit("no frames came out — check the crop is inside the source")
    print("grading   %d frames at keep=%s contrast=%s bright=%s"
          % (len(frames), keep, contrast, bright))
    t0 = time.time()
    for f in frames:
        im = Image.open(f).convert("RGB")
        im = place.to_palette(im, keep)
        im = ImageEnhance.Contrast(im).enhance(contrast)
        im = ImageEnhance.Brightness(im).enhance(bright)
        im.save(f)
    print("          %.1fs" % (time.time() - t0))

    os.makedirs(args.out, exist_ok=True)
    mp4 = os.path.join(args.out, args.plate + ".mp4")
    webm = os.path.join(args.out, args.plate + ".webm")
    src = os.path.join(work, "%04d.png")

    # No audio track on either: the page synthesises its own sound at the gate
    # and a second source would fight it.
    print("encoding  h264")
    subprocess.run([ff, "-v", "error", "-y", "-framerate", "24", "-i", src,
                    "-c:v", "libx264", "-preset", "slow", "-crf", "30",
                    "-pix_fmt", "yuv420p", "-movflags", "+faststart", mp4], check=True)
    print("encoding  vp9")
    subprocess.run([ff, "-v", "error", "-y", "-framerate", "24", "-i", src,
                    "-c:v", "libvpx-vp9", "-crf", "48", "-b:v", "0",
                    "-row-mt", "1", "-deadline", "good", "-cpu-used", "2",
                    webm], check=True)

    shutil.rmtree(work)

    # The page names the codec in each <source type>, not just the container,
    # so that a browser without H.264 skips the mp4 instead of downloading it
    # to find out. Read the real string back out of the avcC box.
    data = open(mp4, "rb").read()
    i = data.find(b"avcC")
    codec = "avc1.%02X%02X%02X" % (data[i + 5], data[i + 6], data[i + 7])

    for path in (mp4, webm):
        print("%-28s %6d KB" % (path, os.path.getsize(path) // 1024))
    print('\ncodec: %s — the page must carry codecs="%s" on its mp4 <source>'
          % (codec, codec))
    print('add    data-clip="img/%s" to that plate\'s <figure>, then run check/clip.cjs'
          % args.plate)


if __name__ == "__main__":
    main()
