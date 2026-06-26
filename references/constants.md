# Constants And Key Meanings

This file records values that are commonly stable across Ruishu variants. Treat them as defaults, then verify against the current target.

## Common Constants

| Item | Value or rule |
| --- | --- |
| PRNG | `seed = 15679 * (seed & 0xffff) + 2531011` |
| Huffman weights | byte `0` -> `45`, byte `255` -> `6`, other bytes -> `1` |
| Inner AES | AES-128-CBC, key `keys[17]`, zero IV |
| Outer AES | AES-128-CBC, key `keys[16]`, random 16-byte IV |
| CRC32 polynomial | `0xEDB88320` |
| Cookie T name | `keys[7].split(';')[5] + 'T'` |
| Ajax suffix name | `keys[7].split(';')[1]` |
| getLine multiplier | `55295` |
| Variable chars | `_$abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789` |
| `_ifElse` steps | `[4, 16, 64, 256, 1024, 4096, 16384, 65536]` |

Custom Base64 alphabet:

```text
qrcklmDoExthWJiHAp1sVYKU3RFMQw8IGfPO92bvLNj.7zXBaSnu0TC6gy_4Ze5d
```

`cd` decoding commonly uses the same alphabet plus extra punctuation:

```text
qrcklmDoExthWJiHAp1sVYKU3RFMQw8IGfPO92bvLNj.7zXBaSnu0TC6gy_4Ze5d{}|~ !#$%()*+,-;=?@[]^
```

## Encryption Pipeline

```text
basearr
  -> Huffman encode
  -> XOR first 16 bytes with keys[2][0:16]
  -> AES-CBC with keys[17], zero IV, PKCS7
  -> packet: [2, 8] + r2t(4B) + now(4B) + [48] + keys[2](48B) + len(cipher) + cipher
  -> CRC32(packet) prefix
  -> AES-CBC with keys[16], random IV, PKCS7
  -> custom Base64
  -> "0" + encoded payload
```

## Key Reference

| Key | Typical length | Meaning | Common use |
| --- | --- | --- | --- |
| `keys[2]` | 48 bytes | KEYS48 | first-16-byte XOR and packet embedded material |
| `keys[7]` | variable | semicolon config | cookie name, suffix param name, JS selection hints |
| `keys[16]` | 16 bytes | outer AES key | final Cookie T encryption |
| `keys[17]` | 16 bytes | inner AES key | compressed basearr encryption |
| `keys[19]` | variable | timestamp/config string | time fields and some suffix routines |
| `keys[21]` | variable | r2mka time related | nonce/time input |
| `keys[22]` | variable | encrypted or optional branch data | `type=6`, branch selection |
| `keys[24..26]` | variable | numeric strings/config | `type=10` and branch-specific fields |
| `keys[29..32]` | often 4 bytes each | variable names or cp1 anchors | `type=2` mapping |
| `keys[33..34]` | variable | codeUid inputs | `type=7` identity |

## Stability Classification

- Usually fixed in engine code: PRNG, Base64 alphabet, Huffman weights, AES/CRC pipeline.
- Variant-fixed after extraction: key indices and cookie/suffix name expressions.
- Profile-specific: TLV field order, branch lengths, codeUid JS index, type2 mapping.
- Fresh every session: `cd`, `nsd`, `S`, `T`, keys, time fields, suffix values.
