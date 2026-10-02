# HANDOFF — gpu-hash-cracking

## State (2026-10-01)
Complete and working. Real crack run done on the RTX 4090.
- scripts/gen_hashes.py: pure-Python NTLM/MD4 generator, 12 synthetic users. Self-test passes.
- scripts/crack.sh: dictionary -> rules -> mask -> bcrypt progression.
- RESULTS.md + results/cracked_*.txt: REAL results. NTLM 9/12, MD5 6/12, SHA256 6/12, bcrypt 3/12.
- Benchmarks real: NTLM 249 GH/s, bcrypt 211 kH/s on the 4090.
- docs/defense.md: blue-team detections (ties to ad-attack-lab).

## Notes
- rockyou.txt and ANSWER_KEY.csv are gitignored. cracked_*.txt hold SYNTHETIC plaintext (safe to commit).
- Ran with portable hashcat at /tmp/hashcat-6.2.6. After `apt install hashcat`, scripts just use `hashcat` on PATH.

## Not done
- Nothing required. Optional: add OneRuleToRuleThemAll, combinator attacks.
