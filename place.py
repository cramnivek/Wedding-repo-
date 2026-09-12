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
    (0.00, (7, 7, 10)),
    (0.32, (38, 28, 22)),
    (0.60, (122, 106, 86)),
    (0.84, (198, 182, 150)),
    (1.00, (243, 219, 170)),
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
    ("battlefield", 0.030, 0.28,     None,         1.08,     0.80,   1800),
    ("hall",        0.010, 0.0,      0.42,         1.12,     0.72,   1500),
    ("garments",    0.008, 0.0,      0.5,          1.10,     0.60,   1100),
    ("hands",       0.0,   0.0,      None,         1.02,     0.94,   1100),
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
