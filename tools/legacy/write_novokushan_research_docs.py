"""Publish research design tables/diagram data in the workspace, not in the game."""
import json
from pathlib import Path

from novokushan_research_design import path_cost

PROJECT = Path(__file__).resolve().parents[1]


def main():
    design = json.loads((PROJECT / "local/novokushan/research-design.json").read_text(encoding="utf-8"))
    manifest = json.loads((PROJECT / "local/fleet-preview/manifest.json").read_text(encoding="utf-8"))
    strings = manifest["strings"]
    localized_count = sum('\t' in line for line in (PROJECT/'local/fleet-preview/source/locale/Russian/vrcampaign.ucs').read_text(encoding='utf-16').splitlines())
    names = {r["id"]: strings[r["title"].lstrip('$')] for r in manifest["ships"]["kus"]}
    names["kus_mothership"] = "Материнский корабль"
    techs = {t["id"]: t for t in design["technologies"]}
    modules = {m["id"]: m for m in design["modules"]}
    lines = ['# Новокушане: исследовательское дерево v1', '',
        '21 октября 2026. Основа — подробное дерево Дмитрия; цены, времена и величины бонусов — первая настройка для пробы. Схема реализуется только у Новокушан. Научная сборка Новотаиидан и её классовое дерево — следующий отдельный этап; станция по-прежнему только у них.', '',
        '## Зафиксированные уточнения', '',
        '- Минному корвету нужны двигатели/шасси корветов и **Минные системы**, не скоронаводящиеся орудия.',
        '- Общие усовершенствованные шасси/двигатели сами дают бонус классу и открывают продолжение. Предложенные ступени: **115% базовых HP /110% скорости**; индивидуальные броня/двигатель — целевые **130% HP /125% скорости**. Это абсолютные целевые уровни, не обещание подтверждённого в движке порядка сочетания модификаторов.',
        '- Последнее уточнение Дмитрия: индивидуальные двигатели **многопушечного** корвета. Предыдущее английское heavy Corvette drive сохранено как исходный текст, его русский смысл исправлен по уточнению.',
        '- **Плазменные орудия / Plasma Weapons —250RU/25с**: общее условие бомбардировщика и штурмового фрегата. **Улучшенные плазменные бомбы / Improved Plasma Bombs —1500RU/45с**, после плазменных орудий: отдельный специальный боеприпас против подсистем для обоих кораблей, по механике UseSpecialWeaponsInNormalAttack из Classic. Обычные пушки штурмового фрегата не усиливает. Цены/время улучшения совпадают с референсом Hgn/Vgr Classic; характеристики двух кушанских установок остаются собственной пробной настройкой.',
        '- Heavy Guns — добровольное усиление урона пушечных лёгкого/тяжёлого эсминцев на10%. Оно не становится новым обязательным условием тяжёлого эсминца.',
        '- Новая игровая единица: **фрегат защитного поля**, существующий подготовленный корпус VR nku_barricadefrigate, механика поля штатного Hgn. Первая настройка1100 RU/55 с/16000HP, общий лимит NFP_Special2 вместе с дронным фрегатом. Это не автоматическое отождествление с CUT_Ship_Kus_SupportFrigate.',
        '- Носитель, по прежнему канону UI, остаётся «Носитель»; «авианосец» — понятный алиас обсуждения. С’Джет сохраняет ранее согласованное написание. «Воягры» — сленг Дмитрия; рабочая словарная форма Vaygr — «вэйгры».', '',
        '## Научная сборка и очередь', '',
        'Шесть разных научных кораблей, по одному каждого профиля. Все шесть доступны без исследований; первый профиль можно выбрать свободно. Наабал использует основной корпус кольца, остальные секции работают самостоятельно и пристыковываются при наличии основы. Последовательные ограничения штатного скрипта сняты, физические стыковка/эффекты сохранены. Реальное поведение сборки и подсчёт скрытых исследовательских подсистем ещё требуют теста HWRM.', '',
        'Одна общая научная очередь. Профиль проверяется RequiredSubSystems, связи между технологиями — RequiredResearch. Полное кольцо стоит **2200RU**; цена каждого профиля ниже. Каждая секция занимает1 из общего пула генераторов18, отдельный профиль ограничен1 — всего не более6 научных секций. Новые UI-вкладки/иконки не добавлены.', '',
        '| Модуль | Направление | RU | Постройка, базовые с | Техническая секция |', '|---|---|---:|---:|---|']
    for m in modules.values(): lines.append(f'| {m["ru"]} / {m["en"]} | {m["branch"]} | {m["cost"]} | {m["time"]} | `{m["ship"]}` |')
    lines += ['', 'При потере профильной секции новые работы её ветки недоступны; полученные технологии и постройка уже открытых проектов не требуют сохранять лабораторию. Пауза/поведение уже выполняющегося задания определяется штатным ResearchManager и пока не проверено. Скрипт не отменяет очередь и не убивает другие секции вручную.', '',
        '## Цены и базовое время исследований', '',
        'Время — исходное поле Time. Ориентир ускорения Classic: t=T/√(n+1), где n — активные секции. На одной секции 70.7% T, при полном кольце37.8% T. Нулевая длительность внутренних эффектов не означает ещё одну бесплатную очередь: это сопровождающие применения уже оплаченного исследования по штатному образцу InstaAdvancedFrigateTech.', '']
    diagrams = []
    for module in modules.values():
        group = [t for t in techs.values() if t['module'] == module['id']]
        lines += ['### ' + module['ru'] + ' — ' + module['branch'], '', '| RU / EN | RU | Базовые с | Предыдущее открытие | Эффект |', '|---|---:|---:|---|---|']
        graph = ['flowchart LR', f'  M["{module["ru"]}: {module["branch"]}<br/>{module["cost"]} RU / {module["time"]} с"]']
        for t in group:
            prerequisites = ', '.join(techs[x]['ru'] for x in t['requires']) or 'Только профильный модуль'
            effect = t['note'] or 'Открытие связанных проектов'
            lines.append(f'| {t["ru"]}<br>{t["en"]} | {t["cost"]} | {t["time"]} | {prerequisites} | {effect} |')
            graph.append(f'  {t["key"]}["{t["ru"]}<br/>{t["cost"]} RU / {t["time"]} с"]')
            for parent in t['requires'] or ['M']:
                graph.append('  ' + ('M' if parent == 'M' else parent.removeprefix('NKR_')) + ' --> ' + t['key'])
        lines += ['', '```mermaid', *graph, '```', '']
        diagrams += ['%% ' + module['ru'], *graph, '']
    lines += ['## Открытия кораблей и полная цена доступа', '',
        'Стоимость включает все необходимые научные секции и исследования с нуля, без самого корабля. Общие узлы оплачиваются один раз. Уже имеющиеся секции/технологии уменьшают цену следующего проекта. Выданный в исходном флоте корабль не доказывает, что его проект уже разрешён к постройке.', '',
        '| Корабль | Обязательные технологии | Исследования, RU | Секции, RU | Доступ всего, RU | Базовая научная работа, с |', '|---|---|---:|---:|---:|---:|']
    ships = []
    for ident, reqs in design['requirements'].items():
        price = path_cost(design, reqs)
        ship = dict(id=ident, ru=names[ident], requires=reqs, **price)
        ships.append(ship)
        lines.append(f'| {names[ident]} | {" + ".join(techs[k]["ru"] for k in reqs) or "Без исследований"} | {price["research_cost"]} | {price["module_cost"]} | {price["cost"]} | {price["base_research_time"]} |')
    lines += ['', 'Материнский корабль исходный, не новый строительный заказ. Сборщик, ресурсный контроллер и обычный зонд доступны сразу. Ремонтный/абордажный корветы теперь за технологиями по указанию Дмитрия. Носитель не производит эсминцы, другие носители и ресурсный контроллер; исследования этот охват не расширяют.', '',
        'Базовые90000HP тяжёлого эсминца сохранены. Условия его проекта включают обе общие усовершенствованные ступени: при ожидаемом общем бонусе это103500HP и110% исходной скорости; отдельная броня целится в117000HP. Нативный порядок модификаторов ещё должен быть проверен.', '',
        '## Сенсоры и гиперпространство', '',
        '- Сенсорная батарея сохраняет большой пассивный обзор. Enhanced Scanning включает её SensorPing и CloakDetection4; бесплатного обнаружения маскировки до открытия больше нет.',
        '- Hyperspace Sensors использует штатный тип подсистемы HyperspaceSensor на креплении NKRHyperspaceSensor батареи. Три узла Position/Direction/Rest добавлены в исходный HOD по штатному образцу. Первоначальная ошибочная привязка Root вызвала падение загрузки; после исправления Дмитрий подтвердил успешный запуск. Реальные сигнатуры после исследования ещё не проверены. Подробности — [FLEET_PREVIEW.md](FLEET_PREVIEW.md).',
        '- Hyperspace Generator открывает гиперпрыжки Материнского корабля и носителей через штатное улучшение способности. Не добавляет станцию Новокушанам.',
        '- Условие «исследовательская станция = генератор гиперпространства» сохраняется для будущего дерева Новотаиидан. Сейчас их полигон остаётся без исследований; привязать станцию к недоступному им новокушанскому открытию нельзя.', '',
        '## Проба и совместимость', '',
        '- В Extra Missions добавлена отдельная **«Новокушане — исследовательская проба»**: Материнский корабль, сборщик, контроллер, зонд и20000RU; без выданных технологий и лабораторий. По исходной схеме первый лёгкий истребитель также требует Fighter Drive.',
        '- Старый полигон Новокушан остаётся показом флота с выданными технологиями; там есть все шесть секций и баррикадный фрегат. Он не проверяет развитие с нуля.',
        '- Скирмиш использует те же зависимости. ИИ пока не обучен новому дереву; не считать его поведение проверенным.',
        '- Три главы HWVR сохраняют сценарные бесплатные открытия: разрешённым проектам выдаются необходимые технологии, научная очередь в главах заблокирована. Реплики/объявления технологий не переписывались. Это исследовательская проба фракции, не решение о платной науке кампании.', '',
        '## Локализация RU/EN', '',
        f'В обеих версиях{localized_count} совпадающих ID:{localized_count-len(strings)} строк прежней кампании и{len(strings)} новых строк флота/науки. Новые корабли, лимиты, лаборатории, названия/описания исследований и сцены имеют отдельные переводы. В BIG находятся locale:Russian и locale:English, общий locale использует английский fallback. Запускатель по умолчанию русский; `start_campaign.ps1 -Language English` выбирает английский. Выбор языка в движке и специальный боеприпас новой версии ещё требуют игрового теста.', '',
        '## Статус проверки', '',
        'Граф, отсутствие циклов, реальные LUA-таблицы, условия проектов, цены/время, лимиты, бесплатные сценарные открытия, исправления минного/многопушечного корветов и подготовленный VR-корпус проверяются отдельным верификатором. Это данные и API-моки; не нативная проверка HWRM. Перед балансной оценкой проверить свободный выбор секций, сборку, одну очередь/ускорение, автоматические эффекты, фактические HP/скорости, исследовательское меню и выпуск кораблей.', '',
        'Источники: пользовательская схема21 октября, [референс Classic](HW2_CLASSIC_RESEARCH.md), [общие решения науки](epics/NOVOKUSHAN_RESEARCH_MODULES.md). Данные/исходные EN-алиасы: [research-design.json](../local/novokushan/research-design.json). Воспроизведение: `rebuild_fleet_preview.ps1`.', '']
    (PROJECT/'docs/NOVOKUSHAN_RESEARCH_TREE.md').write_text('\n'.join(lines), encoding='utf-8')
    data = {**design, 'ships': ships, 'names': names}
    (PROJECT/'local/novokushan/research-diagram-data.json').write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    # Keep user slang as an alias, not the displayed race name.
    path = PROJECT/'localization/glossary.json'
    glossary = json.loads(path.read_text(encoding='utf-8'))
    race = next(r for r in glossary if r['en'] == 'Vaygr')
    race['aliases'] = sorted(set(race.get('aliases', []) + ['воягры', 'Воягры', 'воягров']))
    race['note'] = 'Рабочая форма проекта — вэйгры; окончательная форма на проверке. «Воягры» и производные — сленг Дмитрия, уточнение21 октября2026; не использовать как каноническое имя в интерфейсе.'
    for module in modules.values():
        existing = next((r for r in glossary if r.get('research_module') == module['id']), None)
        row = existing or dict(section='Исследовательские корабли Новокушан', research_module=module['id'])
        row.update(en=module['en']+' Research Module', ru='Исследовательский модуль '+module['ru']+' — '+module['branch'],
                   status='confirmed_by_user', native_reference=module['ship'],
                   note='Профиль и имя корабля согласованы21 октября2026. В схеме исследований также «Исследовательский центр '+module['ru']+'». EN — рабочий перевод; штатный прототип Research Ship остаётся отдельным исходным именем.')
        if not existing: glossary.append(row)
    barrier = next((r for r in glossary if r.get('novokushan_project') == 'defense_field_frigate'), None)
    if not barrier:
        glossary.append(dict(section='Корабли Новокушан', en='Defense Field Frigate', ru='Фрегат защитного поля',
            novokushan_project='defense_field_frigate', native_reference='nku_barricadefrigate', status='confirmed_by_user',
            note='Роль задана Дмитрием21 октября2026; подготовленный VR-корпус Barricade Frigate, механика штатного Hgn. Не объединяет исходные определения Ship_Hgn_BarricadeFrigate и CUT_Ship_Kus_SupportFrigate.'))
    for tech in techs.values():
        existing = next((r for r in glossary if r.get('research_id') == tech['id']), None)
        row = existing or dict(section='Исследования Новокушан', research_id=tech['id'])
        row.update(en=tech['en'], ru=tech['ru'], status='confirmed_by_user',
                   note='Исследовательский центр ' + modules[tech['module']]['ru'] + '. Основа — схема Дмитрия21 октября2026; цены/время отдельно как пробная настройка. Исходный EN: ' + tech['source_en'] + '.')
        row['aliases'] = sorted(set(row.get('aliases', []) + ([tech['source_en']] if tech['source_en'] != tech['en'] else [])))
        if not existing: glossary.append(row)
    path.write_text(json.dumps(glossary, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(document='docs/NOVOKUSHAN_RESEARCH_TREE.md', technologies=len(techs), diagrams=6,
                         module_cost=sum(m['cost'] for m in modules.values()), paths={s['ru']:s['cost'] for s in ships if s['id'] in ('kus_scout','kus_interceptor','kus_assaultfrigate','kus_ioncannonfrigate','kus_destroyer','kus_heavycruiser')}), ensure_ascii=False))


if __name__ == '__main__': main()
