"""Check the generated research graph and Lua data; not native engine validation."""
import json
import re
from pathlib import Path

from lupa.lua51 import LuaRuntime

from apply_novokushan_research import read_lua_table
from novokushan_research_design import closure, make_design, path_cost
from prepare_fleet_preview import BASE, CAPS, PROJECT, ROOT, REPORT
from borrow_native_rig import chunks
from sensor_hardpoint import SENSOR_HARDPOINT, hierarchy, require_hardpoint_joints
from verify_fleet_preview import ship_config


def verify():
    design = make_design()
    manifest = json.loads(REPORT.read_text(encoding="utf-8"))
    techs = {t["id"]: t for t in design["technologies"]}
    assert len(techs) == len(design["technologies"]) == 57
    assert len(closure(design, list(techs))) == 57  # Cycles/unknown dependencies fail.
    research = read_lua_table(ROOT / "scripts/races/Kushan/scripts/def_research.lua", "research")
    by_name = {r["Name"]: r for r in research}
    assert len(by_name) == len(research)
    assert len(read_lua_table(ROOT / "scripts/races/Taiidan/scripts/def_research.lua", "research")) == 0
    modules = {m["id"]: m for m in design["modules"]}
    assert sum(m["cost"] for m in modules.values()) == 2200
    for tech in techs.values():
        row = by_name[tech["id"]]
        assert row["RequiredResearch"] == " & ".join(tech["requires"])
        assert row["RequiredSubSystems"] == modules[tech["module"]]["subsystem"]
        assert row["Cost"] == tech["cost"] > 0 and row["Time"] == tech["time"] > 0
        assert row["TargetName"] == modules[tech["module"]]["ship"]
        for i, fx in enumerate(tech["effects"]):
            effect = by_name[tech["id"] + "_Effect" + str(i + 1)]
            assert effect["Cost"] == effect["Time"] == 0 and effect["RequiredResearch"] == tech["id"]
            assert effect["RequiredSubSystems"] == ""  # Learned effects survive loss of a lab.
            assert effect["TargetName"] == fx["target"] and effect["UpgradeName"] == fx["name"]
            assert effect["UpgradeType"] == (1 if fx["kind"] == "ability" else 0)
            if fx["value"] is not None: assert effect["UpgradeValue"] == fx["value"]
            assert not effect["DisplayedName"]
    build = read_lua_table(ROOT / "scripts/races/Kushan/scripts/def_build.lua", "build")
    builds = {r["ThingToBuild"].lower(): r for r in build}
    for ident, requirements in design["requirements"].items():
        assert builds[ident]["RequiredResearch"] == " & ".join(requirements)
        assert builds[ident]["RequiredShipSubSystems"] == ""
    assert "NKR_Minelaying" in builds["kus_minelayercorvette"]["RequiredResearch"]
    assert "FastTracking" not in builds["kus_minelayercorvette"]["RequiredResearch"]
    assert techs["NKR_MultigunCorvetteSpeed"]["effects"][0]["target"] == "kus_multiguncorvette"
    assert "NKR_HeavyGuns" not in builds["kus_heavycruiser"]["RequiredResearch"]
    for ident in ("kus_attackbomber", "kus_assaultfrigate"):
        assert "NKR_PlasmaWeapons" in builds[ident]["RequiredResearch"]
        assert "NKR_PlasmaBombs" not in builds[ident]["RequiredResearch"]
    assert techs["NKR_PlasmaWeapons"]["effects"] == []
    assert techs["NKR_PlasmaBombs"]["requires"] == ["NKR_PlasmaWeapons"]
    assert {(fx["target"], fx["name"]) for fx in techs["NKR_PlasmaBombs"]["effects"]} == {
        ("kus_attackbomber", "UseSpecialWeaponsInNormalAttack"),
        ("kus_assaultfrigate", "UseSpecialWeaponsInNormalAttack")}
    assert "tai_researchstation" not in builds and "kus_researchstation" not in builds
    caps = manifest["science_caps"]["kus"]
    for module in modules.values():
        assert builds[module["ship"]]["RequiredResearch"] == ""
        config, supply, calls = ship_config(ROOT / f'ship/{module["ship"]}/{module["ship"]}.ship')
        assert config.buildCost == module["cost"] and config.buildTime == module["time"]
        assert supply == {"NFP_Generators": 1, module["cap"]: 1} and caps[module["cap"]] == 1
    for race, expected in (("Kushan", caps), ("Taiidan", CAPS)):
        for mode in ("small", "normal", "large", "huge"):
            vm = LuaRuntime(); actual = {}
            vm.globals().supplyLimit = lambda k, v: actual.__setitem__(k, v)
            vm.globals().supplyShow = lambda *args: None
            vm.execute((ROOT / f"scripts/races/{race}/deathmatch/unitcaps/{mode}.lua").read_text())
            assert actual == expected
    family_vm = LuaRuntime(); family_vm.execute('getn=nil; table=nil; string=nil; math=nil')
    family_vm.execute((ROOT / "scripts/familylist.lua").read_text())
    supplies = {r.name for r in family_vm.globals().unitcapsFamily.values()}
    assert len(supplies) == 61
    for faction in ("kus", "tai"):
        for row in manifest["ships"][faction]:
            ident = row["id"]
            config, supply, calls = ship_config(ROOT / f"ship/{ident}/{ident}.ship")
            assert set(supply) <= supplies and set(supply) == set(row["caps"])
            assert config.buildCost == row["ru"] and config.buildTime == row["build_time"]
            if row["stem"] == "heavycruiser": assert config.maxhealth == 90000 and config.ArmourFamily == "HeavyArmour"
    # Check new HOD is exactly the existing prepared VR model, not a stock stand-in.
    barrier = ROOT / "ship/nku_barricadefrigate/nku_barricadefrigate.hod"
    assert barrier.read_bytes() == (PROJECT / "local/testmod/ship/nku_barricadefrigate/nku_barricadefrigate.hod").read_bytes()
    config, supply, calls = ship_config(barrier.with_suffix('.ship'))
    assert config.maxhealth == 16000 and supply == {"Frigate": 1, "NFP_Special": 1}
    assert any(c[0] == "DefenseFieldAbility" for c in calls)
    # Native docking code is retained, but sequential selection and destructive
    # scripted side effects must not be restored by subsequent rebuilds.
    vm = LuaRuntime(); forbidden = []
    vm.globals().Player_RestrictBuildOption = lambda *args: forbidden.append(args)
    vm.globals().SobGroup_TakeDamage = lambda *args: forbidden.append(args)
    vm.globals().Player_CancelResearch = lambda *args: forbidden.append(args)
    assembly = (ROOT / "ship/kus_researchship/kus_researchship.lua").read_text()
    vm.execute(assembly); vm.globals().Load_Kus_ResearchShip(0); vm.globals().Destroy_Kus_ResearchShip("base", 0, 1)
    assert not forbidden
    update = assembly.split('function Update_Kus_ResearchShip', 1)[1].split('function Destroy_Kus_ResearchShip', 1)[0]
    assert 'Restrict_Kus_Ship' not in update and 'Player_GetNumberOfSquadronsOfTypeAwakeOrSleeping(playerIndex' not in update
    # Sensor technology uses a real native subsystem, with explicit state tests.
    vm = LuaRuntime(); flags = []
    vm.execute((ROOT / "ship/kus_sensorarray/kus_sensorarray.lua").read_text())
    vm.globals().SobGroup_SetHardPointHealth = lambda *args: flags.append(args)
    for value in (0, 1, 0):
        vm.globals().Player_HasResearch = lambda *args: value
        vm.globals().NKR_SensorUpdate("array", 0, 1)
    assert [v[-1] for v in flags] == [0, 1, 0]
    sensor_ship = (ROOT / "ship/kus_sensorarray/kus_sensorarray.ship").read_text()
    sensor_original = (PROJECT / "local/hw1ships/ship/kus_sensorarray/kus_sensorarray.hod").read_bytes()
    sensor_hod = (ROOT / "ship/kus_sensorarray/kus_sensorarray.hod").read_bytes()
    assert require_hardpoint_joints(sensor_ship, sensor_hod) == [SENSOR_HARDPOINT]
    # Reproduce the native fatal error that the old Lua-only check missed.
    try:
        require_hardpoint_joints(sensor_ship.replace('"' + SENSOR_HARDPOINT + '"', '"Root"'), sensor_original)
    except ValueError as error:
        assert "Root_Position" in str(error)
    else:
        raise AssertionError("Regression: original missing hardpoint must fail verification")
    original_nodes, changed_nodes = hierarchy(sensor_original), hierarchy(sensor_hod)
    assert changed_nodes[:len(original_nodes)] == original_nodes
    assert len(changed_nodes) == len(original_nodes) + 3
    node_names = [n["name"] for n in changed_nodes]
    assert len(set(node_names)) == len(node_names)
    assert all(not n["parent"] or n["parent"] in node_names for n in changed_nodes)
    original_chunks, changed_chunks = list(chunks(sensor_original)), list(chunks(sensor_hod))
    assert [k for k, _ in original_chunks] == [k for k, _ in changed_chunks]
    for (kind, original), (_, changed) in zip(original_chunks, changed_chunks):
        if kind == b"DTRM":
            assert [(k, c) for k, c in chunks(original, 12) if k != b"HIER"] == [
                (k, c) for k, c in chunks(changed, 12) if k != b"HIER"]
        else:
            assert original == changed
    assert (ROOT / "subsystem/nkr_hyperspacesensor/nkr_hyperspacesensor.hod").read_bytes() == (BASE / "subsystem/hgn_ms_sensors_detecthyperspace/hgn_ms_sensors_detecthyperspace.hod").read_bytes()
    # The progression scene must start without any laboratories, advanced combat
    # ships or granted science. Fleet showcase deliberately grants the full tree.
    fresh = ROOT / "leveldata/campaign/VRCFleetPreview/Research_Kushan"
    level = (fresh / "Research_Kushan.level").read_text()
    script = (fresh / "Research_Kushan.lua").read_text()
    assert 'resources=20000' in level and 'researchship' not in level
    assert 'kus_heavycruiser' not in level and 'nku_barricadefrigate' not in level
    assert 'Player_GrantResearchOption' not in script
    LuaRuntime().execute(level)  # Parse definitions without invoking game APIs.
    LuaRuntime().execute(script.replace('dofilepath("data:scripts/SCAR/SCAR_Util.lua")', ''))
    showcase = (fresh.parent / "Preview_Kushan/Preview_Kushan.lua").read_text()
    assert showcase.count('Player_GrantResearchOption') == len(research)
    for chapter in ('Preview_Kushan', 'Preview_Taiidan', 'Research_Kushan'):
        vm = LuaRuntime(); spawned, granted = [], []
        noop = lambda *args: None
        callbacks = {name: noop for name in ('createSOBGroup', 'addToSOBGroup', 'addAsteroid', 'addCamera',
            'setWorldBoundsInner', 'loadBackground', 'setSensorsManagerCameraDistances', 'CPU_Enable',
            'SobGroup_Create', 'Player_FillShipsByType', 'SobGroup_AbilityActivate', 'UI_BindKeyEvent',
            'Camera_Interpolate', 'Subtitle_Message', 'Player_RestrictBuildOption', 'Player_UnrestrictBuildOption', 'print')}
        callbacks.update(addSquadron=lambda name, ident, *args: spawned.append(ident),
                         SobGroup_Count=lambda *args: 0, Player_GrantResearchOption=lambda player, name: granted.append(name),
                         dofilepath=lambda path: None if path == 'data:scripts/SCAR/SCAR_Util.lua' else (_ for _ in ()).throw(AssertionError(path)))
        for key, value in callbacks.items(): vm.globals()[key] = value
        for key in ('ONEKEY', 'AB_Move', 'AB_Attack'): vm.globals()[key] = key
        directory = fresh.parent / chapter
        vm.execute((directory / (chapter + '.level')).read_text()); vm.globals().DetermChunk(); vm.globals().NonDetermChunk()
        vm.execute((directory / (chapter + '.lua')).read_text()); vm.globals().OnInit()
        if chapter == 'Preview_Kushan':
            assert set(granted) == set(by_name) and 'nku_barricadefrigate' in spawned
            assert all(module['ship'] in spawned for module in modules.values())
        else: assert not granted
        if chapter == 'Research_Kushan': assert not any('researchship' in s for s in spawned)
    # Campaign story unlocks remain free and bounded to the allowed ship projects.
    vm = LuaRuntime(); grants = []; unlock_events = []
    vm.globals().dofilepath = lambda *args: None
    vm.globals().getn = len
    vm.globals().Player_UnrestrictResearchOption = lambda player, name: unlock_events.append(('unrestrict',name))
    vm.globals().Player_GrantResearchOption = lambda player, name: (grants.append(name),unlock_events.append(('grant',name)))
    vm.globals().Player_RestrictResearchOption = lambda player, name: unlock_events.append(('restrict',name))
    vm.execute((ROOT / "leveldata/campaign/VastReachesMiniCampaign/VRC_Common.lua").read_text())
    vm.globals().NKR_GrantCampaignUnlocks(vm.table_from(["Kus_Interceptor", "Kus_HeavyCorvette"]))
    assert set(grants) == {"NKR_FighterDrive", "NKR_FighterChassis", "NKR_CorvetteDrive", "NKR_CorvetteChassis"}
    assert unlock_events==[event for name in grants for event in [('unrestrict',name),('grant',name),('restrict',name)]], 'Story grants must temporarily unrestrict and restore each paid option'
    assert path_cost(design, design["requirements"]["kus_scout"])["cost"] == 450
    assert path_cost(design, design["requirements"]["kus_assaultfrigate"])["cost"] == 3100
    assert path_cost(design, design["requirements"]["kus_attackbomber"])["cost"] == 1550
    from verify_novokushan_plasma import verify as verify_plasma
    from verify_fleet_localization import verify as verify_localization
    verify_plasma()
    verify_localization()
    result = dict(status="passed", science_races=["kus"], normal_research=57,
                  automatic_effects=len(research)-57, laboratories=6, sandbox_OnInit_mocks=3, independent_laboratories_checked=True,
                  graph_no_cycles_or_unreachable_references=True, ship_gates_checked=len(design["requirements"]),
                  minelayer_and_multigun_corrections_checked=True, fresh_research_sandbox=True,
                  campaign_free_unlocks_checked=True, caps_and_heavy_base_stats_preserved=True,
                  station_taiidan_only=True, vr_barrier_hull_preserved=True, engine_tested=False,
                  sensor_attachment_joints_checked=True, original_missing_joint_regression_checked=True,
                  sensor_geometry_and_original_rig_preserved=True,
                  plasma_unlock_and_special_ammunition_checked=True, ru_en_dictionaries_checked=True,
                  pending=manifest.get("research_design"))
    (PROJECT / "local/fleet-preview/research-verification.json").write_text(json.dumps(result, indent=2) + '\n')
    (PROJECT / "local/fleet-preview/verification.json").write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == "__main__": verify()
