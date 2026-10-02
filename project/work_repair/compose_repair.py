"""Source-derived layer repairs. Artwork comes from adopted imagegen cels.
Polygon masks specify ownership; they neither draw nor recolour character art.
Source water is a separate foreground layer, and source exposure choices are measured from the original cels.
"""
from pathlib import Path
import sys,json,subprocess,hashlib
import numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage as ndi,signal
ROOT=Path(__file__).resolve().parent
sys.path.append(str(ROOT.parent/'work_hd'))
import compose_hd as old
W,H=1920,1080
SRC=old.SRC;BASE=ROOT.parent/'output_hd/我的悲伤是水做的_MIKU_高清重制.mp4'
OUT=ROOT.parent/'output_repair';OUT.mkdir(exist_ok=True)
CONF=json.loads((ROOT/'masks.json').read_text())
SPECS=[s.copy()for s in old.OLD_SPECS]
for s in SPECS:
 if s[0]=='pier_back':s[1]=1982
 if s[0]=='fishing':s[2]=1585
RANGES=[(342,762),(898,1038),(1574,1710),(1982,2177),(2266,2405),(2544,2678),(4184,4456),(5006,5274)]

def load_frame(i):
 p=ROOT/'refs'/f'source_{i:05d}.png'
 if not p.exists():p=old.ROOT/'refs'/f'frame_{i:05d}.png'
 return np.asarray(Image.open(p).convert('RGB'),np.float32)

def polygon(points):
 im=Image.new('1',(W,H));ImageDraw.Draw(im).polygon([(round(x*3),round(y*3))for x,y in points],fill=1)
 return np.asarray(im,bool)

PIER_STATES=json.loads((ROOT/'pier_states.json').read_text())


def prepare(spec):
 name,start,end,idx,*rest=spec
 n='water_birds'if name=='bird_crown'else name
 cfg=CONF[n];ref=load_frame(4240 if name=='bird_crown'else idx)
 asset=ROOT/'assets'/f'{n}.png'
 if not asset.exists():asset=old.ROOT/'assets'/f'{n}.png'
 gen=np.asarray(Image.open(asset).convert('RGB').resize((W,H),Image.Resampling.LANCZOS),np.float32)
 head=old.rect_mask(cfg['head']);hair=np.zeros((H,W),bool)
 for p in cfg['tails']:hair|=polygon(p)
 keep=head|hair
 r,g,b=np.moveaxis(gen,-1,0)
 # Grow semantic hair ownership to the actual generated teal silhouette,
 # so hand-authored polygons cannot cut a filled strand at a rectangle edge.
 colour=(g-r>19)&(b-r>9)&(b-g<14)&(r<212)&(g<241)
 hair|=colour&ndi.binary_dilation(keep,iterations=70)
 keep=head|hair
 mask=ndi.binary_dilation(keep,iterations=6)
 bg=old.bg_field(ref,mask)
 if n in ('anchor_crouch','crouch_back','table_awake','table_sleep','ribbon','bike_sit','bike_crouch') or n.startswith('pier_back'):
  # These shots have a uniform paper field. Anti-aliased garment or
  # bicycle strokes are not valid background samples.
  bg[:]=np.median(ref[100:280,700:1800],axis=(0,1))
 if n=='water_birds':
  line=np.interp(np.arange(W),[0,1100,1500,1919],[743,705,678,651])
  bg[:]=np.median(ref[90:220,700:1100],axis=(0,1))
  wet_bg=np.arange(H)[:,None]>line[None,:]
  bg[wet_bg]=np.median(ref[830:940,0:100],axis=(0,1))
 if n=='pole_sit':
  line=np.interp(np.arange(W),[0,1050,1350,1919],[710,816,829,797])
  bg[:]=np.median(ref[90:250,1300:1700],axis=(0,1))
  wet_bg=np.arange(H)[:,None]>line[None,:]
  bg[wet_bg]=np.median(ref[900:970,1660:1720],axis=(0,1))
 sample=np.median(gen[0:70,1780:1880],axis=(0,1));r,g,b=np.moveaxis(gen,-1,0)
 # Background-relative colour discrimination, with a narrow tolerance.
 # Muted teal is retained even where it approaches the paper colour.
 blank=(r>150)&(r<241)&(abs((g-r)-(sample[1]-sample[0]))<5)&(abs((b-g)-(sample[2]-sample[1]))<4)
 patch=gen.copy();patch[blank]=bg[blank]
 # Added tails do not own nearby source sleeves, props or background.
 preserve_blank=blank&~head
 patch[preserve_blank]=ref[preserve_blank]
 if n=='bowl_head':
  bubble=polygon(cfg['keep'][0]);patch[bubble]=gen[bubble]
  # Original opaque white hair above the waterline is now teal. The
  # submerged part gets the source water layer; the crown stays exposed.
  line=np.interp(np.arange(W),np.array([60,100,135,175,210])*3,np.array([110,116,128,132,131])*3)
  wet=bubble&(np.arange(H)[:,None]>line[None,:])
  water=np.median(ref[210*3:232*3,174*3:188*3],axis=(0,1))
  patch[wet]=.53*water+.47*patch[wet]
 # Table hair passes behind the cups. Only actual cup silhouettes, not
 # bounding boxes, retain the source; hair stays continuous beside them.
 protected=np.zeros((H,W),bool)
 for p in cfg.get('cups',[]):protected|=polygon(p)
 if n.startswith('table_'):
  mask[302*3:]=False
  # Restore the original tabletop stroke only where it crosses hair.
  region=old.rect_mask((290,284,640,300));ink=region&(ref[:,:,0]<145)&(ref[:,:,1]<183)
  # Cut out arms/head, whose navy strokes belong to the identity drawing.
  ink&=~old.rect_mask((384,175,560,302));protected|=ndi.binary_dilation(ink,iterations=1)
 if n=='pole_sit':
  # Preserve street pole foreground. The tail itself has the same complete
  # water layer below the authored curved surface.
  protected|=old.rect_mask((404,305,420,340))&(ref[:,:,0]<145)&(ref[:,:,1]<183)
  curve=np.interp(np.arange(W),[0,1050,1350,1919],[710,816,829,797])
  wet=hair&(np.arange(H)[:,None]>curve[None,:])
  water=np.median(ref[900:970,1660:1720],axis=(0,1))
  patch[wet]=.36*water+.64*patch[wet]
 if n=='water_birds':
  # Keep the regenerated collar as one coherent drawing, with original
  # dynamic birds restored later. The lower tail is submerged with body.
  water=np.median(ref[830:940,0:100],axis=(0,1))
  line=np.interp(np.arange(W),[0,1100,1500,1919],[743,705,678,651])
  wet=hair&(np.arange(H)[:,None]>line[None,:])
  patch[wet]=.34*water+.66*patch[wet]
 delta=np.zeros_like(ref);delta[mask]=patch[mask]-ref[mask];delta[protected]=0
 if n.startswith('pier_back'):
  # The source rail remains foreground across the added tails.
  delta[old.rect_mask((410,247,640,261))]=0
 ys,xs=np.nonzero(mask);box=(int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1))
 a,b,c,d=box
 # Full reference is only needed for authored dissolve estimation.
 return dict(name=name,start=start,end=end,idx=idx,box=box,delta=delta[b:d,a:c].copy(),head=head,old=head,ref=ref,
             ink=head&(ref[:,:,0]<140)&(ref[:,:,1]<180),asset=str(asset.relative_to(ROOT.parent)))

