#!/usr/bin/env bash
set -euo pipefail

SRC="/mnt/c/Users/DELL/Downloads/sip-lab-wsl2/lab"
DST="$HOME/sip-lab"

mkdir -p "$DST/kamailio" "$DST/sipp" "$DST/tools" "$DST/run"

cp -f "$SRC/kamailio/"* "$DST/kamailio/"
cp -f "$SRC/sipp/"* "$DST/sipp/"
cp -f "$SRC/tools/"* "$DST/tools/"
if compgen -G "$SRC/run/*" > /dev/null; then
    cp -f "$SRC/run/"* "$DST/run/"
fi

chmod +x "$DST/tools/"*.sh "$DST/tools/"*.py 2>/dev/null || true

printf 'Synced lab assets from %s to %s\n' "$SRC" "$DST"
