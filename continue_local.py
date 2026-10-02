"""Run the original project workflow from a stable working directory."""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT / 'project'
ACTIONS = {'render': 'render_repair.py', 'compare': 'build_comparison.py',
           'review': 'review_encoded.py', 'verify': 'verify_delivery.py'}


def check():
    for executable in ['ffmpeg', 'ffprobe']:
        if not shutil.which(executable):
            raise RuntimeError(f'{executable} is missing from PATH')
    import numpy
    import scipy
    import PIL
    print('Python', sys.version.split()[0], 'numpy', numpy.__version__,
          'scipy', scipy.__version__, 'Pillow', PIL.__version__)
    for script in list((PROJECT / 'work_hd').glob('*.py')) + list((PROJECT / 'work_repair').glob('*.py')):
        ast.parse(script.read_text(encoding='utf-8'), filename=str(script))
    manifest = json.loads((PROJECT / 'work_repair/delivery_manifest.json').read_text(encoding='utf-8'))
    for relative in list(manifest['selected_assets'].values()) + [manifest['source'], manifest['baseline']]:
        path = PROJECT / relative
        if not path.is_file():
            raise FileNotFoundError(path)
    if not (PROJECT / 'local_support/DejaVuSans.ttf').is_file():
        raise FileNotFoundError('Bundled comparison font')
    probe = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height,r_frame_rate', '-of', 'json',
        str(PROJECT / manifest['source'])]))
    video = probe['streams'][0]
    if (video['width'], video['height'], video['r_frame_rate']) != (1920, 1080, '24/1'):
        raise RuntimeError(f'Unexpected source: {video}')
    for key in ['source', 'baseline']:
        with open(PROJECT / manifest[key], 'rb') as stream:
            digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        if digest != manifest[key + '_sha256']:
            raise RuntimeError(f'{key} differs from the saved project')
    print('Source, baseline, 34 adopted assets, scripts and local font are ready.')
    print('This readiness check does not replace full decode or visual review.')


def main():
    from prepare_media import ensure_media
    ensure_media()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['check', *ACTIONS])
    args = parser.parse_args()
    if not (PROJECT / 'work_repair/compose_repair.py').exists():
        raise RuntimeError('Run python prepare_local.py first')
    if args.action == 'check':
        check()
    else:
        script = PROJECT / 'work_repair' / ACTIONS[args.action]
        subprocess.run([sys.executable, str(script)], cwd=PROJECT, check=True)


if __name__ == '__main__':
    main()