def opacity(it,src,dx=0,dy=0):
 if not it['name'].startswith('pier_back'):return 1.
 yy,xx=np.nonzero(it['ink']);yy2=yy+dy;xx2=xx+dx
 ok=(yy2>=0)&(yy2<H)&(xx2>=0)&(xx2<W)
 rr=it['ref'][yy[ok],xx[ok]]-255;ss=src[yy2[ok],xx2[ok]]-255
 return float(np.clip(np.sum(rr*ss)/max(float(np.sum(rr*rr)),1),0,1))

def over(result,src,it,i):
 n=it['name']
 # Foreground birds are isolated from thin old character lines.
 if n in ('anchor_crouch','water_birds','bird_crown','bike_sit','bike_crouch'):
  region=old.rect_mask((310,0,640,245)if n in ('water_birds','bird_crown')else(0,275,640,360))
  ink=(src[:,:,0]<125)&(src[:,:,1]<170)&region
  ink=ndi.binary_opening(ink,structure=np.ones((5,5)))
  ink=ndi.binary_dilation(ink,iterations=3)&region
  if n=='water_birds':ink&=~ndi.binary_dilation(it['head'],iterations=3)
  result[ink]=src[ink]
 if n.startswith('pier_back'):
  region=old.rect_mask((569,214,640,326))
  birds=region&(src[:,:,0]<145)&(src[:,:,1]<185)
  birds=ndi.binary_dilation(birds,iterations=2)&region
  result[birds]=src[birds]
 # Creator mark is a source layer, even when tails extend close to it.
 logo=old.rect_mask((572,293,640,360))&(src.min(2)>232);result[logo]=src[logo]
 return result

def composite(i,src,items):
 active=[it for it in items if it['start']<=i<it['end'] and (not it['name'].startswith('pier_back') or PIER_STATES.get(str(i))==it['name'])]
 if not active:return src.astype(np.uint8)
 result=src.copy();weights=[]
 for it in active:
  dx,dy=0,0
  weights.append(opacity(it,src,dx,dy)if it['name']in CONF else old.source_opacity(it,src))
 if len(active)==2:
  a,b=active;m=a['old']|b['old']
  if a['name']=='bike_sit':m[280*3:]=False
  contrast=b['ref'][m]-a['ref'][m];sample=src[m]-a['ref'][m]
  w=float(np.clip(np.sum(contrast*sample)/max(float(np.sum(contrast*contrast)),1),0,1));weights=[1-w,w]
 for it,w in zip(active,weights):
  a,b,c,d=it['box'];dx,dy=0,0
  aa,bb,cc,dd=a+dx,b+dy,c+dx,d+dy
  l,t,r,bot=max(aa,0),max(bb,0),min(cc,W),min(dd,H)
  if l<r and t<bot:result[t:bot,l:r]+=w*it['delta'][t-bb:bot-bb,l-aa:r-aa]
 np.clip(result,0,255,out=result)
 for it in active:
  if it['name']in CONF:over(result,src,it,i)
  else:old.overlays(result,src,it,i)
 return result.astype(np.uint8)

def items():
 selected=[prepare(s)for s in SPECS if s[0]in CONF]
 selected.append(old.prepare(next(s for s in SPECS if s[0]=='fishing')))
 for n,idx in [('pier_back_b',2006),('pier_back_c',2024)]:selected.append(prepare([n,1982,2177,idx]))
 return selected

if __name__=='__main__':
 its=items()
 for it in its:
  if it['name']not in CONF:continue
  i=it['idx'];src=load_frame(i);Image.fromarray(composite(i,src,its)).save(ROOT/'analysis'/f"after_{it['name']}.png")
 for i in [1992,2000,2006,2140,2176]:Image.fromarray(composite(i,load_frame(i),its)).save(ROOT/'analysis'/f'after_pier_{i}.png')
 print('repair stills ready',flush=True)
