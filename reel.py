"""Cut the vertical invitation reel.

The page is a page: it scrolls, it has room, and its plates sit in whatever
shape each one was drawn for. A reel is none of that. It is 1080x1920, it is
watched with a thumb hovering, and every source here is 16:9 — so filling the
frame would mean cropping to a third of the width and throwing the composition
away. The two shots that matter most are two people side by side, which is
exactly the picture a 9:16 crop destroys.

So the reel does not crop to fill. It puts each clip on the page's own ground as
a plate, edges dissolved into the black the way `.plate-ink` does, and sets the
type in the space that leaves. That is what the site looks like anyway. It also
means nothing is ever enlarged past 1080 from a 1280 source, where a full-bleed
9:16 would have been working from 405.

    python3 reel.py                 the whole thing
    python3 reel.py --stills        one frame per beat, to look at before waiting

Two files come out: `reel.mp4` with the page's music under it, and
`reel-silent.mp4` without. Post the silent one and add music inside Instagram —
their licence covers their library, and a track uploaded in the file is what
gets muted.
"""

import argparse
import glob
import math
import os
import random
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import place

W, H = 1080, 1920
FPS = 24
DISSOLVE = 0.5                      # seconds of cross-dissolve between beats

INK = (10, 8, 6)                    # --ink, the page's ground
BONE = (235, 220, 192)              # --bone
BONE_SOFT = (196, 178, 150)
MUTED = (156, 139, 112)
GOLD = (217, 164, 65)

SRC = "art-source"
FONTS = "fonts"

# One plate shape for every beat: 3:2, cut from the middle of the 16:9 source at
# 1080 wide — which is the source's own pixels, neither enlarged nor reduced.
# It keeps x 100..1180 of the 1280, so both of them stay in the two-shots (his
# face ends at 530, hers begins at 700). Cropping to fill the 9:16 frame would
# have meant 405 of the 1280 and one of them out of shot.
#
# Keeping it the same in all six beats is deliberate. The variety is in the
# clips; a layout that changes shape every three seconds reads as a template
# rather than as one piece.
PLATE = dict(w=1080, h=720, crop="1080:720", top=660)

# Instagram covers roughly the top 250px and everything below about 1450 with
# its own interface. Type is bottom-aligned above the plate, inside that.
TYPE_BASELINE = 600


def ffmpeg():
    found = shutil.which("ffmpeg")
    if found:
        return found
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


_FONTDIR = None


def prepare_fonts(work):
    """`fonts/` holds what the page serves, which is woff2, and PIL reads
    TrueType. Rather than keeping a second copy of every face in the repo just
    for this, unpack the ones this needs into the work directory — the reel is
    then guaranteed to be set in the same files the site is."""
    global _FONTDIR
    _FONTDIR = os.path.join(work, "fonts")
    os.makedirs(_FONTDIR, exist_ok=True)
    from fontTools.ttLib.woff2 import decompress
    for name in {s[0] for s in STYLES.values()}:
        dst = os.path.join(_FONTDIR, name)
        src = os.path.join(FONTS, name)
        if os.path.exists(src):
            shutil.copy(src, dst)                       # diablo ships as ttf
        else:
            decompress(os.path.join(FONTS, name.replace(".ttf", ".woff2")), dst)


def font(name, size):
    return ImageFont.truetype(os.path.join(_FONTDIR, name), size)


