# Portability

## Values that should be fixed or profiled

- User-Agent and UA CRC.
- Platform, usually `Win32`.
- Viewport and outer window sizes.
- Language headers.
- Visibility state.
- Performance counters if present in type3.

If these values are part of basearr, request headers must match them. Do not read them from the local machine unless the collector deliberately models that machine.

## Values that must be fresh

- `cd`, `nsd`, keys, S cookie, T cookie.
- `r2t`, current time, random r20.
- Ajax `nd` and suffix value.

## Machine-specific risks

- Clock drift.
- Different proxy or IP reputation.
- TLS fingerprint on HTTPS targets.
- Corporate proxy rewriting headers.
- Python version or crypto library padding differences.

## Portability checklist

1. Install exact Python dependencies.
2. Sync system time.
3. Run entry second-hop verification.
4. Run business API verification.
5. If only the new machine fails, compare outbound headers and proxy/TLS behavior before changing basearr.

