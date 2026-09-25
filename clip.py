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

A generation is rarely one usable shot end to end. --trim takes the span that
is, and --unpush cancels a camera move inside it so --loop has the locked-off
shot its crossfade assumes:

    python3 clip.py hall incoming/banquet.mp4 --trim 0:3 --unpush --delogo --loop 0.7

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

import numpy as np
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


def measure_zoom(a, b, lo, hi, step=0.004, size=(256, 144)):
    """How far `a` must be zoomed about its centre to land on `b`'s framing.

    Brute force, because there are only ever a few hundred candidates and the
    alternative is phase correlation for an answer that does not need to be
    better than half a percent. Compared at thumbnail size: the frames differ in
    their content as well as their framing — people move between them — and
    throwing away detail is what stops that content difference from drowning out
    the framing difference the search is actually looking for.

    Returns (scale, residual). The residual is not an error bar; it is dominated
    by whatever moved. Read the scale curve for smoothness instead.
    """
    W, H = a.size
    t = np.asarray(b.resize(size, Image.BILINEAR), dtype=np.float32)
    best = (lo, 1e9)
    s = lo
    while s < hi:
        w, h = W / s, H / s
        box = ((W - w) / 2.0, (H - h) / 2.0, (W + w) / 2.0, (H + h) / 2.0)
        c = np.asarray(a.resize(size, Image.BILINEAR, box=box), dtype=np.float32)
        e = np.abs(c - t).mean()
        if e < best[1]:
            best = (s, e)
        s += step
    return best


def unpush(frames, target):
    """Cancel a camera push, leaving a locked-off shot.

    clip.py's crossfade assumes the camera matches at both ends of the clip —
    every plate on the page so far was a locked-off shot, so it did. A clip that
    zooms breaks that assumption: dissolving its tail over its head blends two
    different framings, which reads as a soft double exposure rather than a
    loop, and without the dissolve the wrap is a visible snap back to wide.

    So measure what the camera did and undo it. Each frame is matched against
    the last one to find how much wider it is, then cropped by exactly that much
    and scaled back out. Everything ends up on the last frame's framing, which
    is the only one that can be reached without inventing pixels — a push can
    be cancelled by throwing resolution away at the wide end, never by zooming
    out past the edge of the frame at the tight end.

    The cost is that the opening frames are the most cropped, so the segment fed
    in should be short enough that the push has not travelled far. Beyond about
    1.25x the earliest frames are being enlarged enough to see.
    """
    n = len(frames)
    last = Image.open(frames[-1]).convert("RGB")
    W, H = last.size

    # Walk backwards from the end, searching a window around the previous
    # answer: the push is continuous, so frame i-1 is a little wider than frame
    # i and never suddenly anything else. Starting each search from the last
    # result keeps this a few dozen candidates per frame instead of a few
    # hundred, and stops a frame whose content changed a lot from jumping to a
    # wild scale that the frames either side contradict.
    zoom = [1.0] * n
    prev = 1.0
    for i in range(n - 2, -1, -1):
        im = Image.open(frames[i]).convert("RGB")
        s, _ = measure_zoom(im, last, lo=max(1.0, prev - 0.01), hi=prev + 0.06)
        zoom[i] = prev = s

    span = zoom[0]
    print("unpush    camera travelled x%.3f across %d frames; "
          "widest frame loses %.0f%% of its width" % (span, n, (1 - 1 / span) * 100))
    if span > 1.30:
        print("          that is a lot — check the first frames for softness")

    out_w = min(target, int(round(W / span)) if span > 1 else W)
    for i, path in enumerate(frames):
        im = Image.open(path).convert("RGB")
        w, h = W / zoom[i], H / zoom[i]
        box = ((W - w) / 2.0, (H - h) / 2.0, (W + w) / 2.0, (H + h) / 2.0)
        out_h = int(round(out_w * h / w)) // 2 * 2
        im.resize((out_w, out_h), Image.LANCZOS, box=box).save(path)
    print("          stabilised to %dx%d" % (out_w, out_h))


