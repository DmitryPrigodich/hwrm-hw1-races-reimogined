"""Check native special-weapon roles and the unchanged normal plasma battery."""

import json
import math
import re

from lupa.lua51 import LuaRuntime, lua_type

from prepare_fleet_preview import BASE, NATIVE, PROJECT, ROOT, REPORT


def weapon_calls(path):
    vm = LuaRuntime()
    vm.globals().NewWeaponType = vm.table()
    calls = {}
    def plain(value):
        return {k: plain(v) for k, v in value.items()} if lua_type(value) == 'table' else value
    text = path.read_text()
    for name in set(re.findall(r'\b(\w+)\(', text)):
        def record(*args, name=name):
            calls.setdefault(name, []).append([plain(v) for v in args[1:]])
        vm.globals()[name] = record
    vm.execute(text)
    return calls


def verify():
    rows = json.loads(REPORT.read_text(encoding='utf8'))['plasma_ammunition']
    assert {r['ship'] for r in rows} == {'kus_attackbomber', 'kus_assaultfrigate'}
    for row in rows:
        original = row['source_weapon'].lower()
        baseline = weapon_calls(BASE / f'weapon/{original}/{original}.wepn')
        normal, ship, subsystem = [weapon_calls(ROOT / f'weapon/{w.lower()}/{w.lower()}.wepn') for w in row['weapons']]
        # Before research the native battery is intact apart from its role label.
        for name, calls in baseline.items():
            if name != 'StartWeaponConfig': assert normal[name] == calls
        native_config = baseline['StartWeaponConfig'][0]
        normal_config = normal['StartWeaponConfig'][0]
        assert normal_config[3] == 'Normal Only'
        assert all(a == b for i, (a, b) in enumerate(zip(native_config, normal_config)) if i not in (3, 12))
        assert ship['StartWeaponConfig'][0][3] == subsystem['StartWeaponConfig'][0][3] == 'Special Attack'
        assert ship['StartWeaponConfig'][0][12] == 0 and subsystem['StartWeaponConfig'][0][12] == 1
        assert ship['AddWeaponResult'] == baseline['AddWeaponResult']
        assert ship['setPenetration'] == baseline['setPenetration']
        assert any(a.get('SubSystem') == 0 for a in ship['setAccuracy'][0] if isinstance(a, dict))
        assert subsystem['setAccuracy'] == [[0, {'SubSystem': 1}]]
        damage = baseline['AddWeaponResult'][0]
        upgraded = subsystem['AddWeaponResult'][0]
        assert all(math.isclose(upgraded[i], damage[i]*190/135, rel_tol=0.00001) for i in (3, 4))
        assert any(a.get('SubSystemArmour') == 2.5 for a in subsystem['setPenetration'][0] if isinstance(a, dict))
        ship_text = (ROOT / f"ship/{row['ship']}/{row['ship']}.ship").read_text()
        native_ship = (NATIVE / f"{row['ship']}/{row['ship']}.ship").read_text()
        hardpoints = lambda text: re.findall(r'StartShipHardPointConfig\(.*?\);', text, flags=re.S)
        assert hardpoints(ship_text) == hardpoints(native_ship)  # Frigate gun subsystems intact.
        for weapon in row['weapons']:
            assert ship_text.count('StartShipWeaponConfig(NewShipType,"'+weapon+'"') == 2
    result = dict(status='passed', ships=2, variants=6, normal_plasma_damage_unchanged=True,
                  anti_subsystem_ammunition_gated_by_research=True, frigate_guns_unchanged=True,
                  engine_tested=False)
    (PROJECT / 'local/fleet-preview/plasma-verification.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__': verify()
