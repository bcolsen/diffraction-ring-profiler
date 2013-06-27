# -*- mode: python -*-
a = Analysis(['C:\\diffraction-ring-profiler\\diffraction_ring_profiler.py'],
             pathex=['C:\\diffraction-ring-profiler'],
             hiddenimports=[],
             hookspath=None)

##### include mydir in distribution #######
def extra_datas(mydir):
    def rec_glob(p, files):
        import os
        import glob
        for d in glob.glob(p):
            if os.path.isfile(d):
                files.append(d)
            rec_glob("%s/*" % d, files)
    files = []
    rec_glob("%s/*" % mydir, files)
    extra_datas = []
    for f in files:
        extra_datas.append((f, f, 'DATA'))

    return extra_datas
###########################################

# append the 'data' dir
a.datas += extra_datas('icons')
a.datas += extra_datas('examples')

pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=os.path.join('dist', 'diffraction_ring_profiler.exe'),
          debug=False,
          strip=None,
          upx=True,
          icon='icons\\diff_profiler_ico.ico'
          console=True )
