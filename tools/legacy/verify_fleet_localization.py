"""Verify both real dictionaries and all generated UI references, without HWRM."""

import json
import re

from prepare_fleet_preview import ROOT, REPORT, PROJECT


def dictionary(path):
    pairs = [line.split('\t', 1) for line in path.read_text(encoding='utf-16').splitlines() if '\t' in line]
    data = {key: value for key, value in pairs}
    assert len(data) == len(pairs), (path, "duplicate localization ID")
    return data


def verify():
    manifest = json.loads(REPORT.read_text(encoding='utf8'))
    ru = dictionary(ROOT / 'locale/Russian/vrcampaign.ucs')
    en = dictionary(ROOT / 'locale/English/vrcampaign.ucs')
    assert set(ru) == set(en)
    assert all(not re.search('[А-Яа-яЁё]', value) for value in en.values())
    assert set(manifest['strings']) == set(manifest['strings_en'])
    for key, value in manifest['strings'].items():
        assert ru[key] == value
        assert en[key] == manifest['strings_en'][key] and en[key].strip()
        assert not re.search('[А-Яа-яЁё]', en[key]), (key, en[key])
    refs = set()
    for path in ROOT.rglob('*'):
        if path.suffix in ('.lua', '.campaign', '.level', '.ship'):
            refs.update(re.findall(r'\$(99[56]\d+)', path.read_text(encoding='ascii')))
    assert refs <= ru.keys() and refs <= en.keys(), refs - ru.keys()
    for name in ('Plasma Weapons', 'Improved Plasma Bombs', 'Heavy Destroyer'):
        assert name in en.values(), name
    result = dict(status='passed', languages=['Russian', 'English'], dictionary_keys=len(ru),
                  generated_pairs=len(manifest['strings']), referenced_ids=len(refs),
                  generated_english_without_cyrillic=True, engine_tested=False)
    (PROJECT / 'local/fleet-preview/localization-verification.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__': verify()
