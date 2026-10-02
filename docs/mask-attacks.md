# Mask attacks — cracking structured passwords

When rules plateau, masks take over. A mask brute-forces a *known shape*
instead of every character, which is what makes patterned passwords fall fast.

## Charsets
| Token | Set |
|---|---|
| ?l | a-z |
| ?u | A-Z |
| ?d | 0-9 |
| ?s | symbols |
| ?a | all of the above |

## The corporate pattern
`Summer2024!` = one upper, five lower, a year, a symbol:
```
hashcat -m 1000 hashes.txt '?u?l?l?l?l?l2024!'
```
Keyspace is tiny (26 * 26^5), seconds on a 4090, because you fixed the structure.

## Hybrid (wordlist + mask)
Append a mask to every dictionary word (-a 6) or prepend (-a 7):
```
hashcat -m 1000 hashes.txt rockyou.txt '?d?d?d?d'   # word + 4 digits
```

## Why this matters for defense
Complexity rules *create* this pattern. `Summer2024!` passes every complexity
box and dies to a 6-char mask. Length (a passphrase) is the real defense,
because it explodes the keyspace a mask has to cover.
