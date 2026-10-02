"""Extract final encoded frames, boundary contact sheets and unchanged-shot checks."""
from pathlib import Path
import subprocess,json
import numpy as np
from PIL import Image,ImageDraw
from render_repair import OUTPUT
import compose_repair as c
ROOT=Path(__file__).resolve().parent;QA=ROOT/'encoded';QA.mkdir(exist_ok=True)
POINTS=[('20s',520,'crouch_back'),('29s',696,'pole_sit'),('39s awake',930,'table_awake'),
    ('39s sleep',990,'table_sleep'),('1m09s',1656,'water_float'),('1m06s fade',1581,'fishing'),
    ('1m23s A',1992,'pier_back'),('1m23s B',2006,'pier_back_b'),('1m23s C',2024,'pier_back_c'),
    ('1m30s',2160,'pier_back_b'),('1m37s',2328,'bowl_head'),('1m47s',2568,'ribbon'),
    ('2m55s',4200,'water_birds'),('ending',5240,'bike_crouch')]
BOUNDARIES=[342,624,762,898,965,1038,1574,1579,1585,1710,1982,2006,2024,2039,2057,2075,2093,2108,2177,
    2266,2405,2544,2678,4184,4318,4456,5006,5131,5143,5274]
UNCHANGED=[250,1200,1470,1730,2180,2470,2740,3000,3400,3550,3720,4480]

def extract(path,ids,folder):
    folder.mkdir(exist_ok=True)
    select='+'.join(f'eq(n,{i})'for i in ids)
    subprocess.run(['ffmpeg','-v','error','-y','-threads','2','-i',str(path),
        '-vf',f"select='{select}'",'-fps_mode','passthrough',str(folder/'%04d.png')],check=True)
    for n,i in enumerate(ids,1):(folder/f'{n:04d}.png').rename(folder/f'f{i:05d}.png')

def image(folder,i):return Image.open(folder/f'f{i:05d}.png').convert('RGB')
def review():
    ids=sorted(set([i for _,i,_ in POINTS]+[j for b in BOUNDARIES for j in [b-1,b]]+UNCHANGED))
    extract(OUTPUT,ids,QA/'repair');extract(c.BASE,sorted(set(i for _,i,_ in POINTS)|set(UNCHANGED)),QA/'before')
    extract(c.SRC,sorted(set(i for _,i,_ in POINTS)),QA/'source')
    for group in range(4):
        rows=POINTS[group*4:group*4+4]
        if not rows:continue
        sheet=Image.new('RGB',(1500,rows.__len__()*385),(25,36,47));d=ImageDraw.Draw(sheet)
        for row,(cue,i,name) in enumerate(rows):
            for col,(label,folder) in enumerate([('SOURCE',QA/'source'),('PREVIOUS',QA/'before'),('REPAIRED',QA/'repair')]):
                im=image(folder,i);sheet.paste(im.resize((500,281)),(col*500,row*385+24))
                d.text((col*500+8,row*385+7),f'{cue} | {label} | frame {i}',fill='white')
            cfg=c.CONF.get(name,{'head':c.old.HEAD.get(name,[0,0,640,360])});a,b,e,f=cfg['head']
            crop=image(QA/'repair',i).crop((int(a*3),int(b*3),int(e*3),int(f*3)))
            crop.thumbnail((490,75));sheet.paste(crop,(1008,row*385+310))
        sheet.save(QA/f'points_{group}.jpg',quality=95)
    for group in range(4):
        bs=BOUNDARIES[group*8:group*8+8]
        if not bs:continue
        sheet=Image.new('RGB',(1400,len(bs)*215),(25,36,47));d=ImageDraw.Draw(sheet)
        for row,b in enumerate(bs):
            for col,i in enumerate([b-1,b]):
                im=image(QA/'repair',i);im.thumbnail((660,185));sheet.paste(im,(col*700,row*215+24))
                d.text((col*700+8,row*215+5),f'BOUNDARY {b} | FRAME {i} | {i/24:.3f}s',fill='white')
        sheet.save(QA/f'boundaries_{group}.jpg',quality=93)
    differences=[]
    for i in UNCHANGED:
        a=np.asarray(image(QA/'before',i),np.float32);b=np.asarray(image(QA/'repair',i),np.float32)
        differences.append({'frame':i,'rgb_mean_absolute_difference':float(np.abs(a-b).mean()),
            'pixels_difference_over_10_fraction':float((np.max(np.abs(a-b),2)>10).mean())})
    report={'point_frames':POINTS,'boundary_frames':BOUNDARIES,'outside_range_checks':differences,
        'method':'encoded frame review and paired boundary stills; not actual realtime player viewing',
        'visual_review_status':'pending'}
    (ROOT/'encoded_review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print('encoded review sheets ready',len(ids),'frames',flush=True)
if __name__=='__main__':review()
