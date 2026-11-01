#!/bin/bash
# parallel range downloader: pdl.sh URL OUT NCHUNKS
URL="$1"; OUT="$2"; N="${3:-12}"
SIZE=$(curl -sIL "$URL" | rg -io "content-length: [0-9]+" | tail -1 | rg -o "[0-9]+")
if [ -z "$SIZE" ]; then
  SIZE=$(curl -sL -r 0-0 -o /dev/null -D - "$URL" 2>/dev/null | rg -io "content-range: bytes 0-0/[0-9]+" | tail -1 | rg -o "[0-9]+$")
fi
if [ -z "$SIZE" ]; then echo "no size"; exit 1; fi
echo "size=$SIZE chunks=$N"
CHUNK=$(( (SIZE + N - 1) / N ))
rm -f "$OUT".part.*
pids=()
for i in $(seq 0 $((N-1))); do
  S=$((i*CHUNK)); E=$(( S+CHUNK-1 )); [ $E -ge $SIZE ] && E=$((SIZE-1))
  ( for try in 1 2 3; do curl -sSL --range $S-$E -o "$OUT.part.$i" "$URL" && sz=$(stat -c%s "$OUT.part.$i" 2>/dev/null || echo 0) && [ "$sz" -eq $((E-S+1)) ] && break; sleep 1; done ) &
  pids+=($!)
done
for p in "${pids[@]}"; do wait $p; done
cat $(for i in $(seq 0 $((N-1))); do echo "$OUT.part.$i"; done) > "$OUT"
TOTAL=$(stat -c%s "$OUT")
echo "total=$TOTAL expected=$SIZE"
[ "$TOTAL" -eq "$SIZE" ] && echo PDL_OK || echo PDL_FAIL
rm -f "$OUT".part.*
