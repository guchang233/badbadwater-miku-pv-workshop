"""HD identity replacement, driven by the original PV exposures.

Generated face/hair are composited onto source clothing, hands, props and
environment. No character drawing, morphing or nonuniform deformation here.
All coordinates below use the original 640x360 layout and scale uniformly
to 1920x1080. Only source-authored fades change the layer opacity.
"""
from pathlib import Path
import json,sys,subprocess,hashlib
import numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage as ndi
ROOT=Path(__file__).resolve().parent
OLD_SPECS=json.load(open(ROOT/'source_specs.json'))
SRC=ROOT.parent/'upload/175348148-1-208.mp4'
OUT=ROOT.parent/'output_hd';OUT.mkdir(exist_ok=True)
W,H=1920,1080
HEAD={
 'stand_back':(100,0,183,81),'stand_threequarter':(100,0,185,83),
 'anchor_crouch':(136,194,201,267),'crouch_back':(95,193,176,257),
 'pole_sit':(435,203,501,266),'pole_stand':(142,119,201,182),
 'table_awake':(380,177,543,290),'table_sleep':(380,177,543,290),
 'sofa_sit':(340,116,412,195),'sofa_lie':(350,223,424,305),
 'fishing':(520,46,582,107),'water_float':(74,213,134,264),
 'water_portrait':(170,0,444,240),'pier_back':(454,73,546,161),
 'wind_profile':(29,170,118,255),'wind_front':(29,169,120,258),
 'bowl_head':(40,72,235,282),'bicycle':(449,0,559,145),
 'ribbon':(87,93,188,219),'tank':(256,4,404,158),
 'window_back':(103,144,175,220),'bed_sleep':(409,206,484,280),
 'hood_side':(480,47,606,212),'hood_ball':(245,10,387,182),
 'hug_knees':(229,108,392,242),'hug_knees_closed':(229,108,392,242),
 'trumpet_crouch':(215,174,296,250),'trumpet_sit':(214,168,298,249),
 'water_birds':(384,75,515,200),'bird_crown':(384,75,515,200),
 'bowl_hold':(39,102,186,255),'bike_sit':(41,150,137,250),
 'bike_crouch':(47,148,146,253),
}
ROI_OVERRIDES={'water_portrait':(20,0,610,360),'wind_profile':(0,155,210,360),
 'wind_front':(0,155,215,360),'ribbon':(15,70,325,360),
 'tank':(165,0,480,310),'sofa_lie':(315,100,640,360)}

def rect_mask(box):
    m=np.zeros((H,W),bool);a,b,c,d=[v*3 for v in box];m[b:d,a:c]=True;return m

def frame(i):
    return np.asarray(Image.open(ROOT/'refs'/f'frame_{i:05d}.png').convert('RGB'),np.float32)

def connected_mask(seed,minimum=20):
    lab,n=ndi.label(seed);counts=np.bincount(lab.ravel());good=counts>=minimum;good[0]=False
    return good[lab]

def bg_field(ref,exclude):
    r,g,b=np.moveaxis(ref,-1,0)
    blank=(r>155)&(r<239)&(g-r<27)&(np.abs(b-g)<24)&~exclude
    inds=ndi.distance_transform_edt(~blank,return_distances=False,return_indices=True)
    return ref[inds[0],inds[1]]

