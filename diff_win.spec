# -*- mode: python -*-
import sys
sys.setrecursionlimit(10000)

from PyInstaller.utils.hooks import is_module_satisfies
import PyInstaller.compat
PyInstaller.compat.is_module_satisfies = is_module_satisfies

block_cipher = None


a = Analysis(['diffraction_ring_profiler.py'],
             pathex=['C:\\Users\\owner\\diff-ring'],
             binaries=[],
             datas=[('icons', 'icons'),
                    ('examples', 'examples'), 
                    ('iotbx_cif.py', '.'),
                    ('README.md', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='diffraction_ring_profiler',
          debug=False,
          strip=False,
          upx=True,
          console=True , icon='icons\\diff_profiler_ico.ico')
