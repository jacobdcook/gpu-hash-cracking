#!/usr/bin/env python3
"""
Generate a realistic corporate hash set for cracking practice.

Everything here is synthetic. No real credentials. The point is to produce
the exact hash formats you meet in the field (NTLM from a DC dump, MD5/SHA256
from a leaked web DB, bcrypt from a modern app) so the cracking workflow is
real end to end.

NTLM is implemented from scratch (NTLM = MD4(password as UTF-16LE)) so the
repo has no exotic dependencies and the internals are visible.

Outputs:
  hashes/ntlm.txt     user:rid:lmhash:nthash:::   (secretsdump format)
  hashes/raw_ntlm.txt  just the nt hashes, one per line (hashcat -m 1000)
  hashes/md5.txt       one per line (hashcat -m 0)
  hashes/sha256.txt    one per line (hashcat -m 1400)
  hashes/bcrypt.txt    one per line (hashcat -m 3200)   [if bcrypt available]
  hashes/ANSWER_KEY.csv  plaintext mapping -- gitignored, for self-check only
"""
import hashlib, struct, csv, os, sys

# ---------------------------------------------------------------------------
# MD4 (RFC 1320), pure Python. NTLM = MD4(UTF-16LE(password)).
# ---------------------------------------------------------------------------
def _lrot(x, n):
    x &= 0xFFFFFFFF
    return ((x << n) | (x >> (32 - n))) & 0xFFFFFFFF

def md4(data: bytes) -> bytes:
    msg = bytearray(data)
    orig_bits = (8 * len(data)) & 0xFFFFFFFFFFFFFFFF
    msg.append(0x80)
    while len(msg) % 64 != 56:
        msg.append(0)
    msg += struct.pack("<Q", orig_bits)

    A, B, C, D = 0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476
    for off in range(0, len(msg), 64):
        X = list(struct.unpack("<16I", msg[off:off + 64]))
        a, b, c, d = A, B, C, D

        def F(x, y, z): return (x & y) | (~x & z)
        def G(x, y, z): return (x & y) | (x & z) | (y & z)
        def H(x, y, z): return x ^ y ^ z

        for i in (0, 4, 8, 12):
            a = _lrot(a + F(b, c, d) + X[i],     3)
            d = _lrot(d + F(a, b, c) + X[i + 1], 7)
            c = _lrot(c + F(d, a, b) + X[i + 2], 11)
            b = _lrot(b + F(c, d, a) + X[i + 3], 19)
        for i in (0, 1, 2, 3):
            a = _lrot(a + G(b, c, d) + X[i]      + 0x5A827999, 3)
            d = _lrot(d + G(a, b, c) + X[i + 4]  + 0x5A827999, 5)
            c = _lrot(c + G(d, a, b) + X[i + 8]  + 0x5A827999, 9)
            b = _lrot(b + G(c, d, a) + X[i + 12] + 0x5A827999, 13)
        for i in (0, 2, 1, 3):
            a = _lrot(a + H(b, c, d) + X[i]      + 0x6ED9EBA1, 3)
            d = _lrot(d + H(a, b, c) + X[i + 8]  + 0x6ED9EBA1, 9)
            c = _lrot(c + H(d, a, b) + X[i + 4]  + 0x6ED9EBA1, 11)
            b = _lrot(b + H(c, d, a) + X[i + 12] + 0x6ED9EBA1, 15)

        A = (A + a) & 0xFFFFFFFF
        B = (B + b) & 0xFFFFFFFF
        C = (C + c) & 0xFFFFFFFF
        D = (D + d) & 0xFFFFFFFF
    return struct.pack("<4I", A, B, C, D)

def nt_hash(password: str) -> str:
    return md4(password.encode("utf-16le")).hexdigest() if False else md4(password.encode("utf-16le")).hex()

