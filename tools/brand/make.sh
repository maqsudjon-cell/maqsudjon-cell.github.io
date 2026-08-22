#!/bin/bash
# Flarestamina brand assets — every file here is drawn from code (SVG paths and
# an HTML card rasterised by headless Chrome). Nothing is AI-generated.
#
#   bash tools/brand/make.sh
#
# Needs: python3 + cairosvg, ImageMagick (`magick`), Google Chrome.
set -e
# ASSET VERSION — bump this and the ?v= in tools/site/shell.py + the HTML together
# whenever the mark or the cards change. Browsers cache favicons by URL and
# Telegram/Facebook cache OG cards by image URL; without a new URL they keep
# serving the old art for weeks.
ASSET_V=2
DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$DIR/../.." && pwd)"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

png () { # png <src.svg> <size> <out.png>
  python3 -c "
import cairosvg,sys
cairosvg.svg2png(url=sys.argv[1], write_to=sys.argv[3],
                 output_width=int(sys.argv[2]), output_height=int(sys.argv[2]))
" "$1" "$2" "$3"
}

echo "→ favicons"
# small sizes use the thicker-waisted variant so the arms survive
png "$DIR/spark-compact.svg"  16 "$TMP/16.png"
png "$DIR/spark-compact.svg"  32 "$TMP/32.png"
png "$DIR/spark-compact.svg"  48 "$TMP/48.png"
magick "$TMP/16.png" "$TMP/32.png" "$TMP/48.png" "$ROOT/favicon.ico"

png "$DIR/spark.svg"  96 "$ROOT/favicon-96.png"
png "$DIR/spark.svg" 180 "$ROOT/apple-touch-icon.png"
png "$DIR/spark.svg" 192 "$ROOT/icon-192.png"
png "$DIR/spark.svg" 512 "$ROOT/icon-512.png"
cp "$DIR/spark.svg" "$ROOT/favicon.svg"

echo "→ og cards"
card () { # card <out.png> <kicker> <title> <sub> [url]
  out="$1"; k="$2"; t="$3"; s="$4"; u="${5:-flarestamina.com}"
  q="kicker=$(u "$k")&title=$(u "$t")&sub=$(u "$s")&url=$(u "$u")"
  "$CHROME" --headless --disable-gpu --hide-scrollbars --no-sandbox \
    --window-size=1200,630 --force-device-scale-factor=1 \
    --virtual-time-budget=6000 \
    --screenshot="$out" "file://$DIR/og.html?$q" >/dev/null 2>&1
  echo "  ✓ ${out#$ROOT/}"
}
u () { python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" "$1"; }

card "$ROOT/og-image.png"            "Flarestamina" "Practice like it’s exam day."              "Free IELTS Academic practice. Tashkent."
card "$ROOT/tests/og.png"             "Catalogue"    "Every IELTS practice test, in one list."   "112 free papers and tools."                  "flarestamina.com/tests"
card "$ROOT/news/og.png"             "News"         "IELTS news, with the source attached."     "Fees, One Skill Retake, scholarships."       "flarestamina.com/news"
card "$ROOT/convert/og.png"          "Converter"    "IELTS, CEFR, Multilevel, TOEFL."           "Official conversion tables."                 "flarestamina.com/convert"
card "$ROOT/deadlines/og.png"        "Deadlines"    "Exam and scholarship dates."               "For students in Uzbekistan."                 "flarestamina.com/deadlines"
card "$ROOT/plan/og.png"             "Study plan"   "From the band you have to the band you need." "A plan you can actually follow."           "flarestamina.com/plan"
card "$ROOT/founder/og.png"          "Founder"      "Built by someone sitting the same exam."   "Maqsudjon Polatov · Tashkent."               "flarestamina.com/founder"
card "$ROOT/teachers/og.png"         "Teachers"     "Set the paper. Read the results."          "Flarestamina for teachers."                  "flarestamina.com/teachers"
card "$ROOT/speaking-topics/og.png"  "Speaking"     "The current Speaking topic rotation."      "Parts 1–3, updated each season."             "flarestamina.com/speaking-topics"
card "$ROOT/writearticle/og.png"     "Writing lab"  "Task 1 and Task 2, taken apart."           "Plans, model structures, vocabulary."        "flarestamina.com/writearticle"
card "$ROOT/account/og.png"          "FS Account"   "One account for every Flarestamina tool."  "Tests, mocks, speaking and writing."         "flarestamina.com/account"

echo "→ done"
