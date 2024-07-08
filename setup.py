from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = {'packages': [], 'excludes': []}

base = 'gui'

executables = [
    Executable('screenSaver_dual.py', base=base, target_name = 'screenSaver_dual.exe')
]

setup(name='screenSaver_dual',
      version = '1.0',
      description = 'oled screen saver',
      options = {'build_exe': build_options},
      executables = executables)