# Each beat is one idea. The text is only what is actually known: the ceremony
# venue is not on the invitation yet, so it is not in here either.
BEATS = [
    dict(clip="eclipse", at=1.0, secs=3.8,
         grade=(0.62, 1.10, 0.94), delay=1.0,
         text=[("Join us for the wedding of", "join"),
               ("Marc-Kevin", "name"), ("&", "amp"), ("Florence", "name")]),

    # Their actual rings, which are made. The blue the script glows is the one
    # colour in the whole reel that fights the page, so this keeps less of
    # itself than the beats either side: at keep 0.42 the inscription reads gold
    # against the band and only the arc above it stays cold, which is what it is
    # meant to be. Pulled further than that and the energy goes out of it.
    dict(clip="rings", at=6.4, secs=3.5,
         grade=(0.42, 1.16, 0.92), delay=0.8,
         text=[("the rings are made", "hand")]),

    dict(clip="seal", at=2.2, secs=3.6,
         grade=(0.38, 1.20, 0.86), delay=0.5,
         text=[("ON", "eyebrow"), ("October 07, 2026", "head"),
               ("a Wednesday", "hand")]),

    # Started late enough that the push has brought the table forward: at the
    # very top of that generation the two of them are fifty pixels across.
    dict(clip="hall", at=0.9, secs=3.6,
         grade=(0.34, 1.24, 0.84), delay=0.5,
         # Five o'clock is the reception's, not the ceremony's, so it is set
         # here rather than on the date beat.
         text=[("THE RECEPTION, FIVE O'CLOCK", "eyebrow"),
               ("Smoque Bistro", "head"),
               ("Carlos P. Garcia East Avenue", "hand"),
               ("Tagbilaran City, Bohol", "hand")]),

    dict(clip="candles", at=0.5, secs=3.4,
         grade=(0.50, 1.15, 0.92), delay=0.5,
         text=[("WHAT TO WEAR", "eyebrow"), ("Black and burgundy", "head")]),

    # The tail, where the push has settled and their faces are 260px across.
    # No type over it: this is the one beat that is about looking at them.
    dict(clip="ridge-close", at=6.9, secs=4.0,
         grade=(0.58, 1.12, 0.92), delay=0.0, text=[]),

    dict(clip=None, secs=3.0, grade=None, delay=0.4, card=True, text=[]),
]

# name, size, tracking (as a fraction of size), colour, space after.
# Sized so the tallest block — the four lines of the opening — still clears
# SAFE_TOP when it is bottom-aligned on TYPE_BASELINE. Making the names bigger
# means moving the baseline down, not letting them run off the top.
STYLES = {
    "join":    ("CormorantGaramond-300-italic.ttf", 40, 0.02, MUTED, 18),
    "name":    ("diablo.ttf", 92, 0.045, BONE, 4),
    "amp":     ("CormorantGaramond-300-italic.ttf", 44, 0.0, GOLD, 4),
    "eyebrow": ("Cinzel-400-normal.ttf", 30, 0.32, MUTED, 30),
    "head":    ("diablo.ttf", 76, 0.045, BONE, 22),
    "hand":    ("CormorantGaramond-300-italic.ttf", 42, 0.02, BONE_SOFT, 10),
}

SAFE_TOP = 250


def tracked_width(text, fnt, track):
    """PIL has no letter-spacing, so every tracked line is drawn a glyph at a
    time and its width has to be added up the same way."""
    return (sum(fnt.getlength(c) for c in text)
            + track * (len(text) - 1) if text else 0)


def draw_tracked(img, cx, y, text, fnt, track, fill, glow=None):
    """One line, centred on cx, letter by letter.

    `glow` paints the same line first into a blurred pass underneath — the names
    on the page carry a warm text-shadow, and without it type this size sits on
    the black looking pasted on rather than lit by the same fire as the plate.
    """
    from PIL import ImageFilter
    total = tracked_width(text, fnt, track)
    if glow:
        halo = Image.new("RGBA", img.size, (0, 0, 0, 0))
        hd = ImageDraw.Draw(halo)
        x = cx - total / 2.0
        for c in text:
            hd.text((x, y), c, font=fnt, fill=glow)
            x += fnt.getlength(c) + track
        img.alpha_composite(halo.filter(ImageFilter.GaussianBlur(22)))
    d = ImageDraw.Draw(img)
    x = cx - total / 2.0
    for c in text:
        d.text((x, y), c, font=fnt, fill=fill)
        x += fnt.getlength(c) + track