def crossfade(frames, seconds, fps=24):
    """Make the clip loop without a visible cut, in place.

    These are locked-off shots, so the camera matches at both ends, but what is
    moving does not: measured across the four on the page, the last frame and
    the first differ by enough that a plain `loop` attribute shows a hard jump
    every time round.

    The fix is to dissolve the tail over the head. The output is the clip minus
    its last `seconds`, where those opening seconds have had the discarded tail
    faded out across them — so the frame after the last is the frame that
    already followed it, and the join is continuous rather than blended away.

    The alternative was a palindrome, which is seamless by construction and
    needs no blending at all, but it plays the second half backwards: fire
    un-flickers and embers fall back down into the flame. Motion here stays
    physically forward, and the dissolve lands on smoke, flame and breath, which
    are the most forgiving things to dissolve there are.
    """
    n = len(frames)
    f = min(int(round(seconds * fps)), n // 3)
    if f < 2:
        return
    print("looping   dissolving %d frames of tail over the head" % f)

    tail = [Image.open(frames[n - f + i]).convert("RGB") for i in range(f)]
    for i in range(f):
        head = Image.open(frames[i]).convert("RGB")
        # i/f, so the first output frame is pure tail — continuous with the
        # frame that precedes it once the clip wraps — and the last is pure head.
        Image.blend(tail[i], head, i / float(f)).save(frames[i])

    for path in frames[n - f:]:
        os.remove(path)
    del frames[n - f:]


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
    ap.add_argument("--trim", metavar="START:LENGTH",
                    help="use only this span of the source, in seconds — e.g. "
                         "0:3 for the first three. A ten-second generation is "
                         "rarely ten seconds of one shot")
    ap.add_argument("--unpush", action="store_true",
                    help="cancel a camera push so the shot ends up locked off. "
                         "Needed before --loop on anything that moves the "
                         "camera, which a crossfade cannot hide")
    ap.add_argument("--still", action="store_true",
                    help="also write the plate's .jpg/.webp/.avif from the "
                         "clip's own first frame, so the two cannot drift")
    ap.add_argument("--loop", nargs="?", const=1.0, type=float, metavar="SECONDS",
                    help="make it loop seamlessly by cross-dissolving the tail "
                         "over the head (default 1s). Costs that much length")
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
    #
    # unpush does its own scaling, and needs every pixel the source has while it
    # works: it crops the wide frames down, so decoding to the target first
    # would mean cropping an already-reduced frame and enlarging the remainder.
    if not args.unpush:
        chain.append("scale='min(%d,iw)':-2" % target)

    # -ss and -t before -i so ffmpeg seeks rather than decoding and discarding.
    span = []
    if args.trim:
        start, length = args.trim.split(":")
        span = ["-ss", start, "-t", length]

    work = os.path.join(os.path.dirname(os.path.abspath(args.source)) or ".",
                        "_clipwork_" + args.plate)
    if os.path.isdir(work):
        shutil.rmtree(work)
    os.makedirs(work)

    print("decoding  %s%s" % (("%s +%ss  " % (span[1], span[3])) if span else "",
                              ",".join(chain)))
    subprocess.run([ff, "-v", "error", "-y"] + span + ["-i", args.source,
                    "-vf", ",".join(chain), "-q:v", "2",
                    os.path.join(work, "%04d.png")], check=True)

    frames = sorted(glob.glob(os.path.join(work, "*.png")))
    if not frames:
        sys.exit("no frames came out — check the crop is inside the source")

    # Before grading, so the measurement runs on the source's own contrast
    # rather than on a version already crushed toward the page's palette.
    if args.unpush:
        unpush(frames, target)

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

    if args.loop:
        crossfade(frames, args.loop)

    os.makedirs(args.out, exist_ok=True)

    if args.still:
        # The still and the clip have to be the same picture, or the swap shows.
        # Matching them by grading a separate render with the same numbers gets
        # close; taking the still out of the clip's own first frame makes them
        # identical by construction, which is the only version that is invisible.
        # This is also the only way to put a clip where no matching still exists.
        im = Image.open(frames[0]).convert("RGB")
        for ext, kw in (("jpg", dict(quality=82, optimize=True, progressive=True)),
                        ("webp", dict(quality=80, method=6)),
                        ("avif", dict(quality=62))):
            p = os.path.join(args.out, args.plate + "." + ext)
            im.save(p, **kw)
            print("still     %-22s %6d KB" % (p, os.path.getsize(p) // 1024))
        print("          the page must carry width=\"%d\" height=\"%d\" on this "
              "plate's <img>" % im.size)
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
