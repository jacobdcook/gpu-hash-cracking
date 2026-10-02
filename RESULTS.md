# Results — real crack run on RTX 4090

Generated from `results/lab.potfile`. Synthetic hashes, no real creds.

## GPU benchmark (hashcat v6.2.6, CUDA 13.0, RTX 4090)

| Mode | Hash | Speed |
|---|---|---|
| 0 | MD5 | 148.3 GH/s |
| 100 | SHA1 | 46.2 GH/s |
| 1000 | NTLM | 249.3 GH/s |
| 1400 | SHA-256 | 20.7 GH/s |
| 3200 | bcrypt (cost 12) | 211.7 kH/s |
| 13100 | Kerberoast (TGS-REP) | 3.24 GH/s |
| 18200 | AS-REP | 3.34 GH/s |

NTLM is ~1.18 million times faster to attack than bcrypt on the same GPU.

## Per-user outcome (NTLM)

| User | Password strength | Cracked? | Method |
|---|---|---|---|
| Administrator | `P@ssw0rd` | yes | rules (best64/dive) |
| jsmith | `password1` | yes | dictionary (rockyou) |
| mjones | `Summer2024!` | yes | mask (?u?l..+year) |
| rpatel | `Welcome123` | yes | rules (best64/dive) |
| klee | `Falcons2023` | yes | mask (?u?l..+year) |
| dgarcia | `Spring2024` | yes | mask (?u?l..+year) |
| twilson | `Letmein!1` | yes | rules (best64/dive) |
| svc_sql | `Sql$erv1ce` | **no** | — (survived) |
| svc_backup | `Backup2024#` | **no** | — (survived) |
| bchen | `qwertyuiop` | yes | dictionary (rockyou) |
| afoster | `Monkey123!` | yes | rules (best64/dive) |
| ghall | `7Kp!vQ2z@Lm9xRt` | **no** | — (survived) |

**NTLM: 9/12 cracked.**

## The lesson

- Dictionary alone catches the laziest passwords.
- Rules (best64, dive) catch simple mangles: capitalization, a trailing digit, leetspeak.
- Masks catch *structured* passwords once you guess the structure (Season+Year+symbol is the classic corporate pattern).
- What survived: a service account with mixed symbols and a 15-char random password. Length + randomness beats the GPU.
- bcrypt survived almost everything **at the same wordlist** purely because it is slow. Algorithm choice is a control.
