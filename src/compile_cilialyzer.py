import os
import subprocess

# PyInstaller path
#pyinstaller_path = r"C:\Users\mschneiter\AppData\Roaming\Python\Python312\Scripts\pyinstaller.exe"
pyinstaller_path = r"C:\Users\mschneiter\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.8_qbz5n2kfra8p0\LocalCache\local-packages\Python38\Scripts\
"

args = [
    pyinstaller_path,
    "--noconsole",
    "--onefile",
    "--noupx",
    "--paths=math_utils",
    "--paths=LocalWavefieldAnalysis",
    "--paths=features",
    "--paths=config",
    "--paths=."
    "cilialyzer.py"
]

# Run the PyInstaller command
subprocess.run(args)
