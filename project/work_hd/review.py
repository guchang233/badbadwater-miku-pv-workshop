from pathlib import Path
import json,sys
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parent
names=sys.argv[1:]
out=Image.new('RGB',(1920,300*len(names)),(20,30,40));d=ImageDraw.Draw(out)
for k,n in enumerate(names):
    job=json.load(open(ROOT/'assets'/f'{n}.json'))
    a=Image.open(ROOT/'refs'/f"frame_{job['idx']:05d}.png").convert('RGB')
    b=Image.open(ROOT/'assets'/f'{n}.png').convert('RGB').resize((1920,1080))
    out.paste(a.resize((480,270)),(0,k*300));out.paste(b.resize((480,270)),(480,k*300))
    ca=a.crop(job['roi']);cb=b.crop(job['roi']);ca.thumbnail((475,270));cb.thumbnail((475,270))
    out.paste(ca,(960,k*300));out.paste(cb,(1440,k*300));d.text((3,k*300+273),n+' SOURCE / NEW | source crop / new crop',fill='white')
out.save(ROOT/'analysis'/'generation_review.jpg')
