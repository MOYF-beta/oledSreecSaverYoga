from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = {'packages': [], 'excludes': []}

base = 'Win32GUI'

executables = [
    Executable('screenSaver_dual.py', base=base, target_name = 'oledScreenSaver')
]

setup(name='oledScreenSaver',
      version = '1.1',
      description = 'oledScreenSaver for yoga book 9i',
      options = {'build_exe': build_options},
      executables = executables)
