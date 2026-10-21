"""Render all instructor decks to PDFs using a private LibreOffice profile."""
from pathlib import Path
import shutil
import subprocess
import tempfile
ROOT=Path(__file__).resolve().parents[1]

def render():
    with tempfile.TemporaryDirectory(prefix='course-render-') as d:
        d=Path(d)
        subprocess.run(['libreoffice',f'-env:UserInstallation={(d/"profile").as_uri()}',
            '--headless','--convert-to','pdf','--outdir',str(d),
            *[str(ROOT/f'module{m}/Module{m}.pptx') for m in (1,2,3)]],check=True,timeout=180)
        for m in (1,2,3):
            source=d/f'Module{m}.pdf'
            if not source.exists(): raise RuntimeError(f'Render failed: {source.name}')
            shutil.copyfile(source,ROOT/f'module{m}/Module{m}.pdf')
if __name__=='__main__': render()
