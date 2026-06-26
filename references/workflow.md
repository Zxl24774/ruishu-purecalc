# Workflow

## Phase Table

| Phase | Input | Output | Validation gate |
| --- | --- | --- | --- |
| 0. Observe | Entry URL | Same-session `412` bundle | `cd`, `nsd`, JS URL, and `S` cookie captured together |
| 1. Decode | `cd` | 45 keys | key length invariants pass |
| 2. Rebuild identity | `nsd`, main JS, keys | `codeUid`, function ordering | matches browser branch or decoded sample |
| 3. Profile basearr | decoded browser Cookie T | TLV profile | generated TLV equals sample or known branch |
| 4. Encrypt | basearr, keys | Cookie T | hybrid check gives entry 200 |
| 5. End-to-end | fresh 412 bundle | browser-free entry 200 | 3 fresh sessions pass |
| 6. Business API | entry 200 session | JSON response | current-session suffix or plain API passes |

## Phase 0: Confirm protection

1. Request the entry URL with browser-like headers.
2. Confirm HTTP `412`.
3. Extract:
   - `$_ts.cd`
   - `$_ts.nsd`
   - first challenge JS URL or main JS URL
   - `xxxS` cookie
4. Keep every value in the same `requests.Session`.
5. Save the raw challenge HTML and response headers. They are the evidence bundle for later mismatch debugging.

If the first response is not `412`, do not force the Ruishu path. Check whether prior cookies, redirects, wrong path, or an already-trusted session changed the result.

## Phase 1: Decode challenge material

1. Decode `cd` using Ruishu custom Base64.
2. Extract 45 keys.
3. Verify basic invariants:
   - `len(keys) == 45`
   - `len(keys[2]) == 48`
   - `len(keys[16]) == 16`
   - `len(keys[17]) == 16`
   - `keys[7]` contains semicolon-separated config.
4. Record the cookie-name expression and suffix-name expression from `keys[7]`.

## Phase 2: Rebuild codeUid

1. Use `nsd` to generate the shuffled variable-name list.
2. Rebuild only the outer VM pieces needed for `functionsNameSort`, `mainFunctionIdx`, and `codeUid`.
3. Compute `codeUid` from `keys[33]` and `keys[34]`.
4. If several JS files exist in `keys[7]`, choose by observed profile branch. Do not assume the first challenge `src` is always the codeUid script.

The goal is not to understand every VM state. The goal is to reproduce the identity values that appear in TLV fields.

## Phase 3: Build basearr

1. Build TLV fields in browser order.
2. Use real samples to decide field lengths and branch rules.
3. For unknown bytes, decode a passing Cookie T and compare byte-by-byte.
4. Classify field sources before coding:
   - fixed profile constant
   - value from `keys[N]`
   - timestamp or elapsed time
   - random value
   - computed value such as CRC, path hash, `codeUid`, or cp1 mapping
   - environment value such as UA, platform, viewport, language, visibility

Do not read the deepest VM first for basearr. The fastest path is usually decoded browser data plus byte-level diffs.

## Phase 4: Encrypt Cookie T

1. Huffman-compress `basearr`.
2. XOR the first 16 compressed bytes with `keys[2][0:16]`.
3. AES-CBC encrypt with `keys[17]`, zero IV.
4. Build packet: `[2,8] + r2t + now + [48] + keys[2] + len(cipher) + cipher`.
5. Prefix `CRC32(packet)`.
6. AES-CBC encrypt with `keys[16]` and random IV.
7. Encode with Ruishu custom Base64 and prefix `0`.

Before debugging basearr, run the hybrid check: use a browser/sdenv basearr with pure encryption. If this does not produce entry 200, the encryption pipeline or key extraction is wrong.

## Phase 5: Verify Cookie T

1. Set `xxxS`, `xxxT`, and any observed enable cookie.
2. Request the same entry URL.
3. Require HTTP 200 before touching business APIs.
4. Repeat with at least three fresh 412 bundles.

## Phase 6: Verify business API

1. If plain POST/GET succeeds after entry 200, no suffix is needed.
2. If API returns 400 while entry-page second hop is 200, solve Ajax suffix.
3. Generate suffix from current session keys and current request timestamp.
4. Treat curl suffix samples as structure hints only; captured suffix values expire with their session.