def prepare(spec):
    name,start,end,idx,roi,*alias=spec
    file_name='water_birds' if name=='bird_crown' else name
    ref=frame(4240 if name=='bird_crown' else idx)
    gen=np.asarray(Image.open(ROOT/'assets'/f'{file_name}.png').convert('RGB').resize((W,H),Image.Resampling.LANCZOS),np.float32)
    allowed=rect_mask(ROI_OVERRIDES.get(name,roi));head=rect_mask(HEAD[name])
    head=ndi.binary_dilation(head,iterations=2)&allowed
    gr,gg,gb=np.moveaxis(gen,-1,0);rr,rg,rb=np.moveaxis(ref,-1,0)
    teal=connected_mask((gg-gr>23)&(gb-gr>13)&(gr<210)&(gg<241)&allowed,minimum=26)
    # Only filled hair and the face/head may use generated content. Source
    # arms, hands, garments, boots and all thin scenery stay in the source.
    gen_backdrop=np.median(gen[0:65,1780:1870],axis=(0,1))
    gen_hair=np.median(gen[teal],axis=0)
    distance_bg=np.sum((gen-gen_backdrop)**2,axis=2)
    distance_hair=np.sum((gen-gen_hair)**2,axis=2)
    teal&=distance_hair<distance_bg
    gen_blank=(gr>153)&(gr<238)&(((gg-gr<26)&(np.abs(gb-gg)<22))|(distance_bg<distance_hair))
    ref_blank=(rr>153)&(rr<239)&(rg-rr<27)&(np.abs(rb-rg)<22)
    new_head=connected_mask(head&~gen_blank,minimum=20)
    old_head=connected_mask(head&~ref_blank,minimum=20)
    new_head=ndi.binary_fill_holes(ndi.binary_closing(new_head,iterations=2))&head
    old_head=ndi.binary_fill_holes(ndi.binary_closing(old_head,iterations=2))&head
    new=ndi.binary_dilation(new_head|teal,iterations=7)&allowed
    old=ndi.binary_dilation(old_head,iterations=7)&head
    # The transparent fishbowl head includes source-coloured face/glass fill.
    if name in ('bowl_head','water_portrait','wind_front','water_birds','bird_crown','water_float'):
        old=head.copy();new=head|ndi.binary_dilation(teal,iterations=7)
    union=old|new
    bg=bg_field(ref,head|teal)
    if name=='water_portrait':
        bg[:]=np.median(ref[0:75,1760:1850],axis=(0,1))
    if name in ('water_birds','bird_crown'):
        bg[:210*3]=np.median(ref[0:75,0:100],axis=(0,1))
    patch=bg.copy();patch[new]=gen[new]
    patch[new&gen_blank]=bg[new&gen_blank]
    clean_ref=ref;lyric_masks=None
    if name=='water_portrait':
        # The source cel carries the first lyric. Subtracting those strokes
        # from a later lyric would create bright inverted text. Use the
        # circle-covered source frame to isolate that foreground text.
        text_ref=frame(1783);text_later=frame(1852)
        band=rect_mask((190,192,445,216))
        center=rect_mask((263,198,371,213))
        first=band&(text_ref[:,:,0]<155)&(text_ref[:,:,1]<185)
        first&=(np.max(np.abs(text_ref-text_later),axis=2)>12)|center
        second=center&(text_later[:,:,0]<155)&(text_later[:,:,1]<185)
        lyric_masks=(first,second)
        glyph=first&(rr<155)&(rg<185)
        glyph=ndi.binary_dilation(glyph,iterations=2)
        nearest=ndi.distance_transform_edt(glyph,return_distances=False,return_indices=True)
        clean_ref=ref.copy();clean_ref[glyph]=ref[nearest[0][glyph],nearest[1][glyph]]
    delta=np.zeros_like(ref);delta[union]=patch[union]-clean_ref[union]
    # Source glyphs and props are independent of the regenerated identity.
    if name.startswith('table_'):
        delta[290*3:]=0
        # Cups in front of the face/tails retain the source raster and fill.
        for box in ((348,270,389,329),(422,306,458,356),(471,292,499,339),(579,269,612,332),(602,298,634,350)):
            delta[rect_mask(box)]=0
    if name=='sofa_lie':delta[100*3:177*3,365*3:439*3]=0
    if name=='bowl_hold':
        # Preserve raised supporting hand and outer bowl edge at screen right.
        delta[126*3:266*3,248*3:278*3]=0
    ink=old_head&(rr<140)&(rg<180)
    if ink.sum()<60:ink=old_head
    a=ref[ink]-bg[ink];den=float(np.sum(a*a))
    ys,xs=np.nonzero(union);box=(int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1))
    a0,b0,c0,d0=box
    return dict(name=name,start=start,end=end,idx=idx,box=box,
        delta=delta[b0:d0,a0:c0].copy(),ref=ref,head=head,old=old,
        ink=ink,bg=bg,opacity_a=a,opacity_den=den,lyric_masks=lyric_masks)

def source_opacity(it,src):
    if it['name'] in ('water_portrait','bird_crown'):return 1.0
    # Small global background changes are independent of the source cel fade.
    rb=np.median(it['ref'][0:70,1815:1890],axis=(0,1));sb=np.median(src[0:70,1815:1890],axis=(0,1))
    b=src[it['ink']]-it['bg'][it['ink']]-(sb-rb)
    return float(np.clip(np.sum(it['opacity_a']*b)/max(it['opacity_den'],1),0,1))

def overlays(result,src,it,i):
    n=it['name']
    if n=='water_portrait':
        # Original lyric strokes plus the author's opaque white flash/wipe.
        first,second=it['lyric_masks'];dark=(src[:,:,0]<155)&(src[:,:,1]<185)
        unique=[first&~second,second&~first]
        scores=[float((dark&m).sum())/max(int(m.sum()),1)for m in unique]
        text=(first if scores[0]>=scores[1]else second)&dark;result[text]=src[text]
        if i>=1783:
            # The main opaque circle is a held source effect. Exclude
            # unchanged old white hair from the effect matte, then include
            # the exact central disk and newly appearing peripheral circles.
            yy,xx=np.ogrid[:H,:W]
            disk=(xx-911)**2+(yy-373)**2<=287**2
            white=(src.min(2)>235)
            white&=~(it['head']&(yy<640)&(it['ref'].min(2)>235))|disk
            result[white]=src[white]
    if n=='hood_ball':
        for box in ((174,215,241,237),(392,215,457,237)):
            mask=rect_mask(box)&(src[:,:,0]<158)&(src[:,:,1]<186);result[mask]=src[mask]
    if n in ('anchor_crouch','trumpet_sit','water_birds','bird_crown','bike_crouch','bike_sit'):
        if n in ('water_birds','bird_crown'):
            region=rect_mask((310,0,640,245))
            # Flock is foreground; only restore coherent filled pigeon shapes.
            navy=(src[:,:,0]<125)&(src[:,:,1]<170)&region
            navy=ndi.binary_opening(navy,structure=np.ones((5,5)))
            navy=ndi.binary_dilation(navy,iterations=4)&region
            if n=='water_birds':navy&=~ndi.binary_dilation(it['old'],iterations=3)
        else:
            region=rect_mask((0,275,640,360))
            navy=(src[:,:,0]<110)&(src[:,:,1]<160)&region
            navy=ndi.binary_opening(navy,structure=np.ones((6,6)))
            navy=ndi.binary_dilation(navy,iterations=3)&region
        result[navy]=src[navy]
    # Moving pale fish over the standing girl's legs are always source layers.
    if n=='pole_stand':
        region=rect_mask((0,250,260,360));fish=(src.min(2)>219)&(src.max(2)-src.min(2)<35)&region
        result[fish]=src[fish]
    mark=rect_mask((572,293,640,360))&(src.min(2)>232);result[mark]=src[mark]
    return result