# ---------------------------------------------------------------------------
# Synthetic corporate users. Passwords span the strength spectrum on purpose:
#  - trivial (in rockyou, fall in seconds)
#  - keyboard/seasonal patterns (fall with rules)
#  - decent-but-cracked (fall with rules + mask)
#  - strong random (should NOT fall -- proves the method's ceiling)
# Mirrors CORP.LOCAL in the companion ad-attack-lab repo so a Kerberoast /
# secretsdump from that lab lands in the same workflow.
# ---------------------------------------------------------------------------
USERS = [
    ("Administrator", 500, "P@ssw0rd"),         # classic, weak
    ("jsmith",       1104, "password1"),         # top-20 ever
    ("mjones",       1105, "Summer2024!"),       # seasonal pattern
    ("rpatel",       1106, "Welcome123"),        # onboarding default
    ("klee",         1107, "Falcons2023"),       # team + year
    ("dgarcia",      1108, "Spring2024"),         # season + year
    ("twilson",      1109, "Letmein!1"),          # keyboard-ish
    ("svc_sql",      1110, "Sql$erv1ce"),         # service account
    ("svc_backup",   1111, "Backup2024#"),        # service account
    ("bchen",        1112, "qwertyuiop"),         # keyboard walk
    ("afoster",      1113, "Monkey123!"),          # word + rule
    ("ghall",        1114, "7Kp!vQ2z@Lm9xRt"),    # strong random -- survives
]

def main():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    hd = os.path.join(here, "hashes")
    os.makedirs(hd, exist_ok=True)

    # bcrypt is optional; only emit that file if a backend exists.
    bcrypt_fn = None
    try:
        import bcrypt
        bcrypt_fn = lambda p: bcrypt.hashpw(p.encode(), bcrypt.gensalt(rounds=10)).decode()
    except Exception:
        try:
            import crypt
            if hasattr(crypt, "METHOD_BLOWFISH"):
                bcrypt_fn = lambda p: crypt.crypt(p, crypt.METHOD_BLOWFISH)
        except Exception:
            pass

    ntlm, raw_ntlm, md5s, sha256s, bcrypts, key = [], [], [], [], [], []
    EMPTY_LM = "aad3b435b51404eeaad3b435b51404ee"
    for user, rid, pw in USERS:
        nt = nt_hash(pw)
        ntlm.append(f"{user}:{rid}:{EMPTY_LM}:{nt}:::")
        raw_ntlm.append(nt)
        md5s.append(hashlib.md5(pw.encode()).hexdigest())
        sha256s.append(hashlib.sha256(pw.encode()).hexdigest())
        row = {"user": user, "password": pw, "ntlm": nt}
        if bcrypt_fn:
            b = bcrypt_fn(pw)
            bcrypts.append(b)
            row["bcrypt"] = b
        key.append(row)

    def w(name, lines):
        with open(os.path.join(hd, name), "w") as f:
            f.write("\n".join(lines) + "\n")
        print(f"  {name:16} {len(lines)} hashes")

    w("ntlm.txt", ntlm)
    w("raw_ntlm.txt", raw_ntlm)
    w("md5.txt", md5s)
    w("sha256.txt", sha256s)
    if bcrypts:
        w("bcrypt.txt", bcrypts)
    else:
        print("  bcrypt.txt       skipped (no bcrypt backend)")

    with open(os.path.join(hd, "ANSWER_KEY.csv"), "w", newline="") as f:
        cols = ["user", "password", "ntlm"] + (["bcrypt"] if bcrypts else [])
        wri = csv.DictWriter(f, fieldnames=cols)
        wri.writeheader()
        for r in key:
            wri.writerow({k: r.get(k, "") for k in cols})
    print(f"  ANSWER_KEY.csv   {len(key)} rows (gitignored)")

    # self-test against a known NTLM vector
    assert nt_hash("password") == "8846f7eaee8fb117ad06bdd830b7586c", "MD4/NTLM self-test failed"
    print("  NTLM self-test   OK (password -> 8846f7eaee8fb117ad06bdd830b7586c)")

if __name__ == "__main__":
    main()
