"""Verify this portable repository snapshot, or refresh it after intended edits."""
from pathlib import Path
import argparse,ast,hashlib,json
ROOT=Path(__file__).resolve().parent
EXCLUDED={'manifest.json','docs/REPOSITORY_CHECKS.json'} | {r['target'] for r in json.loads((ROOT/'media_parts/manifest.json').read_text(encoding='utf-8'))}
IGNORED_DIRS={'.git','.venv','venv','__pycache__','.pytest_cache','build','dist'}

def paths():
 return [p for p in sorted(ROOT.rglob('*')) if p.is_file() and not any(s in IGNORED_DIRS for s in p.relative_to(ROOT).parts) and str(p.relative_to(ROOT)).replace('\\','/') not in EXCLUDED and p.suffix not in {'.pyc','.log','.tmp'}]

def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for data in iter(lambda:f.read(1024*1024),b''):h.update(data)
 return h.hexdigest()

def main():
 from prepare_media import ensure_media
 ensure_media()
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--refresh',action='store_true');args=p.parse_args()
 files=paths();manifest=ROOT/'manifest.json'
 if args.refresh:
  manifest.write_text(json.dumps([{'path':str(f.relative_to(ROOT)).replace('\\','/'),'bytes':f.stat().st_size,'sha256':digest(f)} for f in files],ensure_ascii=False,indent=2),encoding='utf-8')
  print('Snapshot refreshed:',len(files),'files');return
 records=json.loads(manifest.read_text(encoding='utf-8'));errors=[]
 for r in records:
  f=ROOT/r['path']
  if not f.is_file():errors.append('missing '+r['path'])
  elif f.stat().st_size!=r['bytes'] or digest(f)!=r['sha256']:errors.append('changed '+r['path'])
 for f in files:
  if f.suffix=='.py':ast.parse(f.read_text(encoding='utf-8'),filename=str(f))
  if f.stat().st_size>100*1024*1024:errors.append('over 100 MiB '+str(f.relative_to(ROOT)))
  if any(s in str(f.relative_to(ROOT)).lower() for s in ['new_mv_project','41945795968','huagu_duo']):errors.append('excluded project '+str(f.relative_to(ROOT)))
 if errors:raise SystemExit('\n'.join(errors))
 print('Verified',len(records),'files; all snapshot hashes and Python syntax passed.')
 print('This checks packaging; use continue_local.py check/verify for the MV workflow.')

if __name__=='__main__':main()
