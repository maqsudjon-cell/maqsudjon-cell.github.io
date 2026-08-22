#!/bin/bash
# Subsets the two site faces to WOFF2 and drops them in assets/fonts/.
# Self-hosting removes a render-blocking third-party stylesheet plus two
# extra connections (fonts.googleapis.com and fonts.gstatic.com) from every
# page. Re-run after replacing a source TTF.
#
#   bash tools/brand/fonts.sh
#
# Needs: pip install fonttools brotli
set -e
DIR="$(cd "$(dirname "$0")/../../assets/fonts" && pwd)"

# Latin + Latin-Ext covers Uzbek (including oʻ/gʻ), Turkish and German names
# that appear in the scholarship posts; the rest is the punctuation and the
# arrows the UI actually draws.
RANGE="U+0000-00FF,U+0100-017F,U+0192,U+02BB-02BC,U+02C6,U+02DA,U+2013-2014,U+2018-201A,U+201C-201E,U+2020-2022,U+2026,U+2030,U+2039-203A,U+2044,U+20A0-20BF,U+2122,U+2190-2199,U+21BA-21BB,U+2212,U+2215,U+2248,U+2260,U+2264-2265,U+25A0-25FF,U+2605,U+2713-2714,U+FEFF"

sub () { # sub <in.ttf> <out.woff2> [extra flags]
  python3 -m fontTools.subset "$DIR/$1" \
    --unicodes="$RANGE" \
    --layout-features='kern,liga,calt,ccmp,locl,mark,mkmk,tnum,case' \
    --flavor=woff2 \
    --output-file="$DIR/$2" ${3:-}
  printf "  %-26s %6s KB\n" "$2" "$(( $(wc -c < "$DIR/$2") / 1024 ))"
}

echo "→ subsetting"
# only 400-600 is ever used, and slicing the axis first roughly halves the file
python3 -m fontTools.varLib.instancer "$DIR/Inter-Variable.ttf" wght=400:600 \
  -o "$DIR/.inter-slice.ttf" >/dev/null
sub .inter-slice.ttf          inter-var.woff2
rm -f "$DIR/.inter-slice.ttf"
sub IBMPlexMono-Regular.ttf   plex-mono-400.woff2
sub IBMPlexMono-Medium.ttf    plex-mono-500.woff2
echo "→ done"
