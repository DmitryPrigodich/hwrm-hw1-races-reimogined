"""First playable Novokushan research design, based on Dmitry's 2026-10-21 tree.

Costs/effects are tuning proposals. Native IDs and user input aliases stay separate.
"""
from __future__ import annotations

MODULES = [
    dict(id="naabal", ru="Наабал", en="Naabal", branch="Шасси", ship="kus_researchship", subsystem="Research", cap="Research", cost=350, time=30),
    dict(id="manaan", ru="Манаан", en="Manaan", branch="Двигатели", ship="kus_researchship_1", subsystem="ResearchShip1", cap="Research1", cost=350, time=30),
    dict(id="soban", ru="Собан", en="Soban", branch="Орудия", ship="kus_researchship_2", subsystem="ResearchShip2", cap="Research2", cost=350, time=30),
    dict(id="sjet", ru="С’Джет", en="S’jet", branch="Спецтехнологии", ship="kus_researchship_3", subsystem="ResearchShip3", cap="Research3", cost=500, time=40),
    dict(id="somtaaw", ru="Сомтаау", en="Somtaaw", branch="ИИ-системы", ship="kus_researchship_4", subsystem="ResearchShip4", cap="Research4", cost=350, time=30),
    dict(id="paktu", ru="Пакту", en="Paktu", branch="Сенсоры", ship="kus_researchship_5", subsystem="ResearchShip5", cap="Research5", cost=300, time=25),
]
CLASSES = {
    "Fighter": ["kus_scout", "kus_interceptor", "kus_attackbomber", "kus_cloakedfighter", "kus_defender"],
    "Corvette": ["kus_lightcorvette", "kus_heavycorvette", "kus_multiguncorvette", "kus_minelayercorvette", "kus_repaircorvette", "kus_salvagecorvette"],
    "Frigate": ["kus_supportfrigate", "kus_assaultfrigate", "kus_ioncannonfrigate", "kus_dronefrigate", "nku_barricadefrigate"],
    "Destroyer": ["kus_destroyer", "kus_missiledestroyer", "kus_carrier", "kus_heavycruiser"],
}


def effect(target, name, value=None, kind="modifier"):
    return dict(target=target, name=name, value=value, kind=kind)


