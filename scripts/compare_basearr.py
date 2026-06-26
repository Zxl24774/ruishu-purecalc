#!/usr/bin/env python3
"""Compare two Ruishu basearr JSON arrays as TLV fields."""

import json
import sys
from pathlib import Path


def load_array(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict):
        for key in ("basearr", "browser_basearr", "python_basearr"):
            if key in data:
                data = data[key]
                break
    if not isinstance(data, list) or not all(isinstance(x, int) for x in data):
        raise SystemExit(f"{path}: expected JSON integer array or object containing basearr")
    return data


def tlv(arr):
    out = []
    pos = 0
    while pos + 2 <= len(arr):
        typ = arr[pos]
        length = arr[pos + 1]
        payload = arr[pos + 2:pos + 2 + length]
        out.append((typ, length, pos, payload))
        pos += 2 + length
    return out, pos


def main(argv):
    if len(argv) != 3:
        raise SystemExit("usage: compare_basearr.py browser.json python.json")
    left = load_array(argv[1])
    right = load_array(argv[2])
    l_tlv, l_end = tlv(left)
    r_tlv, r_end = tlv(right)

    print(f"left_len={len(left)} right_len={len(right)} equal={left == right}")
    print(f"left_parse_end={l_end} right_parse_end={r_end}")

    for idx in range(max(len(l_tlv), len(r_tlv))):
        if idx >= len(l_tlv):
            print(f"field[{idx}] missing_left right={r_tlv[idx][:3]}")
            continue
        if idx >= len(r_tlv):
            print(f"field[{idx}] missing_right left={l_tlv[idx][:3]}")
            continue

        lt, ll, lp, lv = l_tlv[idx]
        rt, rl, rp, rv = r_tlv[idx]
        diffs = []
        for j in range(max(len(lv), len(rv))):
            a = lv[j] if j < len(lv) else None
            b = rv[j] if j < len(rv) else None
            if a != b:
                diffs.append((j, a, b))
        print(f"field[{idx}] type {lt}/{rt} len {ll}/{rl} pos {lp}/{rp} diffs={len(diffs)}")
        if diffs:
            print("  first_diffs:", diffs[:40])


if __name__ == "__main__":
    main(sys.argv)

