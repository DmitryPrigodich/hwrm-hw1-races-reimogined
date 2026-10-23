# Эпик: Новокушане / Novokushan

Начат 20 октября 2026 года по обсуждению с Дмитрием. Этот файл — общая точка входа и справочник исходных рас. **Актуальный принятый состав Новокушан из 28 проектов, лимиты и предложение исследований находятся в [NOVOKUSHAN_DESIGN.md](NOVOKUSHAN_DESIGN.md)**. Штатные списки ниже сохранены для сравнения и не заменяют новый состав.

## Принятое направление

- Основа — уже существующие кушане, с выбранными изменениями в сторону игрового устройства Homeworld 2.
- **Приоритет для цен, экономики и баланса — Homeworld 2 Classic, предпочтительнее HWRM.** Это требование Дмитрия от 20 октября. Численные параметры ещё не утверждены и в игровые файлы этим обсуждением не перенесены.
- Штатные HWRM-корпуса и функции используем как техническую базу. Для малых боевых кораблей нужны отряды; число корпусов в отряде, цена отряда и лимиты рассматриваются раздельно.
- Кампанийные открытия и объявления технологий сохраняются. Реплика о готовой технологии сама по себе не создаёт обязательное платное исследование.
- Технические названия `novokushan`, `nku_*` и другие существующие ID сохраняются до стабилизации мода.
- Последнее уточнение Дмитрия: истребители и три боевых корвета — отряды, минный корвет одиночный. Бывший тяжёлый крейсер переименован в тяжёлый эсминец. Общий крупный кап 15, лёгкие эсминцы ≤10 вместе, тяжёлые ≤5, носители ≤4. Генераторы (исследовательский корабль, стэлс-генератор, гравицапа и сенсорная батарея) ≤6 каждого типа и ≤18 вместе; Защитники отдельно ≤4 групп по 4 аппарата. Инженеры ≤20 вместе; коллекторы 20, контроллеры 4. Носитель 4000 RU, лёгкий эсминец 1350, лёгкий ракетный 1500 (HW1 Classic), тяжёлый 2800. Наука — кольцо до шести секций с ускорением общей очереди по HW2. **Носитель — классический охват и последовательная стройка, без сверхтяжей и пока без контроллера; расширение до эсминцев снято.** Сенсорная батарея сразу имеет большой обзор, пинг и анти-стэлс открываются исследованиями. Две военная/мирная линии пока только техническая разведка. Само дерево исследований ещё предложено для обсуждения.
- [Наука двух рас принята](NOVOKUSHAN_RESEARCH_MODULES.md): Новокушанам — шесть инженерных направлений с киитами, [Новотаииданам](NEOTAIIDAN_DESIGN.md) — шесть классовых модулей. Новотаиидане копируют общую балансную основу, сохраняют научную сборку и дополнительно вызывают tai_researchstation с производством до фрегатов включительно. Её дополнительные функции отложены. У каждой расы одна общая очередь; Support Units и детальные работы/цены пока проектируются.

Предыдущие договорённости: [DESIGN_DIRECTION.md](../DESIGN_DIRECTION.md). Исходная кампанийная прогрессия: [QUEST_PROGRESSION.md](../QUEST_PROGRESSION.md).

## Имя: варианты для обсуждения

| Вариант | Смысл / статус |
|---|---|
| Новокушане / Novokushan | Нынешнее рабочее имя проекта; техническое имя уже используется. |
| Neo-Kushan; о людях Neo-Kushans | Предложение для английского отображаемого имени. Напрямую передаёт «новокушане»; окончательный выбор пока не сделан. |
| Neokushans | Предложенный Дмитрием вариант слитного написания; также не утверждён. |
| Kiithid | Уже существующее обозначение кланов во множественном числе, а не перевод «новокушане». Подходит по смыслу для союза/флотов кланов, если будет выбрана такая концепция. |

