"""Build a reversible, no-research two-faction preview over the HWVR demo.

Stock ship IDs/models stay stable. Output is project/local/fleet-preview/source;
the normal minicampaign source is not edited. Never starts the game.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path

from borrow_native_rig import chunks, form
from fleet_localization import english

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT / "local/fleet-preview/source"
REPORT = PROJECT / "local/fleet-preview/manifest.json"
NATIVE = PROJECT / "local/hw1ships/ship"
BASE = PROJECT / "local/hwrm-base"
IDENTITY = "VRC-two-faction-no-research-preview-v1"
DEFAULT_BATCH_FORMATION = "Batch_delta"
BATCH_FORMATION_OVERRIDES = {
    "defender": "SG_2x2Wall",
    "lightcorvette": "NFP_Batch_Diamond4",
    "attackbomber": "NFP_Batch_Claw5",
    "interceptor": "NFP_Batch_X5",
    "defensefighter": "NFP_Batch_X5",
}
FIGHTER_WEAPON_DAMAGE = {"scout": 0.6, "interceptor": 1.2}
PLATFORM_ICONS = {"defender", "defensefighter", "salvagecorvette", "repaircorvette"}
GENERATOR_STEMS = {"cloakgenerator", "gravwellgenerator", "sensorarray"}

# role, stock suffix, RU/order, hulls/squadron, build seconds, prototype HP.
SPECS = [
    ("Лёгкий истребитель", "scout", 450, 5, 30, 20),
    ("Перехватчик", "interceptor", 550, 5, 35, 40),
    ("Штурмовой бомбардировщик", "attackbomber", 550, 5, 40, 30),
    ("Стэлс-истребитель", "cloakedfighter", 700, 5, 45, 30),
    ("Лёгкий корвет", "lightcorvette", 600, 4, 45, 300),
    ("Тяжёлый корвет", "heavycorvette", 650, 3, 45, 400),
    ("Многопушечный корвет", "multiguncorvette", 650, 3, 45, 400),
    ("Минный корвет", "minelayercorvette", 800, 1, 45, 400),
    ("Фрегат поддержки", "supportfrigate", 650, 1, 50, 16000),
    ("Штурмовой фрегат", "assaultfrigate", 700, 1, 50, 16000),
    ("Ионный фрегат", "ioncannonfrigate", 700, 1, 45, 16000),
    ("Дронный фрегат", "dronefrigate", 1100, 1, 55, 16000),
    ("Лёгкий эсминец", "destroyer", 1350, 1, 110, 45000),
    ("Лёгкий ракетный эсминец", "missiledestroyer", 1500, 1, 120, 45000),
    ("Тяжёлый эсминец", "heavycruiser", 2800, 1, 165, 90000),
    ("Носитель", "carrier", 4000, 1, 100, 80000),
    ("Защитник", "defender", 450, 4, 35, 60),
    ("Абордажный корвет", "salvagecorvette", 250, 1, 25, None),
    ("Ремонтный корвет", "repaircorvette", 250, 1, 25, None),
    ("Генератор маскировки", "cloakgenerator", 500, 1, 45, None),
    ("Генератор гравитационного поля", "gravwellgenerator", 800, 1, 50, None),
    ("Сенсорная батарея", "sensorarray", 700, 1, 50, None),
    ("Сборщик ресурсов", "resourcecollector", 400, 1, 30, 2000),
    ("Ресурсный контроллер", "resourcecontroller", 800, 1, 45, 18000),
    ("Разведывательный зонд", "probe", 150, 1, 15, None),
    ("Датчик приближения", "proximitysensor", 250, 1, 20, None),
]
CAPS = {"Fighter": 14, "Corvette": 12, "Frigate": 21, "Capital": 15,
        "Destroyer": 5, "NFP_LightDestroyers": 10, "Carrier": 4, "Platform": 4,
        "NFP_Generators": 18, "CloakGenerator": 6, "GravWellGenerator": 6,
        "SensorArray": 6, "NFP_Engineers": 20, "ResourceCollector": 20,
        "ResourceController": 4, "Probe_hw1": 10, "ProximitySensor_hw1": 10,
        "MinelayerCorvette": 5, "NFP_Support": 4, "NFP_Special": 2, "Shipyard": 1,
        "Mothership": 1, "Research": 0, "Research1": 0, "Research2": 0,
        "Research3": 0, "Research4": 0, "Research5": 0}
STRINGS: dict[int, str] = {}
STRINGS_EN: dict[int, str] = {}


def ucs(text, en=None):
    key = 9960000 + len(STRINGS)
    STRINGS[key] = text
    STRINGS_EN[key] = english(text) if en is None else en
    return "$" + str(key)


def write(relative, text):
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="ascii")


def family_table(source, name, entries):
    """Add literal rows to a stock data table, without runtime Lua helpers.

    FamilyList loads in a restricted engine scope: even getn is unavailable.
    Native top-level table closing braces are unindented.
    """
    pattern = rf"(^\s*{re.escape(name)}\s*=\s*\{{\n)(.*?)(^\}})"
    def extend(match):
        return match[1] + match[2] + "\t-- Fleet preview additions.\n" + entries + match[3]
    result, count = re.subn(pattern, extend, source, count=1, flags=re.M | re.S)
    if count != 1: raise ValueError("Missing native family table: " + name)
    return result


def call(source, marker):
    start = source.index(marker)
    opening = source.index("(", start)
    depth, quoted = 0, False
    for i in range(opening, len(source)):
        ch = source[i]
        if ch == '"' and source[i - 1] != "\\":
            quoted = not quoted
        if not quoted:
            if ch == "(": depth += 1
            if ch == ")":
                depth -= 1
                if depth == 0: return source[start:i + 1] + ";"
    raise ValueError(marker)


def groups(stem):
    if stem in ("scout", "interceptor", "attackbomber", "cloakedfighter"):
        return ["Fighter"], "Fighter"
    if stem in ("lightcorvette", "heavycorvette", "multiguncorvette", "minelayercorvette"):
        return ["Corvette"] + (["MinelayerCorvette"] if stem == "minelayercorvette" else []), "Corvette"
    if stem.endswith("frigate"):
        sub = ["NFP_Support"] if stem == "supportfrigate" else ["NFP_Special"] if stem in ("dronefrigate", "fieldfrigate") else []
        return ["Frigate"] + sub, "Frigate"
    if stem in ("destroyer", "missiledestroyer"):
        return ["Capital", "NFP_LightDestroyers"], "Capital"
    if stem == "heavycruiser": return ["Capital", "Destroyer"], "Capital"
    if stem == "carrier": return ["Capital", "Carrier"], "Capital"
    if stem in ("defender", "defensefighter"): return ["Platform"], "Platform"
    if stem in ("salvagecorvette", "repaircorvette"): return ["NFP_Engineers"], "Platform"
    if stem in ("cloakgenerator", "gravwellgenerator", "sensorarray"):
        return ["NFP_Generators", {"cloakgenerator": "CloakGenerator", "gravwellgenerator": "GravWellGenerator", "sensorarray": "SensorArray"}[stem]], "NonCombat"
    return [{"resourcecollector": "ResourceCollector", "resourcecontroller": "ResourceController", "probe": "Probe_hw1", "proximitysensor": "ProximitySensor_hw1"}[stem]], "Resource" if stem.startswith("resource") else "NonCombat"


def build_entry(ident, title, priority):
    return ('{Type=Ship,ThingToBuild="' + ident + '",RequiredResearch="",'
            'RequiredShipSubSystems="",DisplayPriority=' + str(priority) + ',DisplayedName="' + title + '",Description="' + title + '"}')


def starting_fleets(race):
    from lupa.lua51 import LuaRuntime, lua_type
    def literal(value):
        if lua_type(value) == "table":
            return "{" + ",".join("[" + literal(k) + "]=" + literal(v) for k, v in value.items()) + "}"
        if value is None: return "nil"
        if isinstance(value, bool): return "1" if value else "0"
        if isinstance(value, (int, float)): return str(value)
        if isinstance(value, str): return json.dumps(value)
        raise TypeError(value)
    for source in (BASE / "scripts/startingfleets").glob(race.lower() + "*.lua"):
        vm = LuaRuntime()
        vm.execute(source.read_text(encoding="utf-8-sig"))
        data = vm.globals().PersistantData
        kept = [row for _, row in data.Squadrons.items() if "researchship" not in row.type.lower()]
        sizes = {race[:3].lower() + "_" + stem: count for _, stem, _, count, _, _ in SPECS}
        if race == "Taiidan": sizes["tai_defensefighter"] = 3
        for row in kept:
            # Stock skirmish uses a separate NoHold mothership script. Route
            # this no-science preview to the configured production ship.
            if row.type.lower() == race[:3].lower() + "_mothership_nohold":
                row.type = race[:3].lower() + "_mothership"
            # Native full fleets use size=N to request every hull in a squadron.
            row.size = sizes.get(row.type.lower(), 1)
        data.Squadrons = vm.table_from(kept)
        data.Research = vm.table()
        write("scripts/startingfleets/" + source.name, "PersistantData=" + literal(data) + "\n")


def build_ability(prefix, station=False):
    tag = "Kus" if prefix == "kus" else "Tai"
    families = f"Fighter_{tag}, Corvette_{tag}, Frigate_{tag}, Resource_{tag}, NonCombat_{tag}"
    if not station:
        families += f", SuperCap_{tag}"
        if prefix == "tai": families += ", Shipyard_Tai"
    displays = "Fighter, Corvette, Frigate, Capital, Platform, Resource, NonCombat, Utility"
    return f'addAbility(NewShipType,"CanBuildShips",1,"{families}","{displays}");'


def fighter_evidence(row):
    """Compare mounted barrels and damage bounds, without claiming combat DPS."""
    source = NATIVE / row["id"] / (row["id"] + ".ship")
    guns = re.findall(r'StartShipWeaponConfig\(NewShipType,"([^"]+)"', source.read_text())
    low, high, records = 0.0, 0.0, []
    for weapon in guns:
        path = BASE / "weapon" / weapon.lower() / (weapon.lower() + ".wepn")
        text = path.read_text()
        hit = re.search(r'AddWeaponResult\(NewWeaponType,"Hit","DamageHealth","Target",([\d.]+),([\d.]+)', text)
        if not hit: raise ValueError("Unsupported fighter damage result: " + str(path))
        a, b = float(hit[1]), float(hit[2])
        low += a; high += b
        accuracy = re.search(r'\{Fighter_hw1=([\d.]+)\}', text)
        records.append({"weapon": weapon, "damage_bounds": [a, b],
                        "fighter_hw1_accuracy": float(accuracy[1]),
                        "weapon_sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    mult = FIGHTER_WEAPON_DAMAGE[row["stem"]]
    return {"mounted_barrels": len(guns), "weapons": records,
            "unmodified_combined_discharge_damage": [low, high],
            "new_combined_discharge_damage": [low * mult, high * mult],
            "new_squadron_health": row["prototype_hp"] * row["squadron"],
            "new_ru": row["ru"], "damage_multiplier": mult,
            "not_dps": "No cadence, burst timing, accuracy, penetration, tactics, range or maneuver uptime model; no duel result implied."}


def prepare_formations():
    """Keep delta batch combat tuning; specialize the squadron layouts."""
    native = (BASE / "scripts/strike groups/sg_batch_delta.lua").read_text()
    text = native
    text = re.sub(r'^Name\s*=\s*"[^"]+"', 'Name="NFP_Batch_Diamond4"', text, count=1, flags=re.M)
    for key, label in (("Hint", "Ромб: четыре лёгких корвета, 1+2+1"), ("Title", "Ромб")):
        text = re.sub(rf'^{key}\s*=\s*"[^"]+"', key + '="' + ucs(label) + '"', text, count=1, flags=re.M)
    layout = '''strikegroup={
  OffsetFromParent={0,0,0},
  Children={
    {OffsetFromParent={-1,0,-1}},
    {OffsetFromParent={1,0,-1}},
    {OffsetFromParent={0,0,-2}},
  },
}
'''
    text, count = re.subn(r'^strikegroup\s*=.*\Z', lambda m: layout, text, count=1, flags=re.M | re.S)
    if count != 1: raise ValueError("Native batch layout not found")
    write("scripts/strike groups/nfp_batch_diamond4.lua", text)

    # Native Claw is internally named Movers, as also mapped by KAS_SetFormation.
    # Use its first four arms (and X's) as fixed batch slots, rather than a fleet
    # formation that could split/merge squadrons. Keep the existing combat tuning.
    for suffix, donor, alias in (("claw5", "sg_movers.lua", "Movers"),
                                  ("x5", "sg_x.lua", "X")):
        donor_text = (BASE / "scripts/strike groups" / donor).read_text()
        donor_layout = donor_text.split("strikegroup =", 1)[1]
        offsets = re.findall(r'OffsetFromParent\s*=\s*\{([^}]+)\}', donor_layout)
        if len(offsets) != 17: raise ValueError("Unexpected native four-arm layout: " + donor)
        # Each native arm has four nodes; take its first node only.
        slots = [offsets[i] for i in (1, 5, 9, 13)]
        layout = 'strikegroup={\n  OffsetFromParent={0,0,0},\n  FacingLimit=0.0,\n  Children={\n'
        layout += ''.join('    {OffsetFromParent={' + slot + '},FacingLimit=34.0},\n' for slot in slots)
        layout += '  },\n}\n'
        name = "NFP_Batch_Claw5" if suffix == "claw5" else "NFP_Batch_X5"
        text = re.sub(r'^Name\s*=\s*"[^"]+"', 'Name="' + name + '"', native, count=1, flags=re.M)
        text = re.sub(r'^UIAlias\s*=\s*"[^"]+"', 'UIAlias="' + alias + '"', text, count=1, flags=re.M)
        for key in ("Hint", "Title", "Hotkey"):
            value = re.search(r'^' + key + r'\s*=\s*([^\r\n]+)', donor_text, re.M)[1]
            text = re.sub(r'^' + key + r'\s*=[^\r\n]+', key + '=' + value, text, count=1, flags=re.M)
        text, count = re.subn(r'^strikegroup\s*=.*\Z', lambda m: layout, text, count=1, flags=re.M | re.S)
        if count != 1: raise ValueError("Native batch layout not found")
        write("scripts/strike groups/nfp_batch_" + suffix + ".lua", text)


def prepare_station():
    """Keep the station's entire rig/materials, add only carrier DOCK paths."""
    source = NATIVE / "tai_researchstation/tai_researchstation.hod"
    donor = NATIVE / "tai_carrier/tai_carrier.hod"
    dock = dict(chunks(dict(chunks(donor.read_bytes()))[b"DTRM"], 12))[b"DOCK"]
    output = []
    for kind, chunk in chunks(source.read_bytes()):
        if kind == b"DTRM":
            kept = [c for k, c in chunks(chunk, 12) if k != b"DOCK"]
            chunk = form(b"DTRM", b"".join(kept) + dock)
        output.append(chunk)
    path = ROOT / "ship/tai_researchstation/tai_researchstation.hod"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"".join(output))
    return {"source": str(source), "donor": str(donor), "copied": "DOCK only; original station hierarchy, geometry, textures and collision retained", "engine_tested": False}


