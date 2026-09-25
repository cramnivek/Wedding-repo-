"""Prepare the four commissioned plates for the page.

Each one gets only the treatment it actually needs, which differs per image:

  battlefield  already ink on a warm ground — it only needs the paper border
               trimmed and the top cropped away, because the page draws its own
               eclipse behind the names and two suns in one view is a mess.
  hall         the outlier. Blue stone and cool mist, a colour the page never
               uses, so its luminance is mapped through the page's own ramp with
               a good share of the original left in — enough to kill the blue,
               not so much that the candlelight goes with it.
  garments     ink already, on cream paper. Border trimmed, ground darkened so
               the paper stops glowing against a near-black page.
  hands        already black-ground line art. Nothing but a resize.

Run from the scratchpad once the files are in ./incoming/.
"""

from PIL import Image, ImageEnhance
import os
import sys

SRC = "incoming"
OUT = "img"

# The page's own tokens, as a luminance ramp: ink, warm shadow, bone, ember.
RAMP_STOPS = [
    (0.00, (5, 5, 7)),
    (0.16, (22, 15, 10)),
    (0.34, (66, 44, 24)),
    (0.46, (112, 74, 32)),
    (0.70, (190, 136, 56)),
    (0.88, (238, 198, 116)),
    (1.00, (255, 243, 212)),
]


def build_ramp():
    ramp = []
    for i in range(256):
        t = i / 255
        for j in range(len(RAMP_STOPS) - 1):
            a, ca = RAMP_STOPS[j]
            b, cb = RAMP_STOPS[j + 1]
            if a <= t <= b:
                k = (t - a) / (b - a)
                ramp.append(tuple(round(ca[c] + (cb[c] - ca[c]) * k) for c in range(3)))
                break
        else:
            ramp.append(RAMP_STOPS[-1][1])
    return ramp


RAMP = build_ramp()


def to_palette(im, keep):
    """Map luminance through the page ramp, blending `keep` of the original back
    so it reads as a treated drawing rather than a flat two-colour poster."""
    lum = im.convert("L")
    duo = Image.merge("RGB", [lum.point([RAMP[i][c] for i in range(256)]) for c in range(3)])
    return Image.blend(duo, im, keep)


def trim_border(im, frac):
    """These renders come with a paper margin around the plate. Crop it off."""
    w, h = im.size
    dx, dy = round(w * frac), round(h * frac)
    return im.crop((dx, dy, w - dx, h - dy))


JOBS = [
    # name         border  crop_top  palette_keep  contrast  bright  longest
    ("battlefield", 0.030, 0.28,     0.34,         1.24,     0.86,  1800),
    # hall's row still grades the ink drawing in art-source/, but the plate the
    # page ships is no longer that drawing: clip.py --still now writes hall.jpg
    # out of the banquet clip's own first frame, using these same numbers, so
    # the still and the video are the same picture. Running place.py would put
    # the drawing back and the clip would swap in over a different scene.
    ("hall",        0.010, 0.0,      0.30,         1.26,     0.80,  1180),
    ("garments",    0.008, 0.0,      0.40,         1.22,     0.68,   800),
    ("hands",       0.0,   0.0,      0.45,         1.16,     0.96,   640),
    ("them-ink",    0.0,   0.0,      0.34,         1.22,     0.86,   780),

    # The prenup set: same ramp, each pulled by however much its own light needs.
    ("vow",         0.0,   0.0,      0.34,         1.26,     0.96,   860),
    ("camp",        0.0,   0.0,      0.32,         1.26,     0.92,  1180),
    ("ridge",       0.0,   0.0,      0.24,         1.30,     0.80,   780),
    ("knight",      0.0,   0.0,      0.28,         1.30,     0.86,   780),
    ("walk",        0.0,   0.0,      0.28,         1.30,     0.84,  1800),

    # The black-sun scene arrives with a red eclipse and a grey sky. Pulled hard
    # through the ramp so the corona lands on the page's gold instead of fighting
    # it, and darkened so the plate's mask can dissolve its edges into the page.
    ("sun",         0.0,   0.0,      0.26,         1.28,     0.84,   860),

    # Already crimson and near-black before it got here — it was generated into
    # the palette rather than corrected into it — so it keeps most of itself and
    # only gets nudged. Grading this one hard would flatten the wet armour, which
    # is most of why it works.
    ("rescue",      0.0,   0.0,      0.55,         1.12,     0.9,  1000),

    # The chamber portrait is the one render where the faces read as themselves,
    # so it keeps most of its own light — grading it as hard as the rest would
    # cost the likeness, which is the only reason it is on the page.
    ("chamber",     0.0,   0.0,      0.58,         1.10,     0.94,   780),

    # The two real photographs keep most of themselves — they are the one place
    # the page is not a painted world, and over-grading them loses the contrast
    # that section is built on.
    ("us-1",        0.0,   0.0,      0.62,         1.12,     0.92,   780),
    ("us-2",        0.0,   0.0,      0.62,         1.12,     0.92,   780),
]


def find(name):
    for f in sorted(os.listdir(SRC)):
        if f.lower().startswith(name):
            return os.path.join(SRC, f)
    return None


def main():
    os.makedirs(OUT, exist_ok=True)
    missing = []
    for name, border, crop_top, keep, contrast, bright, longest in JOBS:
        path = find(name)
        if not path:
            missing.append(name)
            continue
        im = Image.open(path).convert("RGB")
        before = im.size
        if border:
            im = trim_border(im, border)
        if crop_top:
            w, h = im.size
            im = im.crop((0, round(h * crop_top), w, h))
        if keep is not None:
            im = to_palette(im, keep)
        im = ImageEnhance.Contrast(im).enhance(contrast)
        im = ImageEnhance.Brightness(im).enhance(bright)
        sc = longest / max(im.size)
        if sc < 1:
            im = im.resize((round(im.size[0] * sc), round(im.size[1] * sc)), Image.LANCZOS)
        dst = os.path.join(OUT, name + ".jpg")
        im.save(dst, "JPEG", quality=82, optimize=True, progressive=True)
        print(f"{dst:22} {before[0]}x{before[1]} -> {im.size[0]}x{im.size[1]}  "
              f"{os.path.getsize(dst) // 1024} KB")
    if missing:
        print("\nnot found in ./%s/: %s" % (SRC, ", ".join(missing)), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