Официальное описание [Deserts of Kharak Expedition Guide](https://store.steampowered.com/app/433240/Deserts_of_Kharak_Expedition_Guide/) прямо поясняет kiithid как clans. [Homeworld: Revelations](https://modiphius.net/pages/homeworld) перечисляет отдельные Kushan Kiith — Naabal, Soban, S’jet и другие. Рекомендация Neo-Kushan — авторское предложение этого обсуждения, не найденное каноническое имя.

## Как читать справочные списки

Ниже штатные расовые типы, сгруппированные по классу. Кушане и хиигаряне показаны отдельно. RU приведены по [общему глоссарию](../../localization/GLOSSARY.md); новые названия внесены туда как рабочие, кроме явно подтверждённых Дмитрием. 20 октября приняты: Защитник / Defender, стэлс-истребитель / Cloaked Fighter, минный корвет / Minelayer Corvette, дронный фрегат / Drone Frigate, тягач / Mover. EN сверены по извлечённым английским таблицам игры. Численные цены HWRM намеренно не используются как утверждённый баланс HW2 Classic.

Базовый список включает строящиеся типы и Материнский корабль. Корабли, которые выдаёт сюжет, варианты одного корпуса, дроны и технические объекты оговорены отдельно. Группировка «вспомогательные» объединяет несколько технических build-family для удобства обсуждения.

## Кушане / Kushan

**28 основных типов: 27 строительных и Материнский корабль.** Дополнительные секции исследовательского корабля считаются вариантами одного типа.

| Класс RU / EN | Название RU | Название EN | Штатный ID |
|---|---|---|---|
| Истребители / Fighters | Разведчик | Scout | `kus_scout` |
| Истребители / Fighters | Перехватчик | Interceptor | `kus_interceptor` |
| Истребители / Fighters | Защитник | Defender | `kus_defender` |
| Истребители / Fighters | Ударный бомбардировщик | Attack Bomber | `kus_attackbomber` |
| Истребители / Fighters | Стэлс-истребитель | Cloaked Fighter | `kus_cloakedfighter` |
| Корветы / Corvettes | Лёгкий корвет | Light Corvette | `kus_lightcorvette` |
| Корветы / Corvettes | Тяжёлый корвет | Heavy Corvette | `kus_heavycorvette` |
| Корветы / Corvettes | Многопушечный корвет | Multi-Gun Corvette | `kus_multiguncorvette` |
| Корветы / Corvettes | Минный корвет | Minelayer Corvette | `kus_minelayercorvette` |
| Корветы / Corvettes | Ремонтный корвет | Repair Corvette | `kus_repaircorvette` |
| Корветы / Corvettes | Абордажный корвет | Salvage Corvette | `kus_salvagecorvette` |
| Фрегаты / Frigates | Штурмовой фрегат | Assault Frigate | `kus_assaultfrigate` |
| Фрегаты / Frigates | Ионный фрегат | Ion Cannon Frigate | `kus_ioncannonfrigate` |
| Фрегаты / Frigates | Фрегат поддержки | Support Frigate | `kus_supportfrigate` |
| Фрегаты / Frigates | Дронный фрегат | Drone Frigate | `kus_dronefrigate` |
| Эсминцы / Destroyers | Эсминец | Destroyer | `kus_destroyer` |
| Эсминцы / Destroyers | Ракетный эсминец | Missile Destroyer | `kus_missiledestroyer` |
| Крейсеры / Cruisers | Тяжёлый крейсер | Heavy Cruiser | `kus_heavycruiser` |
| Носители / Carriers | Носитель | Carrier | `kus_carrier` |
| Материнские корабли / Motherships | Материнский корабль | Mothership | `kus_mothership` |
| Вспомогательные / Utility | Сборщик ресурсов | Resource Collector | `kus_resourcecollector` |
| Вспомогательные / Utility | Ресурсный контроллер | Resource Controller | `kus_resourcecontroller` |
| Вспомогательные / Utility | Исследовательский корабль | Research Ship | `kus_researchship` |
| Вспомогательные / Utility | Зонд | Probe | `kus_probe` |
| Вспомогательные / Utility | Датчик приближения | Proximity Sensor | `kus_proximitysensor` |
| Вспомогательные / Utility | Сенсорный массив | Sensors Array | `kus_sensorarray` |
| Вспомогательные / Utility | Генератор гравитационного колодца | Gravwell Generator | `kus_gravwellgenerator` |
| Вспомогательные / Utility | Генератор маскировочного поля | Cloak Generator | `kus_cloakgenerator` |

У кушан нет штатной отдельной верфи / Shipyard. `kus_researchship_1`…`_5` — дополнительные секции Research Ship / Aux. Hubs. Дроны `kus_drone0`…`11`, исследовательская сборка `kus_researchstation` и учебная мишень не добавлены как самостоятельные проекты для расы. Наличие внутренних записей дронов в def_build не означает отдельный обычный заказ игрока.

**Support Frigate здесь — настоящий штатный кушанский фрегат поддержки.** Это не доказательство роли VR-определения `CUT_Ship_Kus_SupportFrigate`: для него предварительная гипотеза защитного поля сохраняется отдельно.

## Хиигаряне / Hiigaran

**23 основных типа: 22 строительных и Материнский корабль.** Это справочник штатного флота HW2 по локальным ресурсам HWRM; он не утверждает тождество численного баланса двух изданий.

| Класс RU / EN | Название RU | Название EN | Штатный ID |
|---|---|---|---|
| Истребители / Fighters | Разведчик | Scout | `hgn_scout` |
| Истребители / Fighters | Перехватчик | Interceptor | `hgn_interceptor` |
| Истребители / Fighters | Бомбардировщик | Bomber | `hgn_attackbomber` |
| Корветы / Corvettes | Пушечный корвет | Gunship | `hgn_assaultcorvette` |
| Корветы / Corvettes | Пульсарный корвет | Pulsar Gunship | `hgn_pulsarcorvette` |
| Корветы / Corvettes | Минный корвет | Minelayer | `hgn_minelayercorvette` |
| Фрегаты / Frigates | Зенитный фрегат | Flak Frigate | `hgn_assaultfrigate` |
| Фрегаты / Frigates | Торпедный фрегат | Torpedo Frigate | `hgn_torpedofrigate` |
| Фрегаты / Frigates | Ионный фрегат | Ion Cannon Frigate | `hgn_ioncannonfrigate` |
| Фрегаты / Frigates | Абордажный фрегат | Marine Frigate | `hgn_marinefrigate` |
| Фрегаты / Frigates | Фрегат защитного поля | Defense Field Frigate | `hgn_defensefieldfrigate` |
| Эсминцы / Destroyers | Эсминец | Destroyer | `hgn_destroyer` |
| Крейсеры / Cruisers | Линейный крейсер | Battlecruiser | `hgn_battlecruiser` |
| Носители / Carriers | Носитель | Carrier | `hgn_carrier` |
| Верфи / Shipyards | Верфь | Shipyard | `hgn_shipyard` |
| Материнские корабли / Motherships | Материнский корабль «Гордость Хиигары» | Mothership / Pride of Hiigara | `hgn_mothership` |
| Платформы / Platforms | Орудийная платформа | Gun Platform | `hgn_gunturret` |
| Платформы / Platforms | Ионная платформа | Ion Cannon Platform | `hgn_ionturret` |
| Вспомогательные / Utility | Сборщик ресурсов | Resource Collector | `hgn_resourcecollector` |
| Вспомогательные / Utility | Мобильный переработчик | Mobile Refinery | `hgn_resourcecontroller` |
| Вспомогательные / Utility | Зонд | Probe | `hgn_probe` |
| Вспомогательные / Utility | Датчик приближения | Proximity Sensor | `hgn_proximitysensor` |
| Вспомогательные / Utility | Зонд подавления сенсоров | Sensors Distortion Probe | `hgn_ecmprobe` |

Здесь `hgn_assaultfrigate` — **Flak Frigate**, а не кушанский Assault Frigate. Аналогично отображаемое имя `hgn_assaultcorvette` — **Gunship**. Отдельного обычного исследовательского корабля у хиигарян HW2 нет: исследования связаны с модулями. Производственные, исследовательские и сенсорные модули не включены в список корпусов.

### Отдельно: сюжетные и особые единицы HW2

| Класс RU / EN | RU / EN | Статус |
|---|---|---|
| Истребители / Fighters | Элитный бомбардировщик / Elite Bomber | `hgn_attackbomberelite`: сюжетный вариант, не обычная строительная ветка. |
| Корветы / Corvettes | Элитный пушечный корвет / Elite Gunship | `hgn_assaultcorvetteelite`: сюжетный вариант. |
| Фрегаты / Frigates | Фрегат капитана Собана / Captain Soban | `hgn_marinefrigate_soban`: именной вариант Marine Frigate. |
| Особые крупные корабли / Special capital ships | Дредноут / Dreadnaught | `hgn_dreadnaught`: сюжетный корабль, не обычная постройка. |
| Особые крупные корабли / Special capital ships | Саджуук / Sajuuk | Корабль Предтеч под управлением игрока по сюжету; не обычный хиигарский строительный тип. |
| Корветы / Corvettes | Тягач / Mover | `kpr_mover`: техника Предтеч, специальная кампанийная доступность. |

Варианты верфи `hgn_shipyard_spg` / `hgn_shipyard_elohim`, дроны и технические объекты не считаются дополнительными основными проектами.

## Вэйгры / Vaygr

Добавлено по просьбе Дмитрия 20 октября 2026 года для сравнения со штатными кушанами и хиигарянами. Это справочный флот HW2 по локальным ресурсам HWRM; его перечисление не меняет состав Новокушан или роли Радаа. Новые русские названия — рабочие, внесены в общий глоссарий на проверку.

**24 основных типа: 23 строительных и флагман.** Отдельная специальная запись `Vgr_PlanetKillerMissile` в def_build не включена в обычное строительство флота.

| Класс RU / EN | Название RU | Название EN | Штатный ID |
|---|---|---|---|
| Истребители / Fighters | Разведчик | Survey Scout | `vgr_scout` |
| Истребители / Fighters | Штурмовик | Assault Craft | `vgr_interceptor` |
| Истребители / Fighters | Бомбардировщик | Bomber | `vgr_bomber` |
| Истребители / Fighters | Лучевой истребитель | Lance Fighter | `vgr_lancefighter` |
| Корветы / Corvettes | Ракетный корвет | Missile Corvette | `vgr_missilecorvette` |
| Корветы / Corvettes | Лазерный корвет | Laser Corvette | `vgr_lasercorvette` |
| Корветы / Corvettes | Командный корвет | Command Corvette | `vgr_commandcorvette` |
| Корветы / Corvettes | Минный корвет | Minelayer | `vgr_minelayercorvette` |
| Фрегаты / Frigates | Штурмовой фрегат | Assault Frigate | `vgr_assaultfrigate` |
| Фрегаты / Frigates | Тяжёлый ракетный фрегат | Heavy Missile Frigate | `vgr_heavymissilefrigate` |
| Фрегаты / Frigates | Фрегат проникновения | Infiltrator Frigate | `vgr_infiltratorfrigate` |
| Эсминцы / Destroyers | Эсминец | Destroyer | `vgr_destroyer` |
| Крейсеры / Cruisers | Линейный крейсер | Battlecruiser | `vgr_battlecruiser` |
| Носители / Carriers | Носитель | Carrier | `vgr_carrier` |
| Верфи / Shipyards | Верфь | Shipyard | `vgr_shipyard` |
| Флагманы / Flagships | Флагман вэйгров | Vaygr Flagship | `vgr_mothership` |
| Платформы / Platforms | Орудийная платформа | Gun Platform | `vgr_weaponplatform_gun` |
| Платформы / Platforms | Тяжёлая ракетная платформа | Heavy Missile Platform | `vgr_weaponplatform_missile` |
| Платформы / Platforms | Гиперврата | Hyperspace Gate | `vgr_hyperspace_platform` |
| Вспомогательные / Utility | Сборщик ресурсов | Resource Collector | `vgr_resourcecollector` |
| Вспомогательные / Utility | Мобильный переработчик | Mobile Refinery | `vgr_resourcecontroller` |
| Вспомогательные / Utility | Зонд | Probe | `vgr_probe` |
| Вспомогательные / Utility | Датчик приближения | Proximity Sensor | `vgr_probe_prox` |
| Вспомогательные / Utility | Зонд подавления сенсоров | Sensors Distortion Probe | `vgr_probe_ecm` |

Названия EN в основной таблице — из DisplayedName строительного списка. В определениях самих кораблей есть варианты: Scout у `vgr_scout`, Minelayer Corvette у `vgr_minelayercorvette`, Proximity Detector у `vgr_probe_prox`, Sensor Distortion Probe у `vgr_probe_ecm`. Это варианты подписи тех же типов, а не дополнительные корпуса. Для Minelayer сохраняется принятое Дмитрием имя «минный корвет».

### Отдельно: сюжетные единицы и объекты Vaygr

| Класс RU / EN | RU / EN | Статус |
|---|---|---|
| Флагманы / Flagships | Флагман Макаана / Makaan | `vgr_mothership_makaan`: именной сюжетный вариант флагмана. |
| Станции / Stations | Командная станция / Command Station | `vgr_commstation`: объект кампании. |
| Станции / Stations | Командная станция «Таддис Саббах» / Command Station Thaddis Sabbah | `vgr_prisonstation`: сюжетная станция. |
| Особые крупные корабли / Special capital ships | Уничтожитель планет / Planet Killer | `vgr_planetkiller`: сюжетная единица. |
| Ракеты / Missiles | Оружие уничтожения атмосферы с низкой орбиты / Low Orbit Atmosphere Deprivation Weapon | `vgr_planetkillermissile`: сюжетное оружие; в специальной строительной записи подписано Planet Killer. |

У вэйгров, как и у хиигарян HW2, исследовательская инфраструктура выполнена модулями; отдельного обычного Research Ship в этом списке нет.

## HWVR: что добавляется в строительство по миссиям

Источник — **полная Quest 1.1.0-16520**. Порядок взят из MissionDatabase, а не сортировкой M-номеров. Столбец «добавляется» — разница между whitelist текущей и предыдущей главы; он не заявляет, что тип становится доступен ровно в момент FI_Unlock. Объявления подключены, однако обычно корпус уже находится в whitelist сцены.

В список включён весь строительный флот стороны игрока — даже когда ShipDefinition имеет префикс `Hgn`. Фильтр только по `Ship_Kus_*` ошибочно потерял бы большую часть корветов и крупных кораблей.

| Порядок | Миссия RU / EN | Добавляется относительно предыдущей главы: RU / EN | Класс RU / EN | Всего строительных типов |
|---|---|---|---|---:|
| T1, отдельно | Обучение / Tutorial | Перехватчик / Interceptor | Истребители / Fighters | 1 |
| 1 · M1 | Испытательный полигон Хиигары / Hiigara Proving Grounds | Базовый набор: Разведчик / Scout; Перехватчик / Interceptor; Ударный бомбардировщик / Attack Bomber; Сборщик ресурсов / Resource Collector | Истребители / Fighters; вспомогательные / Utility | 4 |
| 2 · M7 | Тёмная сторона Ангельской Луны / Dark Side of Angel Moon | Новых типов нет | — | 4 |
| 3 · M3 | Рейд на Гиббас / The Gybbas Raid | Тяжёлый корвет / Heavy Corvette | Корветы / Corvettes | 5 |
| 4 · M4 | Потерянный эсминец / The Lost Destroyer | Инженерный корвет / Engineer Craft | Корветы / Corvettes | 6 |
| 5 · M5 | Верфь Хиигары / Hiigara Shipyard | Многопушечный корвет / Multi-Gun Corvette | Корветы / Corvettes | 7 |
| 6 · M6 | Оружие / The Weapon | Штурмовой фрегат / Assault Frigate | Фрегаты / Frigates | 8 |
| 7 · M9 | Система Тенхаузер / Tenhauser System | Баррикадный фрегат / Barricade Frigate | Фрегаты / Frigates | 9 |
| 8 · M10 | Добывающий комплекс Внешнего рифа / Outer Reef Mining Facility | Ионный фрегат / Ion Cannon Frigate | Фрегаты / Frigates | 10 |
| 9 · M11 | Создатели оружия / The Weapon Architects | Эсминец / Destroyer | Эсминцы / Destroyers | 11 |
| 10 · M8 | Наступление на Гиббас / The Gybbas Offensive | Баллистический эсминец / Ballistic Destroyer | Эсминцы / Destroyers | 12 |
| 11 · M13 | Возвращение на Хиигару / Return to Hiigara | Тяжёлый крейсер / Heavy Cruiser | Крейсеры / Cruisers | 13 |

Списки вложены: во всех следующих главах сохраняются прежние строительные типы. **Строительная доступность не означает сохранение всех ранее построенных кораблей:** у M7 и M9 Carryover=false, а там, где перенос разрешён, фактический флот зависит от прохождения. DefaultGroups в таком случае — резервный состав.

### Временные ограничения и присутствие вне строительства

- **T1:** Материнский корабль присутствует; перехватчики также выдаются скриптом. Строительная запись только одна.
- **M1:** базовый whitelist — четыре типа. Материнский корабль уже есть и не входит в эти четыре.
- **M7:** строительство отключается после OnSimReady; возвращается после добычи суммарно 2000 RU. Нового корпуса в whitelist нет.
- **M4:** дополнительно выдаются три инженерных корвета. Повреждённый эсминец Радаа — сюжетная цель; его спасение/получение не равно открытию постройки своего эсминца.
- **M5:** верфь / научная станция есть в сцене как `Ship_Hgn_Shipyard`, команда 2. Возможность строить верфи из этого не следует.
- **M6:** в финальной сюжетной цепочке найден `DisableBuildSystem` после `M06_080_070_TS`; восемь типов описывают список главы до этого события.
- **M9:** строительство в начале отключено; возвращается после передачи технологии Бентуси (`M09_020_060_BN` → `SetBuildByBuildList`). Есть также скриптовая выдача штурмового, инженерного и баррикадного кораблей.
- **M10:** три нейтральные добывающие платформы / Mining Platforms присутствуют как объекты сцены. Это не дополнительные строительные типы.
- **M13:** тяжёлый крейсер есть в резервном составе и AdditionalGroups; его наличие возможно до реплики объявления.

В полном наборе whitelist нет строительных команд для носителя, верфи, ресурсного контроллера, ремонтного корвета, лёгкого корвета, минного заградителя, Defender, Cloaked Fighter, Drone Frigate или Research Ship. Поэтому штатный кушанский справочник шире исходного кампанийного строительства. Включение этих проектов в Новокушан потребует отдельного решения.

`Ship_Kus_MobileRefinery` — ресурсный контроллер по принятому уточнению Дмитрия; он не входит в перечисленные 13 строительных типов. `CUT_Ship_Kus_SupportFrigate` и обычный `Ship_Hgn_BarricadeFrigate` (тип 45) остаются разными определениями. Для CUT-варианта роль поля ещё проверяется; слово Support в техническом имени не превращает его в ремонтный корабль.

### Полный конечный список по классам

| Класс RU / EN | Типы, строящиеся к M13, RU / EN |
|---|---|
| Истребители / Fighters | Разведчик / Scout; Перехватчик / Interceptor; Ударный бомбардировщик / Attack Bomber |
| Корветы / Corvettes | Тяжёлый корвет / Heavy Corvette; Многопушечный корвет / Multi-Gun Corvette; Инженерный корвет / Engineer Craft |
| Фрегаты / Frigates | Штурмовой фрегат / Assault Frigate; Баррикадный фрегат / Barricade Frigate; Ионный фрегат / Ion Cannon Frigate |
| Эсминцы / Destroyers | Эсминец / Destroyer; Баллистический эсминец / Ballistic Destroyer |
| Крейсеры / Cruisers | Тяжёлый крейсер / Heavy Cruiser |
| Вспомогательные / Utility | Сборщик ресурсов / Resource Collector |

Слоты постройки VR — отряды: Scout по 3 корпуса, Interceptor/Attack Bomber по 5, Heavy/Multi-Gun Corvette по 3; инженерный корвет, сборщик и крупные корабли по одному. При сравнении цен с HW2 Classic нужно сопоставлять одинаковые единицы заказа.

Steam-демка **1.2.0-25236** — отдельная ревизия: T1, M1 и M4, а также бонус C1. Её M4 имеет шесть строительных типов; C1 — тринадцать, но это не дополнительная глава полной Quest-кампании. См. [DEMO_PROGRESSION.md](../DEMO_PROGRESSION.md). Нынешняя HWRM-мини-кампания T1 → M1 → M4 не подтверждает реализацию полной прогрессии.

## Что обсуждать дальше в этом эпике

Актуальные нерешённые вопросы и схема находятся в [проекте Новокушан v4](NOVOKUSHAN_DESIGN.md). Список ниже — первоначальные направления работы, до принятия актуального состава из 28 проектов.

1. Выбрать отображаемое английское имя, сохранив текущие технические ID.
2. Отметить в кушанском справочнике: оставить / изменить / исключить / добавить из хиигарского флота. Отдельно решить роли Engineer Craft, Barricade Frigate и Ballistic Destroyer.
3. Для выбранного состава составить таблицу HW2 Classic: цена заказа, число корпусов, время, лимит, роль и зависимости. Цены VR и HWRM хранить отдельными колонками источников.
4. Разделить кампанийную доступность и полное дерево расы; решить, какие новые возможности доступны вне кампании, а какие требуют изменения её сценария.

## Проверяемые источники

- [Штатный список кушан HWRM](../../local/hwrm-base/scripts/races/kushan/scripts/def_build.lua), [хиигарян HWRM](../../local/hwrm-base/scripts/races/hiigaran/scripts/def_build.lua), [вэйгров HWRM](../../local/hwrm-base/scripts/races/vaygr/scripts/def_build.lua).
- Определения корпусов: `local/hw1ships/ship/kus_*/*.ship`, `local/hw2ships/ship/hgn_*/*.ship`, `local/hw2ships/ship/vgr_*/*.ship`. Штатные Mothership / Материнский корабль и Vaygr Flagship / флагман добавлены отдельно от def_build.
- Английские имена: [HW1 build/research](../../local/english/hw1buildresearch.dat), [HW2 build/research](../../local/english/buildresearch.dat), [HW1 ships](../../local/english/hw1ships.dat), [HW2 ships](../../local/english/ships.dat). Старые русские таблицы сохранены; рабочая терминология — [глоссарий](../../localization/GLOSSARY.md).
- Для дальнейшего баланса уже извлечён HW2 Classic: `local/hw2classic/ship`, `local/hw2classic/scripts/building and research/hiigaran`. Его Lua-файлы содержат байткод, и численные параметры в этом эпике из них ещё не разобраны.
- [Полная Quest-прогрессия с ID ассетов и узлами графов](../QUEST_PROGRESSION.md); [исходные определения миссий EN/RU](../../local/quest-campaign/missions.json). В эпике используются новые русские названия проекта, а не старые RU-поля missions.json.

Проверка в рамках этого обсуждения: чтение локальных файлов и сверка списков. Игра и лаунчер не запускались, игровые файлы и установленный пакет не изменялись.