def composite(i,src,items):
    active=[it for it in items if it['start']<=i<it['end']]
    if not active:return src.astype(np.uint8)
    result=src.copy();weights=[source_opacity(it,src) for it in active]
    if len(active)==2:
        a,b=active;mask=a['old']|b['old']
        if a['name'] in ('trumpet_crouch','bike_sit'):mask[280*3:]=False
        contrast=b['ref'][mask]-a['ref'][mask];sample=src[mask]-a['ref'][mask]
        den=float(np.sum(contrast*contrast));w=float(np.clip(np.sum(contrast*sample)/max(den,1),0,1));weights=[1-w,w]
    for it,weight in zip(active,weights):
        a,b,c,d=it['box'];result[b:d,a:c]+=weight*it['delta']
    np.clip(result,0,255,out=result)
    for it in active:overlays(result,src,it,i)
    return result.astype(np.uint8)

def review(items):
    for start in range(0,len(items),6):
        batch=items[start:start+6];out=Image.new('RGB',(1920,290*len(batch)),(22,30,40));d=ImageDraw.Draw(out)
        for k,it in enumerate(batch):
            idx=it['idx'];src=frame(idx);gen=composite(idx,src,[it])
            out.paste(Image.fromarray(src.astype(np.uint8)).resize((480,270)),(0,k*290));out.paste(Image.fromarray(gen).resize((480,270)),(480,k*290))
            box=[v*3 for v in HEAD[it['name']]]
            a=Image.fromarray(src.astype(np.uint8)).crop(box);b=Image.fromarray(gen).crop(box);a.thumbnail((470,270));b.thumbnail((470,270));out.paste(a,(960,k*290));out.paste(b,(1440,k*290))
            d.text((5,k*290+272),it['name']+' SOURCE / COMPOSITE / head detail',fill='white')
            Image.fromarray(gen).save(ROOT/'analysis'/f"composite_{it['name']}.png")
        out.save(ROOT/'analysis'/f'composite_review_{start//6}.jpg')
    print('review',len(items),flush=True)

def render(items):
    path=OUT/'我的悲伤是水做的_MIKU_高清重制.mp4'
    decoder=subprocess.Popen(['ffmpeg','-v','error','-i',str(SRC),'-map','0:v:0','-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
    encoder=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','24','-i','-','-i',str(SRC),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-threads','4','-preset','medium','-crf','16','-profile:v','high','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(path)],stdin=subprocess.PIPE)
    count=0;size=W*H*3
    while True:
        data=decoder.stdout.read(size)
        if not data:break
        if len(data)!=size:raise RuntimeError('truncated source frame')
        src=np.frombuffer(data,np.uint8).reshape(H,W,3).astype(np.float32)
        result=composite(count,src,items);encoder.stdin.write(result.tobytes());count+=1
        if count%240==0:print('render',count,'of 5422',flush=True)
    encoder.stdin.close();decoder.stdout.close()
    if decoder.wait()!=0 or encoder.wait()!=0 or count!=5422:raise RuntimeError(f'encode failure or frame mismatch: {count}')
    print(str(path),flush=True)

if __name__=='__main__':
    items=[prepare(s) for s in OLD_SPECS]
    pts=json.load(open(ROOT/'analysis/pts.json'))
    json.dump(dict(version=2,source=str(SRC),source_sha256=hashlib.sha256(SRC.read_bytes()).hexdigest(),resolution=[W,H],source_frames=5422,fps='24/1',mode='strict_source',maximum_pts_grid_error_seconds=max(abs(float(p['best_effort_timestamp_time'])-i/24)for i,p in enumerate(pts)),identity_cels=32,source_clothing_hands_props_preserved=True,source_exposures=[dict(name=s[0],start=s[1],end=s[2],idx=s[3])for s in OLD_SPECS],output_exposures=[dict(name=s[0],start=s[1],end=s[2],asset='water_birds' if s[0]=='bird_crown' else s[0])for s in OLD_SPECS]),open(ROOT/'timeline.json','w'),ensure_ascii=False,indent=2)
    if '--render' in sys.argv:render(items)
    else:review(items)
