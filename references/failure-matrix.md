# Failure Matrix

| Symptom | Likely layer | What to inspect |
| --- | --- | --- |
| First request is not 412 | Not Ruishu or already trusted | Target path, cookies, cache, redirects, previous trusted session. |
| Second hop 412 | Cookie generation or S/T pairing | Cookie name, S cookie, T format, challenge freshness, AES keys. |
| Second hop short 400 | Cookie decrypts but content fails | basearr length, TLV fields, type10 branch, type2 mapping, codeUid. |
| Entry 200, API 400 | Business suffix/signature | URL suffix name/value, `nd`, path CRC, current session keys. |
| Entry 200, API HTML | Wrong endpoint or headers | Referer, X-Requested-With, Content-Type, session cookies, expected route. |
| Works on one computer, fails on another | Portability | UA/type3 consistency, system time, proxy/TLS, environment fields. |

## Debug Order

1. Decrypt your generated Cookie T and verify the decoded basearr equals what you intended.
2. Decode a browser-passing Cookie T from the same target variant.
3. Compare TLV by TLV.
4. Fix the first structural difference before changing later fields.
5. Re-test entry 200 before testing business API.

## Second-Hop 412 Checklist

- Cookie name is derived from the current `keys[7]`, not hardcoded from old traffic.
- `S` and `T` cookies come from the same challenge bundle.
- Cookie T starts with the expected version prefix, usually `0`.
- `keys[16]`, `keys[17]`, and `keys[2]` pass length checks.
- Packet time fields are fresh and the local system clock is not badly skewed.
- The request path and Host match the challenge that produced `S`.

## Short 400 Checklist

Short entry-page 400 usually means the server decrypted Cookie T but rejected the decoded content.

- Run hybrid verification before changing basearr.
- Compare decoded browser basearr and generated basearr by TLV, not by whole-string length only.
- Check branch fields first: `keys[22]`, `type10` length, `type6`, `type7`, and codeUid JS choice.
- Check `type=2` cp1 mapping; do not copy a single sample.
- Check `type3` UA/platform/viewport/language consistency with request headers.

## Coder Mismatch Checklist

If rebuilt eval/outer VM output differs from browser output:

- Find the first byte or character difference.
- Check opcode operand counts before semantic explanations.
- Recreate PRNG state per block when the original code does.
- Confirm `getLine` multiplier and variable-name shuffle seed.
- Use constants and AST structure, not variable names, to locate functions.

## Keys Extraction Checklist

- `len(keys) == 45`.
- `keys[0]` matches the expected decoded marker for the target variant.
- `len(keys[2]) == 48`.
- `len(keys[16]) == 16`.
- `len(keys[17]) == 16`.
- `keys[29..32]` are present when the profile uses `type=2` cp1 mapping.

If these fail, stay in `cd` decode and extraction logic. Do not debug basearr yet.
