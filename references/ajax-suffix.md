# Ajax Suffix Workflow

Use this only after entry-page second hop is already 200. If entry 200 is not proven, API 400 is not actionable.

## When A Suffix Is Needed

1. Build a fresh Cookie T.
2. Request the entry page and confirm 200.
3. Call the business API without any captured suffix.
4. If it returns JSON, suffix is not required for that endpoint.
5. If it returns short 400 while the entry page is 200, profile the suffix/signature.

## Freshness Rules

Never reuse a suffix copied from curl. It is tied to at least some of:

- current `keys`
- request path
- query/body shape
- `nd` or request timestamp
- random value such as `r20`
- server session cookies

The captured suffix is a structure sample, not a credential.

## Inputs To Profile

Capture at least three passing browser API requests:

- full URL including suffix parameter name and value
- method, path, query, and POST body
- `nd` value
- current 45 keys
- cookies used by the request
- Referer and XHR headers
- timestamp near request creation

Then compare suffix byte/string structure across samples. Classify each segment as fixed, key-derived, path-derived, body-derived, time-derived, random, or unknown.

## Common Sources

- suffix parameter name: `keys[7].split(';')[1]`
- path hash or CRC
- `nd` or low32 millisecond timestamp
- `keys[17]`, `keys[19]`, or other branch keys
- random seed from current runtime
- request body serialization order

## Failure Split

| Result | Meaning |
| --- | --- |
| Entry 412 | Cookie T or S/T pairing is still wrong. |
| Entry short 400 | Cookie T decrypts but basearr/profile is wrong. |
| Entry 200, API 400 | Ajax suffix/signature/header serialization is wrong. |
| Entry 200, API HTML | Endpoint/session/header mismatch. |
| Entry 200, API JSON | Business API path is solved. |

## Implementation Rule

Keep Ajax suffix generation as a profile module separate from Cookie T. A suffix change should not require editing the stable Cookie encryption pipeline.
