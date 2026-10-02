"""Render bounded-memory repairs over the accepted HD baseline, copy source AAC."""
from pathlib import Path
import subprocess,json,time
import numpy as np
import compose_repair as c

ROOT=Path(__file__).resolve().parent
OUTPUT=c.OUT/'我的悲伤是水做的_MIKU_高清修正版.mp4'
FRAME_BYTES=c.W*c.H*3

def decoder(path):
    return subprocess.Popen(['ffmpeg','-v','error','-threads','2','-i',str(path),
        '-map','0:v:0','-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)

def frame(pipe):
    b=bytearray()
    while len(b)<FRAME_BYTES:
        p=pipe.read(FRAME_BYTES-len(b))
        if not p:break
        b.extend(p)
    if not b:return None
    assert len(b)==FRAME_BYTES,'Incomplete decoded frame'
    return np.frombuffer(b,dtype=np.uint8).reshape(c.H,c.W,3)

def render():
    its=c.items();source=decoder(c.SRC);baseline=decoder(c.BASE)
    enc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24',
        '-video_size','1920x1080','-framerate','24','-i','-', '-i',str(c.SRC),
        '-map','0:v:0','-map','1:a:0','-c:v','libx264','-threads','4','-preset','medium',
        '-crf','16','-profile:v','high','-pix_fmt','yuv420p','-c:a','copy',
        '-movflags','+faststart',str(OUTPUT)],stdin=subprocess.PIPE)
    t=time.time();changed=0;count=0
    try:
        for i in range(5422):
            src=frame(source.stdout);base=frame(baseline.stdout)
            assert src is not None and base is not None,f'Missing frame {i}'
            if any(a<=i<b for a,b in c.RANGES):
                result=c.composite(i,src.astype(np.float32),its);changed+=1
            else:result=base
            enc.stdin.write(result.tobytes());count+=1
            if i%480==0:print(f'frame {i}/5422; {time.time()-t:.1f}s',flush=True)
        assert frame(source.stdout) is None and frame(baseline.stdout) is None
        enc.stdin.close()
        assert source.wait()==0 and baseline.wait()==0 and enc.wait()==0
    finally:
        for p in [source,baseline,enc]:
            if p.poll() is None:p.terminate()
    report={'frames':count,'recomposited_frames':changed,'ranges':c.RANGES,
        'baseline':str(c.BASE),'output':str(OUTPUT),'seconds':time.time()-t,
        'audio':'original AAC stream copied','outside_ranges':'accepted baseline, then H.264 re-encoded'}
    (ROOT/'render_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print('render complete',OUTPUT,flush=True)

if __name__=='__main__':render()
