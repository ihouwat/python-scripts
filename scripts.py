# ! python 3

# script-list.py - Prints out script descriptions for all scripts in this directory. Description should be on the third line of each script.

from pathlib import Path

dir = Path(r'C:\Users\houwa\python-files')
extensions = {'.py', '.pyw'}

for path in dir.glob(r'**/*'):
  if path.suffix in extensions:
    file = open(Path(path))
    print(file.readlines()[2])