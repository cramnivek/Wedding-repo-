#!/bin/sh
# Assemble the servable site into dist/.
#
# The repository is not the website. art-source/ alone is 70MB of ungraded
# originals and full-size clips — nine times the size of the site itself — and
# check/, place.py and clip.py are tooling. Pointing a host at the repository
# root publishes all of it. Point it at dist/ instead.
#
#   sh build.sh                            then publish dist/
#   sh build.sh https://your-domain        same, and fills in the two places
#                                          that need the real address
#
# Those two places cannot be relative. og:image has to be an absolute URL or the
# link preview resolves in some apps and comes up blank in others, Facebook's
# among them; and the printed card carries the site address as text. Both are
# left blank in the repository and written here, so the source never has to
# carry a domain it might outlive.
#
# Everything here is a copy, so the repository is never modified and this can be
# re-run at any time.
set -e

SITE="${1:-}"
SITE="${SITE%/}"          # a trailing slash would double up in every URL below

cd "$(dirname "$0")"
rm -rf dist
mkdir -p dist

cp index.html dist/
cp -R img fonts card dist/

# Netlify and Cloudflare Pages read _headers from the root of the PUBLISHED
# directory, not the repository, so it has to be copied in like any other file.
cp _headers dist/

# The card is a separate one-page file with its own copies of the two images and
# the display face, so it travels whole. Nothing else in dist/ references it.

# Rewrite through a temporary file rather than sed -i, whose spelling differs
# between GNU and BSD and so breaks on macOS.
rewrite() {
  sed "$1" "$2" > "$2.tmp" && mv "$2.tmp" "$2"
}

if [ -n "$SITE" ]; then
  rewrite "s|<meta property=\"og:image\" content=\"img/og.jpg\">|<meta property=\"og:url\" content=\"$SITE\">\n<meta property=\"og:image\" content=\"$SITE/img/og.jpg\">|" dist/index.html
  # The card's back leaves the address as a marked blank; the class is dropped
  # with it so the dashed rose underline goes too.
  rewrite "s|<span class=\"slot\">your-site-address-here</span>|${SITE#https://}|" dist/card/index.html
  printf 'site address written in as %s\n' "$SITE"
else
  printf 'no domain given — og:image stays relative and the card keeps its blank\n'
fi

printf 'dist/ built — %s over %d files\n' \
  "$(du -sh dist | cut -f1)" "$(find dist -type f | wc -l)"
