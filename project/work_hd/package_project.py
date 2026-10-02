"""Package only reproducible source/assets, instructions and verified reports."""
from pathlib import Path
import zipfile,os
from PIL import Image
ROOT=Path(__file__).resolve().parent;OUT=ROOT.parent/'output_hd'
path=OUT/'我的悲伤是水做的_MIKU_高清制作工程.zip'
for folder in ['assets','refs']:
    for p in (ROOT/folder).glob('*.png'):
        with Image.open(p)as im:im.load()
with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as z:
    for p in sorted(ROOT.iterdir()):
        if p.is_file()and p.suffix in ['.py','.md','.json']:z.write(p,'work_hd/'+p.name)
    for folder in ['assets','refs']:
        for p in sorted((ROOT/folder).iterdir()):
            if p.is_file():z.write(p,'work_hd/'+folder+'/'+p.name)
    for p in sorted((ROOT/'analysis').iterdir()):
        if p.name=='pts.json' or p.name.startswith('encoded_review_')or p.name.startswith('encoded_focus_'):
            z.write(p,'work_hd/analysis/'+p.name)
    z.write(ROOT.parent/'upload/175348148-1-208.mp4','upload/175348148-1-208.mp4')
with open(path,'rb')as f:os.fsync(f.fileno())
with zipfile.ZipFile(path)as z:
    assert z.testzip()is None
print('valid archive',path,path.stat().st_size,flush=True)
