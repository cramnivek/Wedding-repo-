# fonts

`diablo.woff2` / `diablo.woff` / `diablo.ttf` — **Diablo Heavy**, MaGiK
Enterprises, dated 1-23-97 in its own version string. A fan-made face cut in the
shape of the Diablo logo: barred `T`, slashed `O`, slashed zero. Not Exocet,
which is what the games themselves used.

It has no true lowercase. Lowercase input selects alternate capital forms — that
is what puts the slashed `O` in FLORENCE and the wide `M` in MARC-KEVIN — so the
names are written in mixed case on purpose. It cannot set a heading, a label or
body text, and the page only ever uses it for the names.

`diablo.woff2` (15KB) is what loads; the `.woff` is the fallback for browsers too
old for woff2, and the `.ttf` is the original the other two were converted from.


## The Google faces

`Allura-*`, `Cinzel-*` and `CormorantGaramond-*` are the latin subsets of the
three text faces, downloaded from Google Fonts and served from here instead of
from `fonts.googleapis.com`. Google's own stylesheet declares 44 faces across
cyrillic, vietnamese and latin-ext as well; this page is English with Filipino
place names, so the other 33 would never render a glyph.

They are all under the SIL Open Font License, which permits redistribution
alongside the page. A face is still only fetched when something matches it — the
page pulls 7 of the 11 in practice; the rest are declared so that a browser
matching weights differently still finds one.

To refresh them, take the `css2?family=...` URL out of the page's history, fetch
it with a modern browser's user agent, keep the `/* latin */` blocks and
download what they point at.
