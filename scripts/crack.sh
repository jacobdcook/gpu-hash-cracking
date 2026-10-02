#!/usr/bin/env bash
# Dictionary -> rules -> mask progression against the synthetic hash set.
# Requires hashcat on PATH (apt install hashcat) or set HASHCAT=/path/to/hashcat.bin
set -euo pipefail
cd "$(dirname "$0")/.."

HASHCAT="${HASHCAT:-hashcat}"
WL="wordlists/rockyou.txt"
POT="results/lab.potfile"
RULES_DIR="${RULES_DIR:-/usr/share/hashcat/rules}"   # apt install path
mkdir -p results
[ -f "$WL" ] || { echo "Missing $WL — see README step 1"; exit 1; }
[ -f hashes/raw_ntlm.txt ] || { echo "Run scripts/gen_hashes.py first"; exit 1; }

show() { "$HASHCAT" -m "$1" --potfile-path "$POT" --show "$2" 2>/dev/null | wc -l; }

echo "== Stage 1: dictionary (rockyou) =="
for pair in "1000 hashes/raw_ntlm.txt" "0 hashes/md5.txt" "1400 hashes/sha256.txt"; do
  set -- $pair
  "$HASHCAT" -m "$1" -a 0 -O --potfile-path "$POT" "$2" "$WL" >/dev/null 2>&1 || true
done

echo "== Stage 2: rules (best64, then dive) =="
for rule in best64.rule dive.rule; do
  [ -f "$RULES_DIR/$rule" ] || continue
  for pair in "1000 hashes/raw_ntlm.txt" "0 hashes/md5.txt" "1400 hashes/sha256.txt"; do
    set -- $pair
    "$HASHCAT" -m "$1" -a 0 -O --potfile-path "$POT" "$2" "$WL" -r "$RULES_DIR/$rule" >/dev/null 2>&1 || true
  done
done

echo "== Stage 3: targeted masks (Season+Year corporate pattern) =="
for mask in '?u?l?l?l?l?l2024!' '?u?l?l?l?l?l2024' '?u?l?l?l?l?l?l2023'; do
  "$HASHCAT" -m 1000 -a 3 -O --potfile-path "$POT" hashes/raw_ntlm.txt "$mask" >/dev/null 2>&1 || true
done

echo "== Stage 4: bcrypt (slow hash, dictionary only, 5 min cap) =="
"$HASHCAT" -m 3200 -a 0 --potfile-path "$POT" --runtime=300 hashes/bcrypt.txt "$WL" >/dev/null 2>&1 || true

echo
echo "Cracked counts (out of 12):"
printf "  NTLM    %s\n" "$(show 1000 hashes/raw_ntlm.txt)"
printf "  MD5     %s\n" "$(show 0 hashes/md5.txt)"
printf "  SHA256  %s\n" "$(show 1400 hashes/sha256.txt)"
printf "  bcrypt  %s\n" "$(show 3200 hashes/bcrypt.txt)"
echo "Potfile: $POT"
