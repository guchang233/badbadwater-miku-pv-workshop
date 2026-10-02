"""Inspect the actual delivery encode, source holds and key transition frames."""
from pathlib import Path
import subprocess,json
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent;OUT=ROOT.parent/'output_hd';SOURCE=ROOT.parent/'upload/175348148-1-208.mp4'
MAIN=OUT/'我的悲伤是水做的_MIKU_高清重制.mp4'
specs=json.load(open(ROOT/'source_specs.json'))
ids=sorted(set([s[3]for s in specs]+[0,85,95,239,240,341,342,489,490,964,965,971,972,1037,1038,1165,1303,1305,1307,1574,1576,1578,1783,1852,1895,1903,2194,2195,2944,2946,2948,3556,3557,3633,3688,4043,4046,4049,4050,4317,4318,4455,4456,5006,5131,5135,5142,5143,5273,5274,5421]))
expression='+'.join(f'eq(n,{i})'for i in ids)
def read(path):
    raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-vf',"select='"+expression+"',scale=960:540",'-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','-'])
    assert len(raw)==len(ids)*960*540*3
    return np.frombuffer(raw,np.uint8).reshape(len(ids),540,960,3)
source=read(SOURCE);new=read(MAIN)
for start in range(0,len(ids),10):
    count=min(10,len(ids)-start);sheet=Image.new('RGB',(1920,290*((count+1)//2)),(22,30,40));draw=ImageDraw.Draw(sheet)
    for k in range(count):
        j=start+k;x=k%2*960;y=k//2*290
        sheet.paste(Image.fromarray(source[j]).resize((480,270)),(x,y));sheet.paste(Image.fromarray(new[j]).resize((480,270)),(x+480,y))
        draw.text((x+5,y+272),f"frame {ids[j]} / {ids[j]/24:.3f}s | HD SOURCE / ENCODED MIKU",fill='white')
    sheet.save(ROOT/'analysis'/f'encoded_review_{start//10:02d}.jpg')
for idx in [1730,2200,3400,4360,4480,5135]:
    j=ids.index(idx);Image.fromarray(new[j]).save(ROOT/'analysis'/f'encoded_focus_{idx}.jpg')
json.dump(dict(encoded_samples=ids,source_frame_alignment='frame index on 24fps grid',inspection='sample sheets and transition boundaries; no real-time player viewing'),open(ROOT/'encoded_review.json','w'),indent=2)
print('encoded review frames',len(ids),flush=True)
