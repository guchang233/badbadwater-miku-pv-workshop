"""Rebuild the corrected portrait exposure and join it on exact frame cuts."""
import subprocess
import numpy as np
import compose_hd as c

spec=next(s for s in c.OLD_SPECS if s[0]=='water_portrait')
it=c.prepare(spec);start,end=spec[1:3]
patch=c.ROOT/'analysis/portrait_patch.mkv'
dec=subprocess.Popen(['ffmpeg','-v','error','-i',str(c.SRC),'-vf',f'trim=start_frame={start}:end_frame={end}',
    '-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
enc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080',
    '-r','24','-i','-','-c:v','ffv1','-threads','4',str(patch)],stdin=subprocess.PIPE)
for i in range(start,end):
    data=dec.stdout.read(c.W*c.H*3)
    assert len(data)==c.W*c.H*3
    src=np.frombuffer(data,np.uint8).reshape(c.H,c.W,3).astype(np.float32)
    enc.stdin.write(c.composite(i,src,[it]).tobytes())
enc.stdin.close();dec.stdout.close()
assert dec.wait()==0 and enc.wait()==0
from join_patch import join
join(start,end,patch)
