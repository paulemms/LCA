import PyInstaller.config
from pathlib import Path
Path("c:\\temp\\build").mkdir(parents=True, exist_ok=True)
Path("c:\\temp\\dist").mkdir(parents=True, exist_ok=True)
PyInstaller.config.CONF['workpath'] = "c:\\temp\\build"
PyInstaller.config.CONF['distpath'] = "c:\\temp\\dist"


block_cipher = None


a = Analysis(['main.py'],
             pathex=['.'],
             binaries=[(r'C:\Users\Paul\Anaconda3\envs\LCA\Library\bin\glpsol.exe', '.'), (r'C:\Users\Paul\Anaconda3\envs\LCA\Library\bin\glpk_4_65.dll', '.'),],
             datas=[(r'C:\Users\Paul\Anaconda3\envs\LCA\Lib\site-packages\palettable\colorbrewer\data', r'palettable\colorbrewer\data')],
             hiddenimports=['statsmodels.tsa.statespace._filters._conventional',
                            'pint',
                            'qtconsole.client',
                            'pyomo.common.plugins',
                            'pyomo.opt.plugins',
                            'pyomo.core.plugins',
                            'pyomo.dataportal.plugins',
                            'pyomo.duality.plugins',
                            'pyomo.checker.plugins',
                            'pyomo.repn.plugins',
                            'pyomo.repn.util',
                            'pyomo.pysp.plugins',
                            'pyomo.neos.plugins',
                            'pyomo.solvers.plugins',
                            'pyomo.gdp.plugins',
                            'pyomo.mpec.plugins',
                            'pyomo.dae.plugins',
                            'pyomo.bilevel.plugins',
                            'pyomo.scripting.plugins',
                            'pyomo.network.plugins',
                            'pandas._libs.skiplist'
             ],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
a.datas += Tree(r'C:\Users\Paul\Anaconda3\envs\LCA\Lib\site-packages\statsmodels', prefix='statsmodels')

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='main')