def end_card():
    """The last beat has no clip, so it is built rather than decoded: the Brand
    off the gate, struck and bleeding, over the address of the site."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    brand = Image.open(os.path.join("img", "brand.webp")).convert("RGBA")
    bw = 300
    brand = brand.resize((bw, int(brand.height * bw / float(brand.width))),
                         Image.LANCZOS)
    layer.alpha_composite(brand, ((W - bw) // 2, 620))

    name, size, track_frac, colour, _ = STYLES["head"]
    draw_tracked(layer, W / 2.0, 1320, "marcandflo.com", font(name, size),
                 size * track_frac, colour + (255,), (232, 162, 58, 70))
    return layer


def type_layer(lines):
    """All of a beat's text, drawn once onto its own transparent layer so the
    per-frame cost of fading it in is one composite rather than a re-render.

    Bottom-aligned on TYPE_BASELINE rather than run downwards from a top edge:
    beats carry one line or four, and growing upwards keeps the last line — the
    one nearest the picture — in the same place every time.
    """
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    steps = [(t, s, STYLES[s][1] * 1.18 + STYLES[s][4]) for t, s in lines]
    y = TYPE_BASELINE - sum(s[2] for s in steps)
    if y < SAFE_TOP:
        print("          block starts at y=%d, above the %d Instagram covers — "
              "%r" % (y, SAFE_TOP, lines[0][0]))
    for text, style, advance in steps:
        name, size, track_frac, colour, gap = STYLES[style]
        fnt = font(name, size)
        glow = (232, 162, 58, 70) if name == "diablo.ttf" else None
        draw_tracked(layer, W / 2.0, y, text, fnt, size * track_frac,
                     colour + (255,), glow)
        y += advance
    return layer


def ground():
    """The page's ink, with the faint warm lift the artwork canvas gives it."""
    g = Image.new("RGB", (W, H), INK)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W * 0.95)) ** 2 + ((yy - H * 0.42) / (H * 0.62)) ** 2)
    lift = np.clip(1.0 - r, 0, 1) ** 2.2
    a = np.asarray(g, dtype=np.float32)
    for i, c in enumerate((44, 26, 12)):
        a[:, :, i] += lift * c
    return Image.fromarray(np.clip(a, 0, 255).astype("uint8"))


def plate_mask(w, h):
    """The dissolve that puts a plate on the page instead of over it.

    The site's plates fade their edges into the ground with a radial gradient
    rather than sitting on it as rectangles, and at this size against this much
    black a hard edge is the first thing the eye finds. Same idea here, as a
    radius falling away from the middle — the first version ramped the axes
    independently over 6% and 16%, which left the corners lit and the straight
    runs between them reading as an edge anyway.
    """
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.sqrt(((xx - (w - 1) / 2.0) / (w * 0.72)) ** 2 +
                ((yy - (h - 1) / 2.0) / (h * 0.74)) ** 2)
    m = np.clip(1.0 - (r - 0.38) / 0.56, 0, 1) ** 1.6
    return Image.fromarray((m * 255).astype("uint8"), "L")


