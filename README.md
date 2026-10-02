# GPU Hash Cracking Lab

Password-cracking workflow on an RTX 4090, from hash generation through
dictionary, rule, and mask attacks, with a defensive readout for each step.
Everything is synthetic: hashes are generated locally from a fake corporate
user list. No real credentials are involved.

The user list mirrors `CORP.LOCAL` in the companion
[`ad-attack-lab`](../ad-attack-lab) repo, so NTLM hashes dumped from that lab
(via `secretsdump`) and Kerberoast / AS-REP tickets land in this exact
workflow. The two repos are one attack chain: **compromise AD → dump hashes →
crack here → escalate.**

## Why this exists

Hiring managers in detection and SOC roles ask whether you actually understand
offense. "I ran hashcat once" is not that. This shows the full method, the
*ceiling* of each technique, real numbers from real hardware, and — the part
that matters for a blue-team role — what each attack looks like from the
defender's side.

## Hardware

- GPU: NVIDIA RTX 4090 (24 GB), driver 580, CUDA 13.0
- hashcat v6.2.6, CUDA backend

## Layout

```
scripts/gen_hashes.py   generate the synthetic hash set (pure-Python NTLM/MD4)
scripts/crack.sh        run the dictionary -> rules -> mask progression
hashes/                 generated hashes (answer key is gitignored)
wordlists/              rockyou (gitignored, fetch script below)
results/                potfile + cracked output + RESULTS.md
docs/                   methodology and defense notes
```

## Run it

```bash
# 1. wordlist (gitignored)
curl -sL -o wordlists/rockyou.txt \
  https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt

# 2. generate the synthetic hashes
python3 scripts/gen_hashes.py

# 3. crack, escalating dictionary -> rules -> mask
bash scripts/crack.sh
```

## Results

Full table and per-user outcome in [RESULTS.md](RESULTS.md). Headline on an RTX 4090:

| Hash | hashcat speed | Cracked (12 synthetic users) |
|---|---|---|
| NTLM | 249 GH/s | 9/12 (dictionary + rules + mask) |
| MD5 | 148 GH/s | 6/12 (dictionary + rules) |
| SHA-256 | 20.7 GH/s | 6/12 (dictionary + rules) |
| bcrypt (cost 12) | 211 kH/s | 3/12 (dictionary only — slow hash) |

NTLM is ~1.18 **million** times faster to attack than bcrypt on the same card.
That single ratio is the argument for slow, salted password hashing.

## The attack progression (and its ceiling)

1. **Dictionary** (`-a 0` rockyou): catches reused and leaked passwords.
2. **Rules** (`-r best64`, `-r dive`): mangles each word — capitalize, append a
   digit, leetspeak. Catches `Monkey123!`, `Welcome123`, `Letmein!1`.
3. **Mask** (`-a 3 ?u?l?l?l?l?l2024!`): brute-forces a *known structure*. This
   is what cracks `Summer2024!`, `Spring2024`, `Falcons2023` — the Season+Year
   pattern that dominates corporate password resets.
4. **Ceiling**: a 15-char random password and a symbol-heavy service account
   survived everything. Length and randomness win. bcrypt survived the same
   wordlist that fell instantly as NTLM, purely because it is slow.

## Defensive readout (the blue-team half)

See [docs/defense.md](docs/defense.md). Short version:

- **Prevent crackability at the source**: long passphrases (length beats
  complexity), ban the Season+Year pattern, kill weak service-account
  passwords, use managed/group service accounts so there is no crackable
  password at all.
- **Algorithm is a control**: NTLM and unsalted MD5 are the problem. Modern
  apps should use bcrypt/scrypt/argon2. You cannot out-hardware a slow hash.
- **Detect the theft, not the crack**: cracking happens offline on the
  attacker's box — invisible to you. So you detect the *dump*: `secretsdump` /
  DCSync (replication from a non-DC), LSASS access, Volume Shadow Copy abuse,
  and Kerberoast (bulk TGS-REP requests, especially RC4). Those map to the
  detections in the AD lab repo.

## Ethics

Synthetic hashes only. This is for learning offense to build better defenses,
on hardware the author owns. Do not run attacks against systems you are not
authorized to test.