def sandbox(prefix, rows, title):
    chapter = "Preview_Kushan" if prefix == "kus" else "Preview_Taiidan"
    race = "Kushan" if prefix == "kus" else "Taiidan"
    folder = f"leveldata/campaign/VRCFleetPreview/{chapter}"
    title_id = ucs(title)
    mother = prefix + "_mothership"
    lev = ["function DetermChunk()", f'addSquadron("NFP_Mother","{mother}",{{0,0,0}},0,{{0,0,0}},1,0)',
           'createSOBGroup("NFP_Mother")', 'addToSOBGroup("NFP_Mother","NFP_Mother")']
    for i, row in enumerate(rows):
        pos = [1800 + (i % 6) * 650, ((i // 6) % 2) * 350, -2300 + (i // 6) * 1500]
        if row["stem"] == "carrier": pos = [-2400, 0, 1600]
        if row["stem"] == "researchstation": pos = [-5000, 0, -1000]
        # Native batch size comes from buildBatch, not the obsolete SquadronSize.
        lev.append(f'addSquadron("NFP_Show_{i}","{row["id"]}",{{{pos[0]},{pos[1]},{pos[2]}}},0,{{0,0,0}},0,0)')
    for i in range(5):
        lev.append(f'addAsteroid("Asteroid_4",{{{(-1200 + i * 400)},-300,-3600}},2,0,0,0,0)')
    # Passive targets: human decides whether and when to attack.
    for i, target in enumerate(("hgn_interceptor", "hgn_assaultcorvette", "hgn_assaultfrigate", "hgn_destroyer")):
        lev.append(f'addSquadron("NFP_Target_{i}","{target}",{{{3000 + i * 1100},0,11000}},1,{{0,180,0}},1,0)')
    lev += ['addCamera("NFP_Home",{1800,0,1200},{9000,6500,-10000})',
            'setWorldBoundsInner({0,0,3000},{20000,12000,22000})', 'end',
            'function NonDetermChunk()', 'loadBackground("m01")',
            'setSensorsManagerCameraDistances(100,70000)', 'end', f'levelDesc="{title_id}"',
            'maxPlayers=2', 'player={}', f'player[0]={{id=0,name="",resources=100000,raceName="{race}",startPos=0}}',
            'player[1]={id=1,name="",resources=0,raceName="Hiigaran",startPos=0}']
    write(folder + "/" + chapter + ".level", "\n".join(lev) + "\n")
    message = ucs("Свободная проба флота. B — постройка, 1 — общий вид. Все проекты открыты; науки нет. Цели для стрельбы находятся впереди флота.")
    script = ['dofilepath("data:scripts/SCAR/SCAR_Util.lua")', 'function NFP_Home()',
              'Camera_Interpolate("here","NFP_Home",0)', 'end', 'function OnInit()',
              'CPU_Enable(1,0)', 'SobGroup_Create("NFP_Targets")']
    if prefix == "kus":
        script += [f'Player_RestrictBuildOption(0,"kus_drone{i}")' for i in range(14)]
    for i in range(4):
        script += [f'SobGroup_Create("NFP_TargetGroup_{i}")',
                   f'Player_FillShipsByType("NFP_TargetGroup_{i}",1,"{("hgn_interceptor", "hgn_assaultcorvette", "hgn_assaultfrigate", "hgn_destroyer")[i]}")',
                   f'SobGroup_AbilityActivate("NFP_TargetGroup_{i}",AB_Move,0)',
                   f'SobGroup_AbilityActivate("NFP_TargetGroup_{i}",AB_Attack,0)']
    for row in rows: script.append(f'Player_UnrestrictBuildOption(0,"{row["id"]}")')
    for i, row in enumerate(rows):
        if row["squadron"] <= 1: continue
        group = f"NFP_SquadCheck_{i}"
        script += [f'SobGroup_Create("{group}")',
                   f'Player_FillShipsByType("{group}",0,"{row["id"]}")',
                   f'print("NFP_BATCH: {row["id"]} configured_hulls={row["squadron"]} squadron_entries="..SobGroup_Count("{group}"))']
    script += ['UI_BindKeyEvent(ONEKEY,"NFP_Home")', 'NFP_Home()',
               f'Subtitle_Message("{message}",30)', 'print("NFP_PREVIEW: ready '+prefix+'; no engine validation implied by static checks")', 'end']
    write(folder + "/" + chapter + ".lua", "\n".join(script) + "\n")
    thumb = PROJECT / "minicampaign/leveldata/campaign/VastReachesMiniCampaign/M01_ProvingGrounds/M01_ProvingGrounds.dds"
    shutil.copy2(thumb, ROOT / (folder + "/" + chapter + ".dds"))
    return f'Mission[{1 if prefix == "kus" else 2}]={{postload=function() end,directory="{chapter}",level="{chapter}.level",postlevel=function() end,displayName="{title_id}",description="{message}"}}'


def prepare():
    if not ROOT.resolve().is_relative_to((PROJECT / "local").resolve()): raise RuntimeError("Unsafe output")
    marker = ROOT / "preview-id.txt"
    if ROOT.exists() and (not marker.exists() or marker.read_text().strip() != IDENTITY):
        raise RuntimeError("Unknown preview source directory")
    ROOT.mkdir(parents=True, exist_ok=True)
    marker.write_text(IDENTITY + "\n", encoding="ascii")
    shutil.copytree(PROJECT / "minicampaign", ROOT, dirs_exist_ok=True)
    STRINGS.clear()
    STRINGS_EN.clear()
    prepare_formations()
    report = {"identity": IDENTITY, "engine_tested": False, "ships": {}, "caps": CAPS,
              "default_batch_formation": DEFAULT_BATCH_FORMATION,
              "batch_formation_overrides": BATCH_FORMATION_OVERRIDES,
              "fighter_weapon_damage": FIGHTER_WEAPON_DAMAGE, "fighter_comparison": {},
              "base": "minicampaign", "limitations": ["Native weapons/abilities; HP, speeds and build times are initial tuning", "Taiidan defense fighter/field frigate are preview substitutions", "Station borrowed docking paths need an engine launch test"]}
    extra_caps = [("NFP_Generators", "Генераторы", 81), ("NFP_Engineers", "Инженеры", 201),
                  ("NFP_Support", "Фрегаты поддержки", 34), ("NFP_Special", "Специальные фрегаты", 35),
                  ("NFP_LightDestroyers", "Лёгкие эсминцы", 47)]
    family = (BASE / "scripts/familylist.lua").read_text(encoding="utf-8-sig")
    rows = ""
    for key, label, priority in extra_caps:
        rows += f'\t{{name="{key}",numParam={priority},stringParam="{ucs(label)}"}},\n'
    family = family_table(family, "unitcapsFamily", rows)
    # Keep generator sublimits directly after their shared pool, before probes.
    for key, priority in (("CloakGenerator", 82), ("GravWellGenerator", 83), ("SensorArray", 84)):
        pattern = rf'(name\s*=\s*"{key}"\s*,\s*numParam\s*=\s*)\d+'
        family, count = re.subn(pattern, lambda m: m[1] + str(priority), family)
        if count != 1: raise ValueError("Missing native supply priority: " + key)
    # Supply pools are independent of display tabs. Use existing UI tabs:
    # Platform for engineering corvettes/Defenders; NonCombat for generators.
    family = family_table(family, "buildFamily", '\t{name="Shipyard_Tai"},\n')
    # Heavy destroyers use the stock HW2 Destroyer pool/label. Light destroyers
    # receive their own additional pool because these races have no battlecruiser.
    write("scripts/familylist.lua", family)
    missions = []
    for prefix, race, name in (("kus", "Kushan", "Новокушане"), ("tai", "Taiidan", "Новотаиидане")):
        race_id = ucs(name)
        race_text = (BASE / f"scripts/races/{race.lower()}.lua").read_text()
        race_text = re.sub(r'Display_Name\s*=\s*"[^"]+"', f'Display_Name="{race_id}"', race_text)
        write(f"scripts/races/{race.lower()}.lua", race_text)
        rows, entries = [], []
        for index, (label, stem, price, count, seconds, hp) in enumerate(SPECS):
            if prefix == "tai" and stem == "cloakedfighter": stem, label, count = "defensefighter", "Защитный истребитель", 3
            if prefix == "tai" and stem == "dronefrigate": stem, label = "fieldfrigate", "Фрегат защитного поля"
            ident = prefix + "_" + stem
            original = (NATIVE / ident / (ident + ".ship")).read_text(encoding="utf-8-sig")
            text = re.sub(r'^setSupplyValue\([^\n]+\)\s*;?\s*$', "", original, flags=re.M)
            if stem == "carrier":
                old = call(text, 'addAbility(NewShipType,"CanBuildShips"')
                text = text.replace(old.rstrip(';'), build_ability(prefix, station=True).rstrip(';'))
            cap_names, display = groups(stem)
            title = ucs(label)
            text += '\n-- No-research fleet preview: last assignments override stock tuning.\n'
            text += f'NewShipType.displayedName="{title}"\nNewShipType.sobDescription="{title}"\n'
            # Current HWRM uses buildBatch for one build order containing N
            # craft. SquadronSize and the old stance-formation fields are not
            # registered by this engine; copying Classic's fields was inert.
            text += f'NewShipType.SquadronSize=1\nNewShipType.buildBatch={count}\nNewShipType.buildCost={price}\nNewShipType.buildTime={seconds}\nNewShipType.DisplayFamily="{display}"\n'
            formation = BATCH_FORMATION_OVERRIDES.get(stem, DEFAULT_BATCH_FORMATION) if count > 1 else None
            if formation:
                text += f'NewShipType.batchFormation="{formation}"\n'
            if hp is not None: text += f"NewShipType.maxhealth={hp}\n"
            if stem in FIGHTER_WEAPON_DAMAGE:
                mult = FIGHTER_WEAPON_DAMAGE[stem]
                text += f'AddShipMultiplier(NewShipType,"WeaponDamage","ThisShipOnly","Linear",{mult},{mult},0);\n'
            if stem in PLATFORM_ICONS: text += 'NewShipType.TOIcon="Hexagon"\n'
            if stem in GENERATOR_STEMS: text += 'NewShipType.TOIcon="Diamond"\n'
            for cap in cap_names: text += f'setSupplyValue(NewShipType,"{cap}",1.0);\n'
            if stem in ("salvagecorvette", "repaircorvette"):
                text += f'NewShipType.BuildFamily="NonCombat_{"Kus" if prefix == "kus" else "Tai"}"\n'
            if stem == "resourcecontroller":
                text += f'NewShipType.BuildFamily="SuperCap_{"Kus" if prefix == "kus" else "Tai"}"\n'
            if stem == "carrier": text += 'setConcurrentBuildLimit(NewShipType,0,1);\n'
            if stem == "sensorarray": text += 'NewShipType.detectionStrength=4\n'
            if stem == "heavycruiser":
                text += 'NewShipType.AttackFamily="SmallCapitalShip"\nNewShipType.AvoidanceFamily="Capital"\nNewShipType.ArmourFamily="HeavyArmour"\nNewShipType.TOIcon="Parallelogram"\nAddShipMultiplier(NewShipType,"WeaponDamage","ThisShipOnly","Linear",0.35,0.35,0);\n'
            write(f"ship/{ident}/{ident}.ship", text)
            row = dict(id=ident, stem=stem, title=title, ru=price, squadron=count, build_time=seconds,
                       prototype_hp=hp, caps=cap_names, display=display, batch_formation=formation,
                       weapon_damage_mult=FIGHTER_WEAPON_DAMAGE.get(stem, 0.35 if stem == "heavycruiser" else 1), source_sha256=hashlib.sha256(original.encode()).hexdigest())
            rows.append(row)
            entries.append(build_entry(ident, title, index * 10 + 10))
        mother = prefix + "_mothership"
        text = (NATIVE / mother / (mother + ".ship")).read_text(encoding="utf-8-sig")
        text = text.replace(call(text, 'addAbility(NewShipType,"CanBuildShips"').rstrip(';'), build_ability(prefix).rstrip(';'))
        text += '\nsetConcurrentBuildLimit(NewShipType,0,1);\n'
        write(f"ship/{mother}/{mother}.ship", text)
        if prefix == "tai":
            ident, title = "tai_researchstation", ucs("Исследовательская станция")
            carrier = (NATIVE / "tai_carrier/tai_carrier.ship").read_text(encoding="utf-8-sig")
            text = (NATIVE / ident / (ident + ".ship")).read_text(encoding="utf-8-sig")
            text = re.sub(r'^setSupplyValue\([^\n]+\)\s*;?\s*$', "", text, flags=re.M)
            text += '\n-- Experimental station production using native Taiidan carrier dock paths.\n'
            text += f'NewShipType.displayedName="{title}"\nNewShipType.sobDescription="{title}"\nNewShipType.BuildFamily="Shipyard_Tai"\nNewShipType.DockFamily="Shipyard"\nNewShipType.buildCost=4000\nNewShipType.buildTime=100\n'
            text += 'addAbility(NewShipType,"CanDock",1,0);\naddAbility(NewShipType,"CanLaunch");\n'
            text += call(carrier, 'addAbility(NewShipType,"ShipHold"') + "\n"
            text += "\n".join(l for l in carrier.splitlines() if l.startswith("NewShipType.launch") or l.startswith("NewShipType.dock")) + "\n"
            text += build_ability(prefix, station=True) + '\nsetConcurrentBuildLimit(NewShipType,0,1);\nsetSupplyValue(NewShipType,"Shipyard",1.0);\n'
            write(f"ship/{ident}/{ident}.ship", text)
            report["station_rig"] = prepare_station()
            row = dict(id=ident, stem="researchstation", title=title, ru=4000, squadron=1, build_time=100, caps=["Shipyard"], display="Utility")
            rows.append(row); entries.append(build_entry(ident, title, 500))
        if prefix == "kus":
            # Native drone-frigate scripts create these internal hulls. Register
            # them but keep them out of human construction via restrictions.
            for i in range(14): entries.append(build_entry(f"kus_drone{i}", "$11024", 0))
        write(f"scripts/races/{race}/scripts/def_build.lua", 'Ship=0\nSubSystem=1\nbuild={\n'+',\n'.join(entries)+'\n}\n')
        write(f"scripts/races/{race}/scripts/def_research.lua", '-- Preview intentionally has no technologies or research queue.\nresearch={}\n')
        caps = "\n".join(f'supplyLimit("{k}",{v});' for k, v in CAPS.items()) + "\n"
        for key in CAPS:
            caps += f'supplyShow("{key}","{("Never" if key.startswith("Research") or key == "Mothership" else "NotEmpty")}");\n'
        for mode in ("small", "normal", "large", "huge"):
            write(f"scripts/races/{race}/deathmatch/unitcaps/{mode}.lua", caps)
        write(f"scripts/races/{race}/singleplayer/unitcaps/singleplayer.lua", caps)
        # Do not let native deathmatch presets reintroduce research ships.
        restrictions = ",".join(prefix + "_researchship" + s for s in ("", "_1", "_2", "_3", "_4", "_5"))
        if prefix == "kus": restrictions += "," + ",".join(f"kus_drone{i}" for i in range(14))
        props = 'Number_Properties_Priority=20\nNumber_Properties={dm_challenge_research_baseline=0}\nString_Properties_Priority=20\nString_Properties={dm_build_restrict="'+restrictions+'",dm_research_restrict="",dm_allresearch_build_restrict="'+restrictions+'",dm_allresearch_research_restrict=""}\n'
        write(f"scripts/races/{race}/deathmatch/props/gbx.lua", props)
        starting_fleets(race)
        report["ships"][prefix] = rows
        report["fighter_comparison"][prefix] = {row["stem"]: fighter_evidence(row) for row in rows if row["stem"] in FIGHTER_WEAPON_DAMAGE}
        missions.append(sandbox(prefix, rows, name + " — свободная проба"))
    title = ucs("Новокушане и Новотаиидане — проба флота")
    choose = ucs("Выбрать расу")
    campaign = f'displayName="{title}"\ncontentType=2\ncontentName="VRCFleetPreview"\ncontentOrdered=0\ncontentChooseText="{choose}"\ncontentThumbName="{title}"\ncontentThumbDesc="{title}"\ncontentSort=0.3\ncontentRules="SinglePlayer"\nExtFilter="campaign_vast_reaches,campaign_gbx"\nMission={{}}\n' + "\n".join(missions) + "\n"
    write("leveldata/campaign/VRCFleetPreview.campaign", campaign)
    shutil.copy2(PROJECT / "minicampaign/leveldata/campaign/VastReachesMiniCampaign.dds", ROOT / "leveldata/campaign/VRCFleetPreview.dds")
    # Keep legacy HWVR chapter scripts usable with this temporary no-tech overlay.
    common = ROOT / "leveldata/campaign/VastReachesMiniCampaign/VRC_Common.lua"
    source = common.read_text()
    source = re.sub(r'^\s*Player_GrantResearchOption\([^\n]+\)\s*$', '    -- Research grant omitted only in the no-research preview copy.', source, flags=re.M)
    common.write_text(source, encoding="ascii")
    data = ROOT / "leveldata/campaign/VastReachesMiniCampaign/VRC_Data.lua"
    text = data.read_text() + '\n-- Preview has no research definitions.\nVRC_AllResearch={}\n'
    text += 'VRC_AllBuilds={' + ','.join('"'+r['id']+'"' for r in report['ships']['kus']) + '}\n'
    data.write_text(text, encoding="ascii")
    for lang in ("Russian", "English"):
        path = ROOT / f"locale/{lang}/vrcampaign.ucs"
        text = path.read_text(encoding="utf-16")
        strings = STRINGS if lang == "Russian" else STRINGS_EN
        text += "\n" + "\n".join(f"{key}\t{value}" for key, value in strings.items()) + "\n"
        path.write_text(text, encoding="utf-16")
    report["strings"] = STRINGS
    report["strings_en"] = STRINGS_EN
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"source": str(ROOT), "kushan_projects": len(report["ships"]["kus"]), "taiidan_projects": len(report["ships"]["tai"]), "science": False, "game_launched": False}))


if __name__ == "__main__":
    prepare()
