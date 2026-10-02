"""Decode all final videos and verify frame counts and AAC stream identity."""
from pathlib import Path
import subprocess,json,hashlib
ROOT=Path(__file__).resolve().parent;OUT=ROOT.parent/'output_hd'
paths=[ROOT.parent/'upload/175348148-1-208.mp4',OUT/'我的悲伤是水做的_MIKU_高清重制.mp4',OUT/'我的悲伤是水做的_高清原版与MIKU对照.mp4',OUT/'我的悲伤是水做的_高清转场对照短片.mp4']
results=[];audio_hash=[]
for k,p in enumerate(paths):
    subprocess.run(['ffmpeg','-v','error','-i',str(p),'-f','null','-'],check=True)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_entries','stream=codec_name,codec_type,profile,width,height,pix_fmt,nb_read_frames,duration,start_time,r_frame_rate:format=duration,size','-of','json',str(p)]))
    if k<3:
        video=next(s for s in probe['streams']if s['codec_type']=='video');assert int(video['nb_read_frames'])==5422
        bitstream=subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:a:0','-c:a','copy','-f','adts','-']);audio_hash.append(hashlib.sha256(bitstream).hexdigest())
    results.append(dict(file=p.name,complete_decode='passed',probe=probe,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    print('verified',p.name,flush=True)
assert len(set(audio_hash))==1,'Audio bitstream changed'
report=dict(videos=results,audio_bitstream_sha256=audio_hash,audio_identical=True,real_time_player_review=False)
json.dump(report,open(ROOT/'validation.json','w'),ensure_ascii=False,indent=2)
