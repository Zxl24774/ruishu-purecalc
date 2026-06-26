# Basearr Profile

## Profile Model

Represent site-specific behavior as data:

```json
{
  "target": "http://host:port",
  "entry_path": "/path/page.jsp",
  "ua": "browser UA used in request and type3",
  "cookie_name_expr": "keys[7].split(';')[5] + 'T'",
  "suffix_name_expr": "keys[7].split(';')[1]",
  "branches": [
    {
      "name": "keys22-present",
      "condition": "len(keys[22]) > 0",
      "basearr_length": 156,
      "code_uid_js_index": 8,
      "type10_length": 34
    },
    {
      "name": "keys22-empty",
      "condition": "len(keys[22]) == 0",
      "basearr_length": 140,
      "code_uid_js_index": 9,
      "type10_length": 18
    }
  ]
}
```

## TLV Checks

Always parse `basearr` as:

```text
type, length, payload...
```

Common fields:

- `type=3`: environment, often the largest stable field.
- `type=10`: time/network, often branch-dependent.
- `type=7`: fixed header + flag + codeUid.
- `type=0`: short fixed state or longer state blob.
- `type=6`: visibility/decrypted keys22 state.
- `type=2`: cp1 mapping.
- `type=9`: small fixed payload, often `[8,0]`, but profile it.
- `type=13`: small fixed payload, often `[0]`, but profile it.

## Branch Detection

Good branch keys usually come from decoded data, not from guessed VM names:

- `len(keys[22]) == 0` vs `> 0`
- total decoded basearr length
- `type10` payload length
- `type6` presence or decrypted payload length
- `type7` flag bytes
- selected codeUid JS index

If Cookie T length alternates, decode both successful browser cookies and compare TLV shapes. Different encoded lengths usually mean a branch difference before encryption, not a random AES issue.

## Field Source Labels

During diff, classify each byte:

- `fixed`: same in every sample.
- `key`: equals or derives from `keys[N]`.
- `time`: changes with `r2t`, `now`, `nd`, or millisecond low32.
- `random`: changes without direct server relation.
- `environment`: UA, platform, viewport, language, visibility.
- `computed`: CRC, codeUid, cp1 mapping, path CRC.
- `unknown`: collect more samples.

Do not promote `unknown` to fixed after one sample.

## Type 2 Mapping

`type=2` is commonly tied to the `cp1` shuffled variable-name list. Avoid hardcoding the payload from one session.

1. Collect at least five passing samples.
2. Record `nsd`, relevant `keys[29..32]`, and decoded `type=2`.
3. Rebuild `cp1` for each `nsd`.
4. Infer an index-to-byte map that remains stable across sessions.
5. Store that map in the site profile.

## Hooking Rule

Ruishu variable names are not stable. Use structural matching:

- code length or eval payload size
- constants such as `15679`, `2531011`, Base64 alphabet, AES key lengths
- AST shape around state arrays or dispatcher calls
- TLV type order and payload lengths

Do not use literal function or variable names as durable anchors unless they are proven fixed across several fresh `nsd` values.
