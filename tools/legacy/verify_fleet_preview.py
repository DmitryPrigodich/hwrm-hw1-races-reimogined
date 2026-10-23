"""Static/data and strict API-mock checks. Does not launch or validate HWRM."""
import json
import re
from pathlib import Path

from lupa.lua51 import LuaRuntime

from borrow_native_rig import chunks
from prepare_fleet_preview import (ROOT, REPORT, PROJECT, NATIVE, CAPS, BASE, DEFAULT_BATCH_FORMATION,
                                  BATCH_FORMATION_OVERRIDES, FIGHTER_WEAPON_DAMAGE, PLATFORM_ICONS, GENERATOR_STEMS)


def ship_config(path):
    lua = LuaRuntime(unpack_returned_tuples=True)
    g = lua.globals()
    lua.execute('setmetatable(_G,{__index=function(t,k) return function(...) end end})')
    config, supply, calls = lua.table(), {}, []
    g.StartShipConfig = lambda: config
    g.getShipNum = lambda table, key, default: default
    g.getShipStr = lambda table, key, default: default
    g.setSupplyValue = lambda table, family, value: supply.__setitem__(family, value)
    g.addAbility = lambda *args: calls.append(args[1:])
    g.setConcurrentBuildLimit = lambda table, kind, count: calls.append(("Concurrent", kind, count))
    g.AddShipMultiplier = lambda table, *args: calls.append(("Multiplier",) + args)
    lua.execute(path.read_text(encoding="ascii"))
    return config, supply, calls


