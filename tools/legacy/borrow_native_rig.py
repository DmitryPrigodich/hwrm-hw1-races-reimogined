"""Borrow native hardpoints and dock paths for temporary gameplay archetypes.

Keep the newly compiled geometry, texture pool and collision hull. Only named
joint, docking and marker metadata comes from the selected installed ship.
"""

import struct
from pathlib import Path


def chunks(data, begin=0, end=None):
    end = len(data) if end is None else end
    offset = begin
    while offset < end:
        if offset+8 > end:
            raise ValueError("Truncated HOD chunk header")
        tag = data[offset:offset+4]
        size = struct.unpack_from(">I", data, offset+4)[0]
        finish = offset+8+size
        if finish > end:
            raise ValueError("Truncated HOD chunk body")
        kind = data[offset+8:offset+12] if tag == b"FORM" else tag
        yield kind, data[offset:finish]
        offset = finish


def form(kind, content):
    payload = kind+content
    return b"FORM"+struct.pack(">I",len(payload))+payload


def borrow(target: Path, native: Path):
    native_chunks = dict(chunks(native.read_bytes()))
    source = dict(chunks(native_chunks[b"DTRM"],12))
    required = [kind for kind in (b"HIER",b"DOCK",b"MRKS") if kind in source]
    output = []
    for kind, chunk in chunks(target.read_bytes()):
        if kind == b"DTRM":
            # Engine shape joint indexes belong to the original exported rig.
            kept = [c for k,c in chunks(chunk,12) if k not in (b"HIER",b"DOCK",b"MRKS",b"ETSH",b"BURN")]
            chunk = form(b"DTRM", b"".join([source[k] for k in required]+kept))
        output.append(chunk)
    target.write_bytes(b"".join(output))
    return dict(source=str(native),chunks=[k.decode("ascii") for k in required],
                engine_effects="Source engine shape indexes omitted with borrowed hierarchy")
