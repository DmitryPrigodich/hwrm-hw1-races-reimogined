"""Native HW2 special-ammunition roles on the existing Kushan plasma mounts."""

import hashlib
import re

import prepare_fleet_preview as fleet


def weapon_config(text):
    match = re.search(r'StartWeaponConfig\(([^\n]+)\);', text)
    args = re.findall(r'"[^"]*"|[^,]+', match[1])
    return match, args


def apply_plasma():
    report = []
    prototype = {}
    for role, native in (("normal", "hgn_bomblauncher"), ("ship", "hgn_antishipbomblauncher"),
                         ("subsystem", "hgn_antisubsystembomblauncher")):
        prototype[role] = weapon_config((fleet.BASE / f"weapon/{native}/{native}.wepn").read_text())[1]
    for ship, original in (("kus_attackbomber", "HW1_Bomber"), ("kus_assaultfrigate", "Kus_AssaultBomb")):
        source_path = fleet.BASE / f"weapon/{original.lower()}/{original.lower()}.wepn"
        source = source_path.read_text()
        weapons = []
        for role in ("normal", "ship", "subsystem"):
            text = source
            match, args = weapon_config(text)
            # Only the native attack mode and target-selection flag differ.
            for index in (4, 13):
                args[index] = prototype[role][index]
            if role == "subsystem":
                args[3] = prototype[role][3]  # Existing Improved_Plasma_Bomb projectile.
                # Keep each mount's range/cadence; use the Classic bomb damage ratio.
                text = re.sub(r'(DamageHealth","Target",)([\d.]+),([\d.]+)',
                              lambda m: m[1] + f'{float(m[2])*190/135:.6g},{float(m[3])*190/135:.6g}', text)
                text = re.sub(r'setAccuracy\(NewWeaponType,.*?\);',
                              'setAccuracy(NewWeaponType,0,{SubSystem=1});', text, flags=re.S)
                text = re.sub(r'\{SubSystemArmour=[^}]+\}', '{SubSystemArmour=2.5}', text)
            elif role == "ship":
                # Improved mode must choose exactly one ammunition per target.
                def exclude_subsystems(match):
                    accuracy, count = re.subn(r'\{SubSystem=[^}]+\}', '{SubSystem=0}', match[0])
                    return accuracy if count else accuracy[:-2] + ',{SubSystem=0});'
                text = re.sub(r'setAccuracy\(NewWeaponType,.*?\);', exclude_subsystems, text, flags=re.S)
            # Re-find after replacements, since damage/accuracy can change length.
            match, _ = weapon_config(text)
            text = text[:match.start()] + 'StartWeaponConfig(' + ','.join(args) + ');' + text[match.end():]
            ident = f'NKR_{ship.removeprefix("kus_")}_Plasma_{role}'
            fleet.write(f'weapon/{ident.lower()}/{ident.lower()}.wepn', text)
            weapons.append(ident)
        path = fleet.ROOT / f"ship/{ship}/{ship}.ship"
        ship_text = path.read_text()
        pattern = r'StartShipWeaponConfig\(NewShipType,"' + original + r'","([^"]+)","([^"]+)"\);'
        mounts = re.findall(pattern, ship_text)
        if len(mounts) != 2:
            raise ValueError("Expected two native plasma mounts on " + ship)
        ship_text = re.sub(pattern, lambda m: '\n'.join(
            f'StartShipWeaponConfig(NewShipType,"{w}","{m[1]}","{m[2]}");' for w in weapons), ship_text)
        path.write_text(ship_text, encoding="ascii")
        report.append(dict(ship=ship, source_weapon=original, source_sha256=hashlib.sha256(source_path.read_bytes()).hexdigest(),
                           mounts=mounts, weapons=weapons, upgrade="NKR_PlasmaBombs", damage_ratio=190/135,
                           normal_ship_damage_unchanged=True, special_ammunition_subsystems_only=True,
                           frigate_gun_subsystems_unchanged=True, engine_tested=False))
    return report
