"""Explicit RU/EN UI pairs; missing translations fail the build."""

EN = {
    "Ромб: четыре лёгких корвета, 1+2+1": "Diamond: four light corvettes, 1+2+1",
    "Ромб": "Diamond", "Генераторы": "Generators", "Инженеры": "Engineering Ships",
    "Фрегаты поддержки": "Support Frigates", "Специальные фрегаты": "Special Frigates",
    "Лёгкие эсминцы": "Light Destroyers", "Новокушане": "Novokushan", "Новотаиидане": "Neo-Taiidan",
    "Лёгкий истребитель": "Light Fighter", "Перехватчик": "Interceptor",
    "Штурмовой бомбардировщик": "Attack Bomber", "Стэлс-истребитель": "Cloaked Fighter",
    "Защитный истребитель": "Defense Fighter", "Лёгкий корвет": "Light Corvette",
    "Тяжёлый корвет": "Heavy Corvette", "Многопушечный корвет": "Multigun Corvette",
    "Минный корвет": "Minelayer Corvette", "Фрегат поддержки": "Support Frigate",
    "Штурмовой фрегат": "Assault Frigate", "Ионный фрегат": "Ion Cannon Frigate",
    "Дронный фрегат": "Drone Frigate", "Фрегат защитного поля": "Defense Field Frigate",
    "Лёгкий эсминец": "Light Destroyer", "Лёгкий ракетный эсминец": "Light Missile Destroyer",
    "Тяжёлый эсминец": "Heavy Destroyer", "Носитель": "Carrier", "Защитник": "Defender",
    "Абордажный корвет": "Salvage Corvette", "Ремонтный корвет": "Repair Corvette",
    "Генератор маскировки": "Cloak Generator", "Генератор гравитационного поля": "Gravity Well Generator",
    "Сенсорная батарея": "Sensor Array", "Сборщик ресурсов": "Resource Collector",
    "Ресурсный контроллер": "Resource Controller", "Разведывательный зонд": "Probe",
    "Датчик приближения": "Proximity Sensor", "Исследовательская станция": "Research Station",
    "Новокушане — свободная проба": "Novokushan — Fleet Showcase",
    "Новотаиидане — свободная проба": "Neo-Taiidan — Fleet Showcase",
    "Новокушане и Новотаиидане — проба флота": "Novokushan and Neo-Taiidan — Fleet Preview",
    "Выбрать расу": "Choose a faction",
    "Свободная проба флота. B — постройка, 1 — общий вид. Все проекты открыты; науки нет. Цели для стрельбы находятся впереди флота.":
        "Fleet showcase. B: construction; 1: fleet view. All ship designs are unlocked. Practice targets are ahead of the fleet.",
    "Новокушане — исследовательская проба": "Novokushan — Research Trial",
}
BRANCH_EN = {"naabal": "Chassis", "manaan": "Drives", "soban": "Weapons",
             "sjet": "Special Technologies", "somtaaw": "AI Systems", "paktu": "Sensors"}


def english(text):
    if text not in EN:
        raise ValueError("Missing English UI translation: " + text)
    return EN[text]


def research_description_en(tech):
    key, effects = tech["key"], tech["effects"]
    if key == "PlasmaWeapons":
        detail = "Unlocks attack bombers and assault frigates, together with their chassis and drives."
    elif key == "PlasmaBombs":
        detail = "Improved anti-subsystem plasma bombs for attack bombers and assault-frigate bomb launchers. Does not improve the frigate's guns."
    elif key == "HyperspaceSensors":
        detail = "Enables hyperspace detection on Sensor Arrays."
    elif key == "EnhancedScanning":
        detail = "Enables sensor ping and cloaked-ship detection on Sensor Arrays."
    elif key == "LightFighterBurn":
        detail = "Reduces light-fighter acceleration time by 20%; maximum speed is unchanged."
    elif key == "ImprovedManufacturing":
        detail = "Increases Mothership and Carrier construction speed by 30%. Production remains sequential."
    elif key == "HeavyGuns":
        detail = "Increases gun damage on light and heavy destroyers by 10%. Optional; not required to build heavy destroyers."
    elif key == "HyperspaceGenerator":
        detail = "Enables hyperspace jumps for Motherships and Carriers."
    elif effects and effects[0]["name"] in ("MAXHEALTH", "MAXSPEED"):
        stat = "hull strength" if effects[0]["name"] == "MAXHEALTH" else "maximum speed"
        detail = f"Upgrades {stat} to {effects[0]['value'] * 100:g}% of the base value."
        if len(effects) > 1:
            detail += " Applies to the whole class and unlocks further upgrades."
    else:
        detail = "Unlocks the associated ships and technologies."
    return tech["en"] + ". " + detail
