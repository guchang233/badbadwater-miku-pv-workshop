"""Restore exact original media from checked-in chunks; no network required."""
from pathlib import Path
import argparse,hashlib,json,os
ROOT=Path(__file__).resolve().parent

def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

def ensure_media(overwrite=False):
 records=json.loads((ROOT/'media_parts/manifest.json').read_text(encoding='utf-8'))
 for r in records:
  dest=(ROOT/r['target']).resolve()
  if not dest.is_relative_to(ROOT):raise ValueError('Media target outside repository')
  # Existing files may be new renders or deliberate local edits. Preserve them.
  if dest.is_file() and not overwrite:continue
  dest.parent.mkdir(parents=True,exist_ok=True);temp=dest.with_suffix(dest.suffix+'.tmp')
  h=hashlib.sha256();size=0
  with temp.open('wb') as f:
   for part in r['parts']:
    path=(ROOT/part['path']).resolve()
    if not path.is_relative_to(ROOT):raise ValueError('Chunk outside repository')
    data=path.read_bytes()
    if len(data)!=part['bytes'] or hashlib.sha256(data).hexdigest()!=part['sha256']:raise RuntimeError('Missing or damaged media chunk: '+part['path'])
    f.write(data);h.update(data);size+=len(data)
   f.flush();os.fsync(f.fileno())
  if size!=r['bytes'] or h.hexdigest()!=r['sha256']:raise RuntimeError('Original media hash differs: '+r['target'])
  os.replace(temp,dest);print('Restored:',r['target'],flush=True)

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--force',action='store_true',help='Restore the original snapshots even when local media already exists.')
 ensure_media(parser.parse_args().force)