def verify():
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    lua = LuaRuntime()
    # Match FamilyList's data-only engine scope. Do not inject helper aliases:
    # the previous getn=table.getn hid the real engine's nil-getn load error.
    lua.execute('getn=nil; table=nil; string=nil; math=nil')
    lua.execute((ROOT / "scripts/familylist.lua").read_text())
    families = {row.name for _, row in lua.globals().unitcapsFamily.items()}
    assert len(families) == 61, len(families)
    cap_order = {row.name: row.numParam for row in lua.globals().unitcapsFamily.values()}
    assert cap_order["Frigate"] < cap_order["NFP_Support"] < cap_order["NFP_Special"] < cap_order["Capital"]
    active_caps = sorted((name for name, value in CAPS.items() if value > 0), key=cap_order.__getitem__)
    index = active_caps.index("Frigate")
    assert active_caps[index:index + 3] == ["Frigate", "NFP_Support", "NFP_Special"]
    index = active_caps.index("NFP_Generators")
    assert active_caps[index:index + 4] == ["NFP_Generators", "CloakGenerator", "GravWellGenerator", "SensorArray"]
    assert CAPS["Platform"] == 4 and "Defenders" not in CAPS
    assert CAPS["Destroyer"] == 5 and CAPS["NFP_LightDestroyers"] == 10 and CAPS["Capital"] == 15
    assert "HeavyCruiser" not in CAPS
    registries = {}
    for key in ("buildFamily", "displayFamily", "unitcapsFamily"):
        rows = list(lua.globals()[key].values())
        names = {r.name for r in rows}
        assert len(names) == len(rows), (key, "duplicate family")
        registries[key] = names
    priorities = [r.numParam for r in lua.globals().displayFamily.values()]
    assert len(set(priorities)) == len(priorities), "duplicate display priority"
    native_families = LuaRuntime()
    native_families.execute((BASE / "scripts/familylist.lua").read_text(encoding="utf-8-sig"))
    assert registries["displayFamily"] == {r.name for r in native_families.globals().displayFamily.values()}, "new build display categories"
    original_ui = PROJECT / "minicampaign/ui"
    generated_ui = ROOT / "ui"
    original_paths = {p.relative_to(original_ui) for p in original_ui.rglob("*") if p.is_file()}
    generated_paths = {p.relative_to(generated_ui) for p in generated_ui.rglob("*") if p.is_file()}
    assert generated_paths == original_paths, "new UI files or icons introduced"
    assert all((original_ui / p).read_bytes() == (generated_ui / p).read_bytes() for p in original_paths)
    native_batch = (BASE / "scripts/strike groups/sg_batch_delta.lua").read_text()
    assert re.search(r'^Name\s*=\s*"' + re.escape(DEFAULT_BATCH_FORMATION) + '"', native_batch, re.M)
    assert re.search(r'^BatchRestrict\s*=\s*1\b', native_batch, re.M)
    assert report["default_batch_formation"] == DEFAULT_BATCH_FORMATION
    formations = {}
    for base in (BASE, ROOT):
        for path in (base / "scripts/strike groups").glob("*.lua"):
            text = path.read_text()
            name = re.search(r'^Name\s*=\s*"([^"]+)"', text, re.M)
            if name: formations[name[1]] = (path, text)
    assert report["batch_formation_overrides"] == BATCH_FORMATION_OVERRIDES
    for name in set(BATCH_FORMATION_OVERRIDES.values()):
        assert name in formations, name
        assert re.search(r'^BatchRestrict\s*=\s*1\b', formations[name][1], re.M)
    wall_vm = LuaRuntime(); wall_vm.execute(formations["SG_2x2Wall"][1])
    assert wall_vm.globals().UIAlias == "Wall" and len(wall_vm.globals().strikegroup.Children) == 3
    diamond_vm = LuaRuntime(); diamond_vm.execute(formations["NFP_Batch_Diamond4"][1])
    slots = [tuple(row.OffsetFromParent.values()) for row in diamond_vm.globals().strikegroup.Children.values()]
    assert set(slots) == {(-1, 0, -1), (1, 0, -1), (0, 0, -2)}
    # Layout-only delta fork must retain combat multipliers and batch behavior.
    diamond_prefix = formations["NFP_Batch_Diamond4"][1].split("strikegroup=")[0]
    native_prefix = native_batch.split("strikegroup =")[0]
    for key in ("DeathDamage", "FriendlyFire", "PopDecay", "StanceGrouping"):
        pattern = rf'^{key}\s*=([^\n]+)'
        assert re.search(pattern, diamond_prefix, re.M)[1] == re.search(pattern, native_prefix, re.M)[1], key
    for name, donor, alias in (("NFP_Batch_Claw5", "sg_movers.lua", "Movers"),
                                ("NFP_Batch_X5", "sg_x.lua", "X")):
        batch_vm, donor_vm = LuaRuntime(), LuaRuntime()
        batch_text = formations[name][1]
        batch_vm.execute(batch_text)
        donor_vm.execute((BASE / "scripts/strike groups" / donor).read_text())
        assert batch_vm.globals().UIAlias == alias and batch_vm.globals().LayoutMode == "Nodes"
        children = batch_vm.globals().strikegroup.Children
        assert len(children) == 4
        for i in range(1, 5):
            assert tuple(children[i].OffsetFromParent.values()) == tuple(donor_vm.globals().strikegroup.Children[i].OffsetFromParent.values())
            assert children[i].FacingLimit == donor_vm.globals().strikegroup.Children[i].FacingLimit
            assert children[i].Children is None
        assert batch_text.split("strikegroup=")[0].split("BatchRestrict")[1] == native_batch.split("strikegroup =")[0].split("BatchRestrict")[1]
    def check_families(ident, config, calls):
        assert config.BuildFamily in registries["buildFamily"], (ident, config.BuildFamily)
        assert config.DisplayFamily in registries["displayFamily"], (ident, config.DisplayFamily)
        for c in calls:
            if c[0] == "CanBuildShips":
                for arg, key in ((c[2], "buildFamily"), (c[3], "displayFamily")):
                    assert {s.strip() for s in arg.split(",")} <= registries[key], (ident, arg)
    for prefix, race in (("kus", "Kushan"), ("tai", "Taiidan")):
        rows = report["ships"][prefix]
        expected_sizes = {r["id"]: r["squadron"] for r in rows}
        glossary = json.loads((PROJECT / "localization/glossary.json").read_text(encoding="utf-8"))
        names_ru = {r["native_type"]: r["ru"] for r in glossary if r.get("native_type")}
        lua.execute((ROOT / f"scripts/races/{race}/scripts/def_build.lua").read_text())
        entries = list(lua.globals().build.values())
        names = {row.ThingToBuild.lower() for row in entries}
        assert len(names) == len(entries)
        assert not any("researchship" in name for name in names)
        assert not any(row.RequiredResearch or row.RequiredShipSubSystems for row in entries)
        assert {row["id"] for row in rows} <= names
        for row in rows:
            ident = row["id"]
            config, supplies, calls = ship_config(ROOT / f"ship/{ident}/{ident}.ship")
            check_families(ident, config, calls)
            assert config.buildBatch == row["squadron"] or ident == "tai_researchstation"
            if row["squadron"] > 1:
                assert config.SquadronSize == 1
                assert config.batchFormation == row["batch_formation"] == BATCH_FORMATION_OVERRIDES.get(row["stem"], DEFAULT_BATCH_FORMATION)
            if row["stem"] == "scout": assert config.buildBatch == 5
            if row["stem"] == "defensefighter": assert config.buildBatch == 3
            if row["stem"] == "lightcorvette": assert config.buildBatch == 4 and config.buildCost == 600
            if row["stem"] in FIGHTER_WEAPON_DAMAGE:
                mult = FIGHTER_WEAPON_DAMAGE[row["stem"]]
                assert ("Multiplier", "WeaponDamage", "ThisShipOnly", "Linear", mult, mult, 0) in calls
            key = ident if prefix == "kus" else "kus_" + row["stem"]
            if key in names_ru: assert report["strings"][row["title"].lstrip("$")] == names_ru[key], ident
            assert config.buildCost == row["ru"] and config.buildTime == row["build_time"]
            assert set(supplies) == set(row["caps"]), (ident, supplies)
            assert all(name in families for name in supplies)
            assert all(v == 1 for v in supplies.values())
            if row.get("prototype_hp") is not None: assert config.maxhealth == row["prototype_hp"]
            if row["stem"] == "heavycruiser":
                assert config.maxhealth == 90000 and config.ArmourFamily == "HeavyArmour"
                destroyer, _, _ = ship_config(PROJECT / "local/hw2ships/ship/hgn_destroyer/hgn_destroyer.ship")
                assert config.TOIcon == destroyer.TOIcon == "Parallelogram"
                assert config.AttackFamily == destroyer.AttackFamily == "SmallCapitalShip"
                assert config.AvoidanceFamily == destroyer.AvoidanceFamily == "Capital"
                assert supplies == {"Capital": 1, "Destroyer": 1}
            if row["stem"] in ("destroyer", "missiledestroyer"):
                assert supplies == {"Capital": 1, "NFP_LightDestroyers": 1}
            if row["stem"] in PLATFORM_ICONS: assert config.TOIcon == "Hexagon"
            if row["stem"] in GENERATOR_STEMS: assert config.TOIcon == "Diamond"
            # Native build UI exposes only these display-category buttons.
            ui = (PROJECT / "local/hwrm-base/ui/newui/build/finalbuild.lua").read_text()
            tabs = set(re.findall(r'GetFacilityButton\("([^"]+)"', ui))
            assert config.DisplayFamily in tabs, (ident, "no UI tab", config.DisplayFamily)
            if row["stem"] in ("defender", "defensefighter", "salvagecorvette", "repaircorvette"):
                assert config.DisplayFamily == "Platform"
            if row["stem"] in ("defender", "defensefighter"):
                assert supplies == {"Platform": 1}, (ident, supplies)
            if row["stem"] in ("salvagecorvette", "repaircorvette"):
                assert supplies == {"NFP_Engineers": 1}, (ident, supplies)
            if row["stem"] in ("cloakgenerator", "gravwellgenerator", "sensorarray"):
                assert config.DisplayFamily == "NonCombat"
            assert (NATIVE / ident / (ident + ".hod")).exists(), ident
            if ident.endswith("resourcecontroller"): assert config.BuildFamily.startswith("SuperCap_")
            if ident.endswith("carrier") or ident == "tai_researchstation":
                build = [c for c in calls if c[0] == "CanBuildShips"][-1]
                assert "SuperCap" not in build[2], build
                assert "Utility" in build[3] and "Platform" in build[3]
                assert ("Concurrent", 0, 1) in calls
        light = report["fighter_comparison"][prefix]["scout"]
        heavy = report["fighter_comparison"][prefix]["interceptor"]
        assert light["mounted_barrels"] == 2 and heavy["mounted_barrels"] == 1
        assert light["new_squadron_health"] == 100 and heavy["new_squadron_health"] == 200
        assert light["new_ru"] == 450 and heavy["new_ru"] == 550
        assert sum(heavy["new_combined_discharge_damage"]) > 1.9 * sum(light["new_combined_discharge_damage"])
        config, _, calls = ship_config(ROOT / f"ship/{prefix}_mothership/{prefix}_mothership.ship")
        check_families(prefix + "_mothership", config, calls)
        build = [c for c in calls if c[0] == "CanBuildShips"][-1]
        assert "SuperCap" in build[2]
        assert ("Concurrent", 0, 1) in calls
        if prefix == "tai": assert "Shipyard_Tai" in build[2]
        lua.execute((ROOT / f"scripts/races/{race}/scripts/def_research.lua").read_text())
        assert len(lua.globals().research) == 0
        for mode in ("small", "normal", "large", "huge"):
            values = {}
            lua.globals().supplyLimit = lambda name, value: values.__setitem__(name, value)
            lua.globals().supplyShow = lambda *a: None
            lua.execute((ROOT / f"scripts/races/{race}/deathmatch/unitcaps/{mode}.lua").read_text())
            assert values == CAPS
        for path in (ROOT / "scripts/startingfleets").glob(race.lower() + "*.lua"):
            lua.execute(path.read_text())
            data = lua.globals().PersistantData
            assert len(data.Research) == 0
            assert not any("researchship" in row.type.lower() for _, row in data.Squadrons.items())
            for _, row in data.Squadrons.items():
                assert not row.type.lower().endswith("_nohold")
                assert row.size == expected_sizes.get(row.type.lower(), 1), (path, row.type, row.size)
    # Docking patch must not change station geometry, textures or hierarchy.
    original = dict(chunks((NATIVE / "tai_researchstation/tai_researchstation.hod").read_bytes()))
    changed = dict(chunks((ROOT / "ship/tai_researchstation/tai_researchstation.hod").read_bytes()))
    for name in original:
        if name != b"DTRM": assert original[name] == changed[name], name
    before = dict(chunks(original[b"DTRM"], 12))
    after = dict(chunks(changed[b"DTRM"], 12))
    for name in before: assert before[name] == after[name], name
    assert b"DOCK" in after
    # Run both actual map/setup scripts in a strict mock, never a game process.
    for prefix, chapter in (("kus", "Preview_Kushan"), ("tai", "Preview_Taiidan")):
        vm = LuaRuntime(unpack_returned_tuples=True)
        g = vm.globals()
        ships, restricted, enabled, messages, spawn_requests = [], set(), set(), [], []
        def noop(*a): pass
        def add_squad(name, ident, *args):
            ships.append(ident)
            spawn_requests.append((name, ident, args))
        callbacks = {"addSquadron": add_squad,
                     "createSOBGroup": noop, "addToSOBGroup": noop, "addAsteroid": noop,
                     "addCamera": noop, "setWorldBoundsInner": noop, "loadBackground": noop,
                     "setSensorsManagerCameraDistances": noop, "CPU_Enable": noop,
                     "SobGroup_Create": noop, "Player_FillShipsByType": noop, "SobGroup_Count": lambda *a: 0,
                     "SobGroup_AbilityActivate": noop, "UI_BindKeyEvent": noop,
                     "Camera_Interpolate": noop, "Subtitle_Message": lambda *a: messages.append(a),
                     "Player_RestrictBuildOption": lambda player, name: restricted.add(name),
                     "Player_UnrestrictBuildOption": lambda player, name: enabled.add(name),
                     "print": noop, "dofilepath": lambda path: None if path == "data:scripts/SCAR/SCAR_Util.lua" else (_ for _ in ()).throw(AssertionError(path))}
        for key, value in callbacks.items(): g[key] = value
        for key in ("ONEKEY", "AB_Move", "AB_Attack"): g[key] = key
        folder = ROOT / "leveldata/campaign/VRCFleetPreview" / chapter
        vm.execute((folder / (chapter + ".level")).read_text())
        g.DetermChunk(); g.NonDetermChunk()
        vm.execute((folder / (chapter + ".lua")).read_text()); g.OnInit()
        assert g.player[0].resources == 100000
        assert not any("researchship" in name for name in ships)
        assert all(args[3] == 0 for name, ident, args in spawn_requests if name.startswith("NFP_Show_")), "preview requests partial one-hull units"
        assert enabled == {r["id"] for r in report["ships"][prefix]}
        if prefix == "kus": assert restricted == {f"kus_drone{i}" for i in range(14)}
        assert len(messages) == 1
    result = {"status": "passed", "data_ships": 53, "sandbox_scripts": 2,
              "research_entries": 0, "science_ships": 0, "engine_tested": False,
              "station_geometry_preserved": True, "unitcap_families": len(families)}
    result["family_registry_without_helper_aliases"] = True
    result["native_ui_tabs_checked"] = True
    result["starting_squadron_sizes_checked"] = True
    result["stock_ui_and_display_categories_preserved"] = True
    result["heavy_destroyer_tactical_icon_checked"] = True
    result["platform_pool_separate_from_fighters_and_engineers"] = True
    result["frigate_subcaps_order_checked"] = True
    result["generator_subcaps_order_checked"] = True
    result["fighter_roles_and_damage_multipliers_checked"] = True
    result["wall_and_four_corvette_diamond_checked"] = True
    result["destroyer_class_matches_hw2_checked"] = True
    result["platform_utility_tactical_icons_checked"] = True
    (PROJECT / "local/fleet-preview/verification.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__": verify()
