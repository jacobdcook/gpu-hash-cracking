# Defensive readout — what a defender does about each attack

Cracking is the loud, fun part. The job that pays is stopping it. For each
offensive step above, here is the blue-team side: the control that prevents it
and the detection that catches the step you *can* see.

## Key idea: you cannot detect the crack

Hash cracking happens offline, on the attacker's own hardware, after they have
already stolen the hashes. There is no log on your network for a 4090 chewing
through rockyou in someone's basement. So defense splits in two:

1. **Prevent** — make the hashes not worth cracking (slow algorithms, long
   passphrases, no password at all for service accounts).
2. **Detect the theft** — alert on the *dump* and the *reuse*, which do touch
   your network.

## Prevention

| Problem the lab showed | Control |
|---|---|
| `Summer2024!`, `Spring2024` fell to a mask | Ban the Season+Year pattern; enforce length over complexity (14+ char passphrases). A longer password beats a complex short one against masks. |
| `password1`, `qwertyuiop` fell instantly | Block known-breached passwords (e.g. HaveIBeenPwned password API / AD password filter). |
| Service accounts `svc_sql`, `svc_backup` were crackable | Use Group Managed Service Accounts (gMSA) — 120-char random password, auto-rotated, nothing to crack. |
| NTLM cracked 1.18M× faster than bcrypt | Retire NTLM where possible; for apps, hash with bcrypt/scrypt/argon2id, never raw MD5/SHA. |
| 15-char random password survived everything | This is the goal state. Password managers make it the default. |

## Detection (maps to the ad-attack-lab Wazuh/Sigma rules)

| Attack that produces crackable hashes | What you detect | Signal |
|---|---|---|
| `secretsdump` / DCSync | Replication requested by a non-DC account | Windows Security 4662 with the DS-Replication-Get-Changes GUID, from a host that is not a domain controller |
| LSASS dump (Mimikatz, comsvcs) | Process accessing LSASS memory | Sysmon Event ID 10 targeting `lsass.exe` with suspicious GrantedAccess (0x1010/0x1410) |
| Volume Shadow Copy abuse (grab NTDS.dit) | `vssadmin create shadow`, `esentutl`, copy of `ntds.dit` | Sysmon 1 (process create) + 11 (file create) |
| Kerberoasting (steal TGS to crack offline) | Bulk TGS-REP requests, RC4 (etype 0x17) | Windows Security 4769, many SPNs in a short window, weak encryption type |
| AS-REP roasting | AS-REQ for accounts with pre-auth disabled | Windows Security 4768 with pre-auth not required |
| Cracked password then used | Impossible travel, new-device logon, service account interactive logon | 4624/4625 correlation, auth-log analytics |

## Interview-ready sentences

- "You can't detect cracking — it's offline. So I focus detection on the dump:
  DCSync is a non-DC asking for replication, which is a 4662 with the
  replication GUID, and LSASS access is Sysmon event 10."
- "The lab made the bcrypt argument concrete: the same wordlist that cracked
  NTLM in seconds barely dented bcrypt, because bcrypt ran a million times
  slower on the same GPU. Algorithm choice is a control, not a detail."
- "Masks are why complexity rules backfire. `Summer2024!` satisfies every
  complexity box and falls to a six-character mask. Length is the real defense."
