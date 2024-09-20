from sys import platform

if 'linux' in platform:
    from .linux.process import *

elif 'win' in platform:
    from .windows.process import *

else:
    raise Exception("Unsupported platform")
