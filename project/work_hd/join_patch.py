"""Join a corrected exposure with bounded-memory frame streaming."""
import subprocess
import compose_hd as c

def join(start,end,patch):
    main=c.OUT/'我的悲伤是水做的_MIKU_高清重制.mp4'
    final=c.OUT/'portrait_corrected.mp4'
    def decoder(p):
        return subprocess.Popen(['ffmpeg','-v','error','-threads','2','-i',str(p),
            '-map','0:v:0','-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
    base=decoder(main);replacement=decoder(patch)
    enc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080',
        '-r','24','-i','-','-i',str(main),'-map','0:v:0','-map','1:a:0','-c:v','libx264',
        '-threads','4','-preset','medium','-crf','16','-profile:v','high','-pix_fmt','yuv420p',
        '-c:a','copy','-movflags','+faststart',str(final)],stdin=subprocess.PIPE)
    size=c.W*c.H*3
    for i in range(5422):
        data=base.stdout.read(size);assert len(data)==size
        if start<=i<end:
            data=replacement.stdout.read(size);assert len(data)==size
        enc.stdin.write(data)
        if i%960==0:print('join',i,'of 5422',flush=True)
    assert not base.stdout.read(1) and not replacement.stdout.read(1)
    enc.stdin.close();base.stdout.close();replacement.stdout.close()
    assert base.wait()==0 and replacement.wait()==0 and enc.wait()==0
    main.rename(c.ROOT/'analysis/first_pass.mp4');final.rename(main)
    print('portrait corrected',start,end,flush=True)

if __name__=='__main__':join(1710,1920,c.ROOT/'analysis/portrait_patch.mkv')
