import os
import subprocess

# List of directories containing your .py files
directories = [
    r'C:\users\mschneiter\Dropbox\PostDoc\Cilialyzer\src',
    r'C:\users\mschneiter\Dropbox\PostDoc\Cilialyzer\src\LocalWavefieldAnalysis',
    r'C:\users\mschneiter\Dropbox\PostDoc\Cilialyzer\src\math_utils'
]

# List all .py files in the specified directories (recursively)
files = []
for directory in directories:
    for root, _, filenames in os.walk(directory):  # Walk through subdirectories
        for file in filenames:
            if file.endswith(".py"):
                files.append(os.path.join(root, file))

# PyInstaller path
pyinstaller_path = r"C:\Users\mschneiter\AppData\Roaming\Python\Python312\Scripts\pyinstaller.exe"

# Create a list of individual --add-data arguments
add_data_args = []
for file in files:
    add_data_args.append(f"--add-data={file}:{os.path.basename(file)}")

# Run the PyInstaller command with each --add-data as a separate argument
subprocess.run([pyinstaller_path, "--onefile"] + add_data_args + ["cilialyzer.py"])
