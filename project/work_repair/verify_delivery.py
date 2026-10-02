"""Fully decode deliverables and verify original AAC plus actual video frame count."""
from pathlib import Path
import subprocess,json,hashlib
import compose_repair as c
from render_repair import OUTPUT
from build_comparison import COMPARE,FOCUS
ROOT=Path(__file__).resolve().parent
def verify():
    results=[];audio=[]
    for p in [c.SRC,OUTPUT,COMPARE,FOCUS]:
        subprocess.run(['ffmpeg','-v','error','-threads','2','-i',str(p),'-f','null','-'],check=True)
        probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames',
            '-show_entries','stream=codec_name,codec_type,profile,width,height,pix_fmt,nb_read_frames,duration,start_time,r_frame_rate:format=duration,size',
            '-of','json',str(p)]))
        v=next(s for s in probe['streams']if s['codec_type']=='video')
        if p!=FOCUS:
            assert int(v['nb_read_frames'])==5422
            data=subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:a:0','-c:a','copy','-f','adts','-'])
            audio.append(hashlib.sha256(data).hexdigest())
        if p==OUTPUT:assert v['width']==1920 and v['height']==1080 and v['r_frame_rate']=='24/1'
        results.append({'file':p.name,'complete_decode':'passed','probe':probe,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
        print('verified',p.name,flush=True)
    assert len(set(audio))==1,'Original AAC changed'
    report={'videos':results,'audio_bitstream_sha256':audio,'audio_identical':True,
        'real_time_player_review':False,'focus_audio':'original excerpts, AAC re-encoded for edited compilation'}
    (ROOT/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':verify()