def backdrop(frame, base):
    """The same frame, blown up past the edges and blurred, under the plate.

    Six sharp bands on flat black is a slideshow. This gives every beat its own
    colour across the whole 1080x1920 — red under the eclipse, candle gold under
    the candles — without inventing any detail, since none of it is in focus. It
    is also where the bottom third of the frame goes, which Instagram covers
    with its own interface anyway.
    """
    from PIL import ImageFilter
    # Built at an eighth and blown back up. A 56px gaussian over 1080x1920 is
    # most of a second per frame and there are five hundred of them; a 7px one
    # over 135x240 is instant, and after the enlargement the two are the same
    # picture — the blur has already thrown away everything the small version
    # cannot hold. Same reasoning as the page's half-resolution fog buffer.
    # Stretched to the frame rather than cropped to cover it. A cover crop of a
    # 3:2 plate into 9:16 keeps only the middle third of its width, which throws
    # away the lantern light at the edges — the exact colour this layer exists
    # to carry. Nothing here is in focus, so the distortion has nothing to show.
    small = frame.resize((W // 8, H // 8), Image.BILINEAR).filter(ImageFilter.GaussianBlur(7))
    # How much of it shows depends on how bright it is. A fixed blend suits the
    # dark beats and fails the ridge, whose overcast sky came through as a pale
    # wash across the top of the frame — brighter than the plate it was meant to
    # sit behind. Capped on the backdrop's own mean, so each beat lands in the
    # same place instead of being dialled in one at a time.
    lum = float(np.asarray(small.convert("L"), dtype=np.float32).mean())
    k = 0.34 * min(1.0, 42.0 / max(lum, 1.0))
    return Image.blend(base, small.resize((W, H), Image.BICUBIC), k)


def embers(n=54, seed=7):
    """Warm motes drifting up, one layer across the whole reel rather than per
    beat — running through the dissolves is most of what makes six cuts read as
    one piece."""
    rng = random.Random(seed)
    S = 46
    sprite = Image.new("L", (S, S), 0)
    sd = ImageDraw.Draw(sprite)
    for i in range(S // 2, 0, -1):
        sd.ellipse([S / 2 - i, S / 2 - i, S / 2 + i, S / 2 + i],
                   fill=int(255 * (1 - i / (S / 2.0)) ** 2.4))
    return sprite, [dict(x=rng.uniform(0, W), y=rng.uniform(0, H),
                         v=rng.uniform(12, 46), r=rng.uniform(1.6, 5.2),
                         a=rng.uniform(0.10, 0.34), ph=rng.uniform(0, 6.3))
                    for _ in range(n)]


def draw_embers(img, sprite, motes, t):
    layer = Image.new("L", (W, H), 0)
    for m in motes:
        y = (m["y"] - m["v"] * t) % (H + 120) - 60
        x = m["x"] + math.sin(t * 0.5 + m["ph"]) * 26
        d = int(m["r"] * 7)
        s = sprite.resize((d, d), Image.BILINEAR).point(lambda v, a=m["a"]: int(v * a))
        layer.paste(s, (int(x - d / 2), int(y - d / 2)), s)
    warm = Image.new("RGB", (W, H), (226, 150, 58))
    return Image.composite(Image.blend(img, warm, 0.55), img, layer)


def render_beat(i, beat, work, full_text=False):
    """One beat's frames, complete but for the embers."""
    n = int(round(beat["secs"] * FPS))
    out = os.path.join(work, "b%d" % i)
    os.makedirs(out, exist_ok=True)

    base = ground()
    layer = (end_card() if beat.get("card") else
             type_layer(beat["text"]) if beat["text"] else None)

    frames = []
    if beat["clip"]:
        cw = PLATE["crop"].split(":")[0]
        chain = ["crop=%s:(iw-%s)/2:(ih-%s)/2" % (PLATE["crop"], cw,
                                                  PLATE["crop"].split(":")[1]),
                 "scale=%d:%d" % (PLATE["w"], PLATE["h"])]
        dec = os.path.join(work, "dec%d" % i)
        shutil.rmtree(dec, ignore_errors=True)
        os.makedirs(dec)
        subprocess.run([ffmpeg(), "-v", "error", "-y", "-ss", str(beat["at"]),
                        "-t", str(beat["secs"] + 0.3), "-i",
                        os.path.join(SRC, beat["clip"] + "-clip.mp4"),
                        "-vf", ",".join(chain), "-q:v", "2",
                        os.path.join(dec, "%04d.png")], check=True)
        frames = sorted(glob.glob(os.path.join(dec, "*.png")))
        if not frames:
            sys.exit("no frames from %s at %ss" % (beat["clip"], beat["at"]))
        mask = plate_mask(PLATE["w"], PLATE["h"])

    keep, contrast, bright = beat["grade"] or (1.0, 1.0, 1.0)
    from PIL import ImageEnhance
    for f in range(n):
        im = base
        if frames:
            p = Image.open(frames[min(f, len(frames) - 1)]).convert("RGB")
            p = place.to_palette(p, keep)
            p = ImageEnhance.Contrast(p).enhance(contrast)
            p = ImageEnhance.Brightness(p).enhance(bright)
            im = backdrop(p, base)
            im.paste(p, (0, PLATE["top"]), mask)
        else:
            im = base.copy()
        if layer is not None:
            t = f / float(FPS)
            k = 1.0 if full_text else (
                min(1.0, max(0.0, (t - beat["delay"]) / 0.9))
                * min(1.0, max(0.0, (beat["secs"] - t) / 0.5)))
            if k > 0:
                im = Image.alpha_composite(im.convert("RGBA"),
                                           _fade(layer, k)).convert("RGB")
        im.save(os.path.join(out, "%04d.png" % f))
    return [os.path.join(out, "%04d.png" % f) for f in range(n)]


def _fade(layer, k):
    r, g, b, a = layer.split()
    return Image.merge("RGBA", (r, g, b, a.point(lambda v: int(v * k))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", action="store_true",
                    help="one frame per beat and stop — the fast way to judge "
                         "type and framing before rendering five hundred")
    ap.add_argument("--out", default="art-source")
    ap.add_argument("--work", default="_reelwork")
    args = ap.parse_args()

    shutil.rmtree(args.work, ignore_errors=True)
    os.makedirs(args.work)
    prepare_fonts(args.work)

    if args.stills:
        for i, b in enumerate(BEATS):
            # Halfway through the beat, with the type at full opacity: the frame
            # to judge, rather than one caught mid-fade.
            probe = dict(b, secs=2.0 / FPS, at=b.get("at", 0) + b["secs"] / 2.0)
            fs = render_beat(i, probe, args.work, full_text=True)
            shutil.copy(fs[-1], os.path.join(args.work, "still%d.png" % i))
            print("still%d.png  %s" % (i, b["clip"] or "end card"))
        return

    per = [render_beat(i, b, args.work) for i, b in enumerate(BEATS)]
    for i, fs in enumerate(per):
        print("beat %d  %-12s %3d frames" % (i, BEATS[i]["clip"] or "end card", len(fs)))
    assemble(per, args.work, args.out)


def assemble(per, work, out):
    d = int(round(DISSOLVE * FPS))
    starts, t = [], 0
    for fs in per:
        starts.append(t)
        t += len(fs) - d
    total = t + d
    print("assembling %d frames (%.1fs)" % (total, total / float(FPS)))

    final = os.path.join(work, "final")
    os.makedirs(final)
    sprite, motes = embers()
    for j in range(total):
        cur = None
        for i, fs in enumerate(per):
            k = j - starts[i]
            if 0 <= k < len(fs):
                im = Image.open(fs[k]).convert("RGB")
                # Inside the overlap both beats are live; the later one comes up
                # as the earlier one goes, so the join is a dissolve rather than
                # a cut on black.
                cur = im if cur is None else Image.blend(cur, im, min(1.0, (k + 1) / float(d)))
        cur = draw_embers(cur, sprite, motes, j / float(FPS))
        cur.save(os.path.join(final, "%04d.png" % j))

    src = os.path.join(final, "%04d.png")
    silent = os.path.join(out, "reel-silent.mp4")
    scored = os.path.join(out, "reel.mp4")
    v = ["-c:v", "libx264", "-preset", "slow", "-crf", "19", "-pix_fmt", "yuv420p",
         "-profile:v", "high", "-movflags", "+faststart"]
    subprocess.run([ffmpeg(), "-v", "error", "-y", "-framerate", str(FPS),
                    "-i", src] + v + [silent], check=True)

    bed = "audio/theme.m4a"
    if os.path.exists(bed):
        subprocess.run([ffmpeg(), "-v", "error", "-y", "-framerate", str(FPS),
                        "-i", src, "-i", bed] + v +
                       ["-af", "afade=t=out:st=%.2f:d=1.5,volume=0.8"
                        % (total / float(FPS) - 1.5),
                        "-c:a", "aac", "-b:a", "128k", "-ar", "48000",
                        "-shortest", scored], check=True)

    for p in (silent, scored):
        if os.path.exists(p):
            print("%-28s %6d KB" % (p, os.path.getsize(p) // 1024))
    shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
