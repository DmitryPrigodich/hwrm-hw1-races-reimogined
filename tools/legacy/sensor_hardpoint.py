"""Add the native three-joint sensor attachment without replacing the ship rig."""

import re

from borrow_native_rig import chunks, form
from source_weapon_mounts import read_hierarchy, write_hierarchy


SENSOR_HARDPOINT = "NKRHyperspaceSensor"
NATIVE_HARDPOINT = "HardpointSensors1"
HARDPOINT_SUFFIXES = ("_Position", "_Direction", "_Rest")


def hierarchy(hod):
    return read_hierarchy(dict(chunks(dict(chunks(hod))[b"DTRM"], 12))[b"HIER"])


def require_hardpoint_joints(ship_text, hod):
    """The engine expands the .ship prefix; a bare Root is not an attachment."""
    names = {node["name"].casefold() for node in hierarchy(hod)}
    ship_text = re.sub(r"--\[\[.*?\]\]", "", ship_text, flags=re.S)
    ship_text = re.sub(r"--[^\n]*", "", ship_text)
    hardpoints = re.findall(r'StartShipHardPointConfig\(\s*NewShipType\s*,\s*"[^"]+"\s*,\s*"([^"]+)"', ship_text)
    for prefix in hardpoints:
        missing = [prefix + suffix for suffix in HARDPOINT_SUFFIXES
                   if (prefix + suffix).casefold() not in names]
        if missing:
            raise ValueError("Missing hardpoint joints: " + ", ".join(missing))
    return hardpoints


def add_sensor_hardpoint(original, donor):
    """Append a localized stock Hiigaran sensor mount, keeping all old indices."""
    nodes = hierarchy(original)
    if any(node["name"].startswith(SENSOR_HARDPOINT) for node in nodes):
        raise ValueError("Sensor attachment already exists; use the original stock HOD")
    native_nodes = {node["name"]: node for node in hierarchy(donor)}
    for suffix in HARDPOINT_SUFFIXES:
        native = native_nodes[NATIVE_HARDPOINT + suffix]
        node = dict(name=SENSOR_HARDPOINT + suffix,
                    parent=native["parent"].replace(NATIVE_HARDPOINT, SENSOR_HARDPOINT),
                    values=list(native["values"]))
        if suffix == "_Position":
            node["values"] = [0.0] * 9  # Hidden innate subsystem at the ship origin.
        nodes.append(node)
    output = []
    for kind, chunk in chunks(original):
        if kind == b"DTRM":
            chunk = form(kind, b"".join(write_hierarchy(nodes) if subkind == b"HIER" else subchunk
                                       for subkind, subchunk in chunks(chunk, 12)))
        output.append(chunk)
    return b"".join(output)
