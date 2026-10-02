"""Create a verified, reproducible repair package only after all writers finish."""
from pathlib import Path
import json,zipfile,hashlib,os
from PIL import Image
import compose_repair as c
ROOT=Path(__file__).resolve().parent;OLD=ROOT.parent/'work_hd'
PATH=c.OUT/'我的悲伤是水做的_MIKU_高清修复工程.zip'

def package():
    adopted=json.loads((OLD/'delivery_manifest.json').read_text())['assets']
    paths={n:f'work_hd/assets/{n}.png'for n in adopted}
    for n in ['water_float','bowl_head','pier_back_b','pier_back_c']:paths[n]=f'work_repair/assets/{n}.png'
    intervals=[]
    for s in c.SPECS:
        if s[0]=='pier_back':continue
        intervals.append({'name':s[0],'start':s[1],'end':s[2],'source_reference_frame':s[3]})
    intervals+=json.loads((ROOT/'pier_exposures.json').read_text())
    intervals.sort(key=lambda x:x['start'])
    (ROOT/'final_exposures.json').write_text(json.dumps(intervals,ensure_ascii=False,indent=2))
    manifest={'baseline':str(c.BASE.relative_to(ROOT.parent)),'baseline_sha256':hashlib.sha256(c.BASE.read_bytes()).hexdigest(),
        'source':str(c.SRC.relative_to(ROOT.parent)),'source_sha256':hashlib.sha256(c.SRC.read_bytes()).hexdigest(),
        'adopted_unique_cels':len(paths),'new_imagegen_cels':4,'selected_assets':paths,
        'reuse':{'bird_crown':'water_birds'},'repair_ranges':c.RANGES,
        'recomposited_frames':1704,'status':'verified_for_delivery','original_audio_preserved':True,
        'checks':['full decode','frame count','AAC stream identity','encoded stills','paired boundaries','unaffected shot sampling'],
        'real_time_player_review':False}
    (ROOT/'delivery_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    for folder in [OLD/'assets',OLD/'refs',ROOT/'assets',ROOT/'refs',ROOT/'analysis']:
        for p in folder.glob('*.png'):
            with Image.open(p)as im:im.load()
    files=[]
    for p in OLD.iterdir():
        if p.is_file()and p.suffix in ['.py','.md','.json']:files.append(p)
    for folder in [OLD/'assets',OLD/'refs',ROOT/'assets',ROOT/'refs']:
        files.extend(p for p in folder.iterdir()if p.is_file())
    allowed=['README.md','compose_repair.py','render_repair.py','build_comparison.py','review_encoded.py','verify_delivery.py',
        'package_project.py','masks.json','pier_states.json','pier_exposures.json','final_exposures.json',
        'delivery_manifest.json','render_report.json','encoded_review.json','focus_segments.json','validation.json']
    files.extend(ROOT/n for n in allowed)
    files.extend(p for p in (ROOT/'encoded').glob('*.jpg'))
    files.extend(ROOT/'analysis'/n for n in ['pier_transition_sequence.jpg','fishing_fade_source.jpg'])
    files.extend([c.SRC,c.BASE,OLD/'analysis/pts.json'])
    temp=PATH.with_suffix('.zip.part')
    with zipfile.ZipFile(temp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as z:
        for p in sorted(set(files)):z.write(p,str(p.relative_to(ROOT.parent)))
    with open(temp,'rb')as f:os.fsync(f.fileno())
    with zipfile.ZipFile(temp)as z:
        assert z.testzip()is None
        for n in z.namelist():
            if n.endswith('.png'):
                with z.open(n)as f:
                    with Image.open(f)as im:im.load()
    os.replace(temp,PATH)
    print('valid repair archive',PATH,PATH.stat().st_size,flush=True)
if __name__=='__main__':package()
