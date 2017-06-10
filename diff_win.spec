# -*- mode: python -*-

block_cipher = None


a = Analysis(['diffraction_ring_profiler.py'],
             pathex=['C:\\Users\\owner\\diff-ring'],
             binaries=[],
             datas=[('icons', 'icons')],
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