def make_design():
    techs = []
    def add(key, module, ru, en, cost, time, requires=(), effects=(), note="", source_en=None):
        techs.append(dict(id="NKR_" + key, key=key, module=module, ru=ru, en=en, cost=cost, time=time,
                          requires=["NKR_" + x for x in requires], effects=list(effects), note=note, source_en=source_en or en))
    for group, ru, cost, seconds, advanced_cost, advanced_time in (
        ("Fighter", "истребителей", 150, 25, 350, 35),
        ("Corvette", "корветов", 500, 50, 600, 60),
        ("Frigate", "фрегатов", 800, 65, 1000, 75),
        ("Destroyer", "эсминцев", 1600, 90, 1200, 90),
    ):
        add(group + "Chassis", "naabal", "Шасси " + ru, group + " Chassis", cost, seconds)
        add("Advanced" + group + "Chassis", "naabal", "Усовершенствованное шасси " + ru, "Advanced " + group + " Chassis", advanced_cost, advanced_time,
            [group + "Chassis"], [effect(s, "MAXHEALTH", 1.15) for s in CLASSES[group]], "Общий уровень прочности: 115% базовых HP; также открывает продолжение ветки.")
    for key, ru, en, group, target, price, seconds in (
        ("HeavyCorvetteArmor", "Броня тяжёлого корвета", "Heavy Corvette Armor", "Corvette", "kus_heavycorvette", 500, 40),
        ("MultigunCorvetteArmor", "Броня многопушечного корвета", "Multigun Corvette Armor", "Corvette", "kus_multiguncorvette", 500, 40),
        ("AssaultFrigateArmor", "Броня штурмового фрегата", "Assault Frigate Armor", "Frigate", "kus_assaultfrigate", 800, 60),
        ("IonFrigateArmor", "Броня ионного фрегата", "Ion Cannon Frigate Armor", "Frigate", "kus_ioncannonfrigate", 800, 60),
        ("LightDestroyerArmor", "Броня лёгкого эсминца", "Light Destroyer Armor", "Destroyer", "kus_destroyer", 1000, 60),
        ("MissileDestroyerArmor", "Броня лёгкого ракетного эсминца", "Light Missile Destroyer Armor", "Destroyer", "kus_missiledestroyer", 1000, 60),
        ("CarrierArmor", "Броня носителя", "Carrier Armor", "Destroyer", "kus_carrier", 1000, 60),
        ("HeavyDestroyerArmor", "Броня тяжёлого эсминца", "Heavy Destroyer Armor", "Destroyer", "kus_heavycruiser", 1500, 75),
    ):
        add(key, "naabal", ru, en, price, seconds, ["Advanced" + group + "Chassis"], [effect(target, "MAXHEALTH", 1.30)],
            "Индивидуальный уровень: целевые 130% базовых HP, тип брони не меняется.", en.replace(" Armor", " Chassis") if group == "Destroyer" else en)
    for group, ru, cost, seconds, advanced_cost, advanced_time in (
        ("Fighter", "истребителей", 100, 20, 350, 35),
        ("Corvette", "корветов", 500, 50, 500, 50),
        ("Frigate", "фрегатов", 1000, 70, 750, 65),
        ("Destroyer", "эсминцев", 1600, 90, 1000, 75),
    ):
        add(group + "Drive", "manaan", "Двигатели " + ru, group + " Drive", cost, seconds)
        add("Advanced" + group + "Drive", "manaan", "Усовершенствованные двигатели " + ru, "Advanced " + group + " Drive", advanced_cost, advanced_time,
            [group + "Drive"], [effect(s, "MAXSPEED", 1.10) for s in CLASSES[group]], "Общий уровень скорости: 110% исходной; также открывает продолжение ветки.")
    for key, ru, en, group, target, price, seconds in (
        ("LightFighterSpeed", "Скорость лёгкого истребителя", "Light Fighter Drive", "Fighter", "kus_scout", 300, 30),
        ("InterceptorSpeed", "Скорость перехватчика", "Interceptor Drive", "Fighter", "kus_interceptor", 300, 30),
        ("BomberSpeed", "Скорость штурмового бомбардировщика", "Attack Bomber Drive", "Fighter", "kus_attackbomber", 300, 30),
        ("LightCorvetteSpeed", "Скорость лёгкого корвета", "Light Corvette Drive", "Corvette", "kus_lightcorvette", 300, 35),
        ("MultigunCorvetteSpeed", "Скорость многопушечного корвета", "Multigun Corvette Drive", "Corvette", "kus_multiguncorvette", 400, 40),
        ("SupportFrigateSpeed", "Скорость фрегата поддержки", "Support Frigate Drive", "Frigate", "kus_supportfrigate", 500, 50),
        ("AssaultFrigateSpeed", "Скорость штурмового фрегата", "Assault Frigate Drive", "Frigate", "kus_assaultfrigate", 500, 50),
        ("IonFrigateSpeed", "Скорость ионного фрегата", "Ion Cannon Frigate Drive", "Frigate", "kus_ioncannonfrigate", 500, 50),
        ("LightDestroyerSpeed", "Скорость лёгкого эсминца", "Light Destroyer Drive", "Destroyer", "kus_destroyer", 750, 60),
        ("MissileDestroyerSpeed", "Скорость лёгкого ракетного эсминца", "Light Missile Destroyer Drive", "Destroyer", "kus_missiledestroyer", 750, 60),
        ("CarrierSpeed", "Скорость носителя", "Carrier Drive", "Destroyer", "kus_carrier", 750, 60),
        ("HeavyDestroyerSpeed", "Скорость тяжёлого эсминца", "Heavy Destroyer Drive", "Destroyer", "kus_heavycruiser", 1000, 75),
    ):
        aliases = {"LightFighterSpeed": "light interceptor drive", "InterceptorSpeed": "heavy interceptor drive", "MultigunCorvetteSpeed": "heavy Corvette drive"}
        add(key, "manaan", ru, en, price, seconds, ["Advanced" + group + "Drive"], [effect(target, "MAXSPEED", 1.25)], "Индивидуальный уровень: целевые 125% исходной скорости.", aliases.get(key, en))
    add("LightFighterBurn", "manaan", "Ускорение лёгкого истребителя", "Light Fighter Acceleration", 200, 25,
        ["AdvancedFighterDrive"], [effect("kus_scout", "ENGINEACCEL", .8)], "Время разгона ×0.8; максимальная скорость не меняется.", "light interceptor burn")
    for key, ru, en, cost, seconds in (
        ("PlasmaWeapons", "Плазменные орудия", "Plasma Weapons", 250, 25),
        ("IonCannons", "Ионные орудия", "Ion Cannons", 1000, 70),
        ("GuidedMissiles", "Управляемые ракеты", "Guided Missiles", 750, 60),
        ("Minelaying", "Минные системы", "Minelaying Technology", 750, 50),
        ("HeavyGuns", "Тяжёлые орудия", "Heavy Guns", 1200, 75),
        ("SalvageSystems", "Системы захвата", "Salvage Systems", 500, 40),
    ):
        fx = [effect(s, "WeaponDamage", 1.10) for s in ("kus_destroyer", "kus_heavycruiser")] if key == "HeavyGuns" else []
        add(key, "soban", ru, en, cost, seconds, effects=fx, note="Добровольное усиление пушечного вооружения лёгкого/тяжёлого эсминца на10%; не дополнительное условие тяжёлого эсминца." if fx else "")
    add("PlasmaBombs", "soban", "Улучшенные плазменные бомбы", "Improved Plasma Bombs", 1500, 45,
        ["PlasmaWeapons"], [effect(s, "UseSpecialWeaponsInNormalAttack", kind="ability")
                           for s in ("kus_attackbomber", "kus_assaultfrigate")],
        "Открывает улучшенный плазменный боеприпас против подсистем для бомбардировщика и плазменных установок штурмового фрегата. Обычные пушки фрегата не усиливает.")
    add("ProximityDetector", "paktu", "Стэлс-детектор", "Proximity Detector", 500, 40)
    add("SensorArray", "paktu", "Сенсорная батарея", "Sensor Array", 600, 50)
    add("EnhancedScanning", "paktu", "Улучшенное сканирование", "Enhanced Scanning", 500, 40, ["SensorArray"],
        [effect("kus_sensorarray", "SensorPing", kind="ability"), effect("kus_sensorarray", "CloakDetection", 4)], "Пинг и обнаружение маскировки сенсорной батареей.")
    add("HyperspaceSensors", "paktu", "Сенсоры гиперпространства", "Hyperspace Sensors", 400, 40, ["SensorArray"], note="Штатная подсистема HyperspaceSensor на сенсорной батарее; работает после исследования.")
    for key, ru, en, cost, seconds in (
        ("FastTrackingTurrets", "Скоронаводящиеся орудия", "Fast-Tracking Turrets", 500, 45),
        ("DefenderSubsystems", "Подсистемы Защитника", "Defender Subsystems", 400, 40),
        ("DroneTechnology", "Беспилотные технологии", "Drone Technology", 1200, 80),
        ("ImprovedManufacturing", "Улучшенное производство", "Improved Manufacturing", 1200, 75),
        ("RepairSystems", "Системы ремонта", "Repair Systems", 300, 35),
    ):
        fx = [effect(s, "BUILDSPEED", 1.30) for s in ("kus_mothership", "kus_carrier")] if key == "ImprovedManufacturing" else []
        add(key, "somtaaw", ru, en, cost, seconds, effects=fx, note="Скорость производства Материнского корабля и носителей ×1.3; очередь остаётся последовательной." if fx else "")
    for key, ru, en, cost, seconds in (
        ("DefenseField", "Генератор защитного поля", "Defense Field Generator", 1200, 80),
        ("GravityGenerator", "Генератор гравитационного поля", "Gravity Generator", 1000, 70),
        ("CloakGenerator", "Генератор маскировки", "Cloak Generator", 1000, 75),
        ("HyperspaceGenerator", "Генератор гиперпространства", "Hyperspace Generator", 1000, 75),
    ):
        fx = [effect(s, "Hyperspace", kind="ability") for s in ("kus_mothership", "kus_carrier")] if key == "HyperspaceGenerator" else []
        add(key, "sjet", ru, en, cost, seconds, effects=fx)
    requirements = {
        "kus_scout": ["FighterDrive"], "kus_interceptor": ["FighterDrive", "FighterChassis"],
        "kus_attackbomber": ["FighterDrive", "FighterChassis", "PlasmaWeapons"],
        "kus_cloakedfighter": ["FighterDrive", "FighterChassis", "CloakGenerator"],
        "kus_lightcorvette": ["CorvetteDrive"], "kus_heavycorvette": ["CorvetteDrive", "CorvetteChassis"],
        "kus_multiguncorvette": ["CorvetteDrive", "CorvetteChassis", "FastTrackingTurrets"],
        "kus_minelayercorvette": ["CorvetteDrive", "CorvetteChassis", "Minelaying"],
        "kus_supportfrigate": ["FrigateDrive"], "kus_assaultfrigate": ["FrigateDrive", "FrigateChassis", "PlasmaWeapons"],
        "kus_ioncannonfrigate": ["FrigateDrive", "FrigateChassis", "IonCannons"],
        "kus_dronefrigate": ["FrigateDrive", "FrigateChassis", "DroneTechnology"],
        "nku_barricadefrigate": ["FrigateDrive", "FrigateChassis", "DefenseField"],
        "kus_defender": ["FighterChassis", "DefenderSubsystems"],
        "kus_repaircorvette": ["CorvetteChassis", "RepairSystems"],
        "kus_salvagecorvette": ["CorvetteChassis", "SalvageSystems"],
        "kus_carrier": ["DestroyerDrive"], "kus_destroyer": ["DestroyerDrive", "DestroyerChassis"],
        "kus_missiledestroyer": ["DestroyerDrive", "DestroyerChassis", "GuidedMissiles"],
        "kus_heavycruiser": ["AdvancedDestroyerDrive", "AdvancedDestroyerChassis"],
        "kus_resourcecollector": [], "kus_resourcecontroller": [], "kus_probe": [],
        "kus_proximitysensor": ["ProximityDetector"], "kus_sensorarray": ["SensorArray"],
        "kus_gravwellgenerator": ["GravityGenerator"], "kus_cloakgenerator": ["CloakGenerator"],
    }
    return dict(version="NKR-research-v1", date="2026-10-21", modules=MODULES, technologies=techs,
                requirements={k: ["NKR_" + x for x in v] for k, v in requirements.items()},
                station_rule=dict(race="tai", requires="HyperspaceGenerator", implemented=False, note="Станция только Новотаииданам; условие подключается вместе с их будущим классовым деревом."),
                decisions=["Минный корвет требует Минные системы вместо FastTrackingTurrets", "Общие усовершенствования дают бонус классу", "Индивидуальная скорость многопушечного, не тяжёлого корвета: последнее уточнение пользователя", "Плазменные орудия открывают бомбардировщик и штурмовой фрегат; улучшенные бомбы отдельно открывают специальный боеприпас против подсистем обоим кораблям", "Броневые EN Chassis из пользовательского черновика сохранены в source_en, в интерфейсе Armor"],
                tuning_status="first-pass proposal; no native-engine validation")


def closure(design, requested):
    by_id = {row["id"]: row for row in design["technologies"]}
    found, visiting = set(), set()
    def visit(key):
        if key in visiting: raise ValueError("Research cycle: " + key)
        if key in found: return
        visiting.add(key)
        for req in by_id[key]["requires"]: visit(req)
        visiting.remove(key); found.add(key)
    for key in requested: visit(key)
    return [row for row in design["technologies"] if row["id"] in found]


def path_cost(design, requested):
    techs = closure(design, requested)
    modules = [m for m in design["modules"] if any(t["module"] == m["id"] for t in techs)]
    return dict(technologies=[t["id"] for t in techs], modules=[m["id"] for m in modules],
                research_cost=sum(t["cost"] for t in techs), module_cost=sum(m["cost"] for m in modules),
                cost=sum(t["cost"] for t in techs) + sum(m["cost"] for m in modules),
                base_research_time=sum(t["time"] for t in techs), module_time=sum(m["time"] for m in modules))
