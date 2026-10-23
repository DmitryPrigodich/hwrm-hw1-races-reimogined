"""Build the independent race layer on its pinned HWMP dependency. No game launch."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
PROJECT=Path(__file__).resolve().parents[1]
settings_path=PROJECT/'local/settings.json'
if settings_path.exists():
    os.environ.setdefault('HWRM_ASSET_CACHE',json.loads(settings_path.read_text(encoding='utf8'))['asset_cache'])
PARENT=PROJECT/'dependencies/mp-patch'
sys.path.insert(0,str(PARENT/'tools'))
from hwrm_common import CACHE,index,sha,save,copy_layer,build_directory
from hwrm_inspect import record_config
import hwrm_archive
BUILD=build_directory('hw1-races',PROJECT)
SOURCE=BUILD/'source'
IDENTITY='HWRM-HW1-Races-Reimogined-dev1'

def git_head(path):
    return subprocess.check_output(['git','-C',str(path),'rev-parse','HEAD'],text=True).strip()

def prepare():
    lock=json.loads((PROJECT/'dependencies.lock.json').read_text())
    assert git_head(PARENT)==lock['mp_patch']['commit'],'Update the dependency lock explicitly.'
    subprocess.run([sys.executable,str(PARENT/'tools/hwmp24.py')],check=True)
    base_manifest=json.loads((PARENT/'local/hwmp-patch-2.4/manifest.json').read_text(encoding='utf8'))
    assert base_manifest['fix_revision']==lock['mp_patch']['fix_revision']
    if SOURCE.exists():
        assert SOURCE.resolve().is_relative_to(BUILD.resolve())
        assert (SOURCE/'hw1-races-id.txt').read_text().strip()==IDENTITY
        shutil.rmtree(SOURCE)
    shutil.copytree(Path(base_manifest['source']),SOURCE)
    copy_layer(PROJECT/'data',SOURCE)
    assets=json.loads((PROJECT/'assets.json').read_text(encoding='utf8'))
    for name,row in assets.items():
        origin=CACHE/row['cache_relative_path']
        assert origin.is_file() and sha(origin)==row['sha256'],('Missing/changed local asset',name,str(origin))
        target=SOURCE/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(origin,target)
    (SOURCE/'hw1-races-id.txt').write_text(IDENTITY+'\n',encoding='ascii')
    files={n:sha(p) for n,p in index(SOURCE).items()}
    report={'identity':IDENTITY,'source':str(SOURCE),'mp_patch_commit':lock['mp_patch']['commit'],'fix_revision':base_manifest['fix_revision'],'files':files,'engine_tested':False,'installed':False}
    save(PROJECT/'local/source.json',report)
    verify();return SOURCE

def verify():
    report=json.loads((PROJECT/'local/source.json').read_text(encoding='utf8'))
    files=index(SOURCE);assert report['files']=={n:sha(p) for n,p in files.items()}
    contracts=json.loads((PROJECT/'design/ship-contracts.json').read_text(encoding='utf8'))
    for name,expected in contracts.items():
        actual,_=record_config(files[name].read_text(encoding='ascii'))
        for field,value in expected.items():assert actual.get(field)==value,(name,field,actual.get(field),value)
    fixes=json.loads((PARENT/'hwmp-patch-2.4/fixes.json').read_text(encoding='utf8'))
    for name,value in fixes['overrides'].items():assert sha(files[name])==value,('Shared fix shadowed',name)
    assert not any('vastreachesminicampaign' in n or n.startswith(('sound/','ui/speechicons/')) for n in index(PROJECT/'data'))
    from lupa.lua51 import LuaRuntime
    vm=LuaRuntime();vm.execute((SOURCE/'scripts/races/kushan/scripts/def_research.lua').read_text(encoding='ascii'))
    paid=sum(1 for _,row in vm.globals().research.items() if row.Cost>0)
    automatic=sum(1 for _,row in vm.globals().research.items() if row.Cost==0 and row.Time==0)
    assert (paid,automatic)==(57,71)
    result={'status':'passed','files':len(files),'protected_ships':len(contracts),'paid_research':paid,'automatic_effects':automatic,'shared_fix_revision':report['fix_revision'],'no_campaign_story_or_audio':True,'engine_tested':False,'installed':False}
    save(PROJECT/'local/verification.json',result);print(json.dumps(result));return result

def package():
    source=prepare();release=PROJECT/'local/HWRMHW1Races-release'
    result=hwrm_archive.package_source(source,release,'HWRMHW1Races.big','HW1 Races Reimogined')
    shutil.copy2(PROJECT/'README.md',release/'README.md')
    (release/'config.txt').write_text('Title: HW1 Races Reimogined\nGameType: HomeworldRM\nModType: MOD\nBigFilename: HWRMHW1Races.big\n',encoding='ascii')
    save(PROJECT/'local/release.json',result);print(json.dumps(result));return result

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--package',action='store_true');p.add_argument('--verify',action='store_true');args=p.parse_args()
    if args.package:package()
    elif args.verify:verify()
    else:prepare()
