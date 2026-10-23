"""Apply research to the generated preview only; never install or launch a game."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path

from lupa.lua51 import LuaRuntime, lua_type

import prepare_fleet_preview as fleet
from novokushan_research_design import make_design, path_cost
from sensor_hardpoint import SENSOR_HARDPOINT, add_sensor_hardpoint
from fleet_localization import BRANCH_EN, research_description_en
from novokushan_plasma import apply_plasma

PROJECT, ROOT, BASE = fleet.PROJECT, fleet.ROOT, fleet.BASE


def literal(value):
    if isinstance(value, dict): return "{" + ",".join("[" + literal(k) + "]=" + literal(v) for k, v in value.items()) + "}"
    if isinstance(value, (list, tuple)): return "{" + ",".join(map(literal, value)) + "}"
    if lua_type(value) == "table": return literal(dict(value.items()))
    if value is None: return "nil"
    if isinstance(value, bool): return "1" if value else "0"
    if isinstance(value, str): return json.dumps(value, ensure_ascii=True)
    return str(value)


def read_lua_table(path, name):
    vm = LuaRuntime(); vm.execute(path.read_text(encoding="utf-8-sig"))
    return [dict(row.items()) for row in vm.globals()[name].values()]


def research_rows(design):
    modules = {m["id"]: m for m in design["modules"]}
    rows, effects = [], []
    for n, tech in enumerate(design["technologies"]):
        desc = tech["ru"] + ". " + (tech["note"] or "Открывает связанные корабли и технологии.")
        rows.append(dict(Name=tech["id"], RequiredResearch=" & ".join(tech["requires"]),
                         RequiredSubSystems=modules[tech["module"]]["subsystem"], Cost=tech["cost"], Time=tech["time"],
                         DisplayedName=fleet.ucs(tech["ru"], tech["en"]), ShortDisplayedName=fleet.ucs(tech["ru"], tech["en"]), Description=fleet.ucs(desc, research_description_en(tech)),
                         DisplayPriority=10 + n, TargetName=modules[tech["module"]]["ship"],
                         Icon="data:ui/newui/research/icons/" + ("health" if "Chassis" in tech["key"] or "Armor" in tech["key"] else "speed" if "Drive" in tech["key"] or "Speed" in tech["key"] or "Burn" in tech["key"] else "tech") + ".mres"))
        for i, effect in enumerate(tech["effects"]):
            # Same zero-cost/zero-time automatic dependency pattern as the
            # native InstaAdvancedFrigateTech. No extra queue or player payment.
            row = dict(Name=tech["id"] + "_Effect" + str(i + 1), RequiredResearch=tech["id"], RequiredSubSystems="", Cost=0, Time=0,
                       DisplayedName="", ShortDisplayedName="", Description="", DisplayPriority=0,
                       TargetType=2, TargetName=effect["target"], UpgradeType=1 if effect["kind"] == "ability" else 0,
                       UpgradeName=effect["name"])
            if effect["value"] is not None: row["UpgradeValue"] = effect["value"]
            effects.append(row)
    return rows + effects


def assembly_script():
    text = (fleet.NATIVE / "kus_researchship/kus_researchship.lua").read_text()
    text = re.sub(r'(function Load_Kus_ResearchShip\(playerIndex\)).*?\nend', r'\1\n    -- All six profiles may be chosen freely; unique supply limits prevent duplicates.\nend', text, count=1, flags=re.S)
    text = text.replace('\tRestrict_Kus_Ship(playerIndex, "kus_researchship", 1)', '')
    begin = text.index('\tfor i = 1,5,1 do\n\t\tif Player_GetNumberOfSquadronsOfTypeAwakeOrSleeping')
    finish = text.index('function Destroy_Kus_ResearchShip', begin)
    text = text[:begin] + 'end\n\n' + text[finish:]
    text = re.sub(r'(function Destroy_Kus_ResearchShip\(CustomGroup, playerIndex, shipID\)).*?(?=function Restrict_Kus_Ship)',
                  r'\1\n    -- No scripted destruction of other sections and no cancellation of learned technologies.\nend\n\n', text, count=1, flags=re.S)
    return text


def add_barrier(report):
    source = PROJECT / "local/testmod/ship/nku_barricadefrigate"
    destination = ROOT / "ship/nku_barricadefrigate"
    destination.mkdir(parents=True, exist_ok=True)
    for suffix in (".hod", ".events"):
        shutil.copy2(source / (source.name + suffix), destination / (source.name + suffix))
    text = (source / (source.name + ".ship")).read_text()
    text = re.sub(r'^setSupplyValue\([^\n]+\)\s*;?\s*$', '', text, flags=re.M)
    title = fleet.ucs("Фрегат защитного поля")
    text += '\n-- Research phase: VR barricade hull with native Hiigaran field mechanics.\n'
    text += f'NewShipType.displayedName="{title}"\nNewShipType.sobDescription="{title}"\nNewShipType.buildCost=1100\nNewShipType.buildTime=55\nNewShipType.buildBatch=1\nNewShipType.maxhealth=16000\nNewShipType.DisplayFamily="Frigate"\n'
    text += 'setSupplyValue(NewShipType,"Frigate",1.0);\nsetSupplyValue(NewShipType,"NFP_Special",1.0);\n'
    fleet.write("ship/nku_barricadefrigate/nku_barricadefrigate.ship", text)
    row = dict(id="nku_barricadefrigate", stem="barricadefrigate", title=title, ru=1100, squadron=1, build_time=55,
               prototype_hp=16000, caps=["Frigate", "NFP_Special"], display="Frigate", batch_formation=None,
               source_sha256=hashlib.sha256((source / (source.name + ".hod")).read_bytes()).hexdigest())
    report["ships"]["kus"].append(row)
    return row


def science_sandbox(design, report):
    chapter = "Research_Kushan"
    target = ROOT / "leveldata/campaign/VRCFleetPreview" / chapter
    source = target.parent / "Preview_Kushan"
    target.mkdir(parents=True, exist_ok=True)
    text = (source / "Preview_Kushan.level").read_text()
    keep = {"kus_resourcecollector", "kus_resourcecontroller", "kus_probe"}
    lines = []
    for line in text.splitlines():
        if line.startswith('addSquadron("NFP_Show_'):
            ident = re.search(r',"([^"]+)"', line)[1]
            if ident not in keep: continue
        lines.append(line)
    title = fleet.ucs("Новокушане — исследовательская проба")
    message = fleet.ucs("Исследовательская проба. Постройте профильные научные модули; R — исследования, B — строительство. Шесть секций, одна общая очередь. Начальный запас — 20000 RU.",
                        "Research trial. Build specialist research modules; R: research, B: construction. Six sections share one research queue. Starting resources: 20000 RU.")
    text = "\n".join(lines).replace('resources=100000', 'resources=20000')
    text = re.sub(r'levelDesc="[^"]+"', 'levelDesc="' + title + '"', text)
    fleet.write(f"leveldata/campaign/VRCFleetPreview/{chapter}/{chapter}.level", text + "\n")
    script = (source / "Preview_Kushan.lua").read_text()
    script = re.sub(r'print\("NFP_BATCH:[^\n]+\n', '', script)
    script = re.sub(r'Subtitle_Message\("[^\"]+",30\)', f'Subtitle_Message("{message}",30)', script)
    script = script.replace('NFP_PREVIEW: ready kus; no engine validation implied by static checks', 'NKR_RESEARCH: ready kus; native research behavior still needs inspection')
    fleet.write(f"leveldata/campaign/VRCFleetPreview/{chapter}/{chapter}.lua", script)
    shutil.copy2(source / "Preview_Kushan.dds", target / (chapter + ".dds"))
    campaign = ROOT / "leveldata/campaign/VRCFleetPreview.campaign"
    text = campaign.read_text() + f'\nMission[3]={{postload=function() end,directory="{chapter}",level="{chapter}.level",postlevel=function() end,displayName="{title}",description="{message}"}}\n'
    campaign.write_text(text, encoding="ascii")


def sensor_script():
    # Use the actual native HyperspaceSensor subsystem type, rather than inventing
    # a research modifier for hyperspace sensing. It has no research contribution.
    source = (BASE / "subsystem/hgn_ms_sensors_detecthyperspace/hgn_ms_sensors_detecthyperspace.subs").read_text()
    for key, value in (("visible", "0"), ("innate", "1"), ("maxhealth", "30000"), ("regentime", "0"),
                       ("inactiveTimeAfterDamage", "0"), ("activateHealthPercentage", "0.1")):
        source, count = re.subn(r'^NewSubSystemType\.' + key + r'=.*$', 'NewSubSystemType.' + key + '=' + value, source, flags=re.M)
        if count == 0: source += '\nNewSubSystemType.' + key + '=' + value + '\n'
    source = re.sub(r'^loadShipPatchList.*?;\s*', '', source, flags=re.M | re.S)
    fleet.write("subsystem/nkr_hyperspacesensor/nkr_hyperspacesensor.subs", source)
    donor = BASE / "subsystem/hgn_ms_sensors_detecthyperspace/hgn_ms_sensors_detecthyperspace.hod"
    shutil.copy2(donor, ROOT / "subsystem/nkr_hyperspacesensor/nkr_hyperspacesensor.hod")
    shutil.copy2(donor.with_suffix('.events'), ROOT / "subsystem/nkr_hyperspacesensor/nkr_hyperspacesensor.events")
    # StartShipHardPointConfig expands its prefix into _Position/_Direction/_Rest.
    # The unmodified sensor array has only Root and cannot host a subsystem there.
    # Append a proper native sensor mount; preserve existing joints and all meshes.
    native_hod = fleet.NATIVE / "kus_sensorarray/kus_sensorarray.hod"
    sensor_mount_donor = PROJECT / "local/hw2ships/ship/hgn_mothership/hgn_mothership.hod"
    (ROOT / "ship/kus_sensorarray/kus_sensorarray.hod").write_bytes(
        add_sensor_hardpoint(native_hod.read_bytes(), sensor_mount_donor.read_bytes()))
    fleet.write("ship/kus_sensorarray/kus_sensorarray.lua", '''function NKR_SensorUpdate(group, playerIndex, shipID)
    local enabled = Player_HasResearch(playerIndex, "NKR_HyperspaceSensors")
    SobGroup_SetHardPointHealth(group, "NKR Hyperspace Sensor", enabled)
end
''')
    path = ROOT / "ship/kus_sensorarray/kus_sensorarray.ship"
    text = path.read_text()
    text = re.sub(r'addAbility\(NewShipType,"SensorPing",1,', 'addAbility(NewShipType,"SensorPing",0,', text)
    text = re.sub(r'addCustomCode\(NewShipType,"data:Ship/Kus_SensorArray/Kus_SensorArray.lua"[^\n]+',
                  'addCustomCode(NewShipType,"data:Ship/Kus_SensorArray/Kus_SensorArray.lua","","NKR_SensorUpdate","NKR_SensorUpdate","","NKR_Sensors",1)', text)
    text += '\nNewShipType.detectionStrength=1\nStartShipHardPointConfig(NewShipType,"NKR Hyperspace Sensor","' + SENSOR_HARDPOINT + '","System","Innate","Indestructible","NKR_HyperspaceSensor","","","","","","","","");\n'
    path.write_text(text, encoding="ascii")


def apply():
    report = json.loads(fleet.REPORT.read_text(encoding="utf-8"))
    # Recover existing string allocator state; the baseline already contains all
    # ship names. The layer allocates subsequent UCS IDs only.
    fleet.STRINGS.clear(); fleet.STRINGS.update({int(k): v for k, v in report["strings"].items()})
    fleet.STRINGS_EN.clear(); fleet.STRINGS_EN.update({int(k): v for k, v in report["strings_en"].items()})
    design = make_design()
    modules = design["modules"]
    barrier = add_barrier(report)
    entries = read_lua_table(ROOT / "scripts/races/Kushan/scripts/def_build.lua", "build")
    entries.append(dict(Type=0, ThingToBuild=barrier["id"], RequiredResearch="", RequiredShipSubSystems="", DisplayPriority=115,
                        DisplayedName=barrier["title"], Description=barrier["title"]))
    for row in entries:
        reqs = design["requirements"].get(row["ThingToBuild"].lower(), [])
        row["RequiredResearch"] = " & ".join(reqs)
    for index, module in enumerate(modules):
        ident = module["ship"]
        title = fleet.ucs("Исследовательский модуль " + module["ru"] + " — " + module["branch"], module["en"] + " Research Module — " + BRANCH_EN[module["id"]])
        description = fleet.ucs("Направление: " + module["branch"] + ". Открывает свою научную ветку и ускоряет общую очередь. Не более одного модуля каждого профиля.",
                                "Field: " + BRANCH_EN[module["id"]] + ". Unlocks its research branch and accelerates the shared queue. One module of each profile at most.")
        text = (fleet.NATIVE / ident / (ident + ".ship")).read_text(encoding="utf-8-sig")
        text = re.sub(r'^setSupplyValue\([^\n]+\)\s*;?\s*$', '', text, flags=re.M)
        text += f'\nNewShipType.displayedName="{title}"\nNewShipType.sobDescription="{description}"\nNewShipType.buildCost={module["cost"]}\nNewShipType.buildTime={module["time"]}\nNewShipType.buildBatch=1\nNewShipType.TOIcon="Diamond"\n'
        text += f'setSupplyValue(NewShipType,"NFP_Generators",1.0);\nsetSupplyValue(NewShipType,"{module["cap"]}",1.0);\n'
        fleet.write(f"ship/{ident}/{ident}.ship", text)
        entries.append(dict(Type=0, ThingToBuild=ident, RequiredResearch="", RequiredShipSubSystems="", DisplayPriority=600 + index,
                            DisplayedName=title, Description=description))
        report["ships"]["kus"].append(dict(id=ident, stem="researchship" + ("_" + str(index) if index else ""),
                title=title, ru=module["cost"], build_time=module["time"], squadron=1, caps=["NFP_Generators", module["cap"]], display="NonCombat", batch_formation=None))
    fleet.write("ship/kus_researchship/kus_researchship.lua", assembly_script())
    fleet.write("scripts/races/Kushan/scripts/def_build.lua", "Ship=0\nSubSystem=1\nbuild=" + literal(entries) + "\n")
    research = research_rows(design)
    fleet.write("scripts/races/Kushan/scripts/def_research.lua", "-- One native global queue; module conditions select branches.\nresearch=" + literal(research) + "\n")
    caps = dict(fleet.CAPS)
    for m in modules: caps[m["cap"]] = 1
    cap_text = "\n".join(f'supplyLimit("{k}",{v});' for k, v in caps.items()) + "\n"
    cap_text += "\n".join(f'supplyShow("{k}","{("Never" if k == "Mothership" else "NotEmpty")}");' for k in caps) + "\n"
    for mode in ("small", "normal", "large", "huge"):
        fleet.write(f"scripts/races/Kushan/deathmatch/unitcaps/{mode}.lua", cap_text)
    fleet.write("scripts/races/Kushan/singleplayer/unitcaps/singleplayer.lua", cap_text)
    restriction = ",".join("kus_drone" + str(i) for i in range(14))
    fleet.write("scripts/races/Kushan/deathmatch/props/gbx.lua", 'Number_Properties_Priority=20\nNumber_Properties={dm_challenge_research_baseline=1}\nString_Properties_Priority=20\nString_Properties={dm_build_restrict="' + restriction + '",dm_research_restrict="",dm_allresearch_build_restrict="' + restriction + '",dm_allresearch_research_restrict=""}\n')
    sensor_script()
    report["plasma_ammunition"] = apply_plasma()
    for stem in ("mothership", "carrier"):
        path = ROOT / f"ship/kus_{stem}/kus_{stem}.ship"
        text = path.read_text().replace('addAbility(NewShipType,"HyperSpaceCommand",1,', 'addAbility(NewShipType,"HyperSpaceCommand",0,')
        path.write_text(text, encoding="ascii")
    # Free fleet display remains available; research has its own fresh-start map.
    preview = ROOT / "leveldata/campaign/VRCFleetPreview/Preview_Kushan/Preview_Kushan.lua"
    text = preview.read_text()
    # Grant the complete tree only in the fleet-showcase scene, not skirmish or
    # the new research sandbox. No hidden modifier needs an extra paid job.
    grants = '\n'.join('Player_GrantResearchOption(0,"' + row["Name"] + '")' for row in research)
    text = text.replace('function OnInit()\n', 'function OnInit()\n' + grants + '\n', 1)
    text = text.replace('no engine validation implied by static checks', 'showcase grants all technologies; use Research_Kushan for progression')
    preview.write_text(text, encoding="ascii")
    science_sandbox(design, report)
    fresh = ROOT / "leveldata/campaign/VRCFleetPreview/Research_Kushan/Research_Kushan.lua"
    fresh.write_text(fresh.read_text().replace(grants + '\n', '', 1), encoding="ascii")
    showcase_level = preview.with_suffix('.level')
    text = showcase_level.read_text()
    additions = ['addSquadron("NKR_Barrier","nku_barricadefrigate",{3000,0,3500},0,{0,0,0},1,0)']
    additions += [f'addSquadron("NKR_Lab_{i}","{m["ship"]}",{{{-5000+i*650},0,3000}},0,{{0,0,0}},1,0)' for i, m in enumerate(modules)]
    text = text.replace('end\nfunction NonDetermChunk()', '\n'.join(additions) + '\nend\nfunction NonDetermChunk()', 1)
    showcase_level.write_text(text, encoding="ascii")
    # Campaign technology announcements stay scripted; no paid science barrier
    # is inserted into the three existing HWVR chapter review units.
    common = ROOT / "leveldata/campaign/VastReachesMiniCampaign/VRC_Common.lua"
    text = common.read_text()
    unlocks = {ident: path_cost(design, reqs)["technologies"] for ident, reqs in design["requirements"].items()}
    # Accept the original case-sensitive campaign IDs without depending on the
    # Lua 5 string table (the legacy engine exposes a different library surface).
    for row in read_lua_table(BASE / "scripts/races/kushan/scripts/def_build.lua", "build"):
        ident = row["ThingToBuild"]
        if ident.lower() in unlocks: unlocks[ident] = unlocks[ident.lower()]
    helper = 'NKR_CampaignUnlocks=' + literal(unlocks) + '''
function NKR_GrantCampaignUnlocks(allowed)
    for i=1,getn(allowed) do
        local requirements=NKR_CampaignUnlocks[allowed[i]]
        if requirements then
            for j=1,getn(requirements) do
                Player_UnrestrictResearchOption(0,requirements[j])
                Player_GrantResearchOption(0,requirements[j])
                Player_RestrictResearchOption(0,requirements[j])
            end
        end
    end
end
'''
    text += '\n' + helper
    anchor = 'for i=1,getn(allowed) do Player_UnrestrictBuildOption(0,allowed[i]) end'
    if anchor not in text: raise ValueError("Campaign build-unlock anchor changed")
    text = text.replace(anchor, anchor + '\n    NKR_GrantCampaignUnlocks(allowed)', 1)
    common.write_text(text, encoding="ascii")
    data = ROOT / "leveldata/campaign/VastReachesMiniCampaign/VRC_Data.lua"
    text = data.read_text() + '\nVRC_AllResearch=' + literal([r["Name"] for r in research]) + '\n'
    text += 'VRC_AllBuilds=' + literal([r["id"] for r in report["ships"]["kus"]] + ["kus_drone" + str(i) for i in range(14)]) + '\n'
    data.write_text(text, encoding="ascii")
    # Only new strings are appended; baseline entries and RAW localization stay.
    old_strings = len(report["strings"])
    for lang in ("Russian", "English"):
        path = ROOT / f"locale/{lang}/vrcampaign.ucs"
        text = path.read_text(encoding="utf-16")
        strings = fleet.STRINGS if lang == "Russian" else fleet.STRINGS_EN
        text += '\n' + '\n'.join(f'{key}\t{value}' for key, value in list(strings.items())[old_strings:]) + '\n'
        path.write_text(text, encoding="utf-16")
    design["paths"] = {ident: path_cost(design, reqs) for ident, reqs in design["requirements"].items()}
    design["runtime_research_entries"] = len(research)
    design["normal_research_entries"] = len(design["technologies"])
    design["native_validation_pending"] = ["Six independent sections and native docking/counting", "Automatic zero-time effects, modifier replacement vs multiplication", "Sensor hardpoint attachment and hyperspace sensing", "Research UI grouping and ordinary production gates", "AI build/research behavior not tuned"]
    target = PROJECT / "local/novokushan/research-design.json"
    target.write_text(json.dumps(design, ensure_ascii=False, indent=2) + '\n', encoding="utf-8")
    report.update(research_phase="novokushan-v1", science_races=["kus"], science_caps={"kus": caps, "tai": fleet.CAPS},
                  research_design=str(target), research_entries=len(research), normal_research_entries=len(design["technologies"]), strings=fleet.STRINGS, strings_en=fleet.STRINGS_EN)
    fleet.REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding="utf-8")
    print(json.dumps(dict(science="kus", technologies=len(design["technologies"]), automatic_effects=len(research)-len(design["technologies"]), modules=6, game_launched=False)))
    return design


if __name__ == "__main__": apply()
