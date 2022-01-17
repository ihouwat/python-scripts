# ! python
# mcb.pyw - Saves and loads pieces of text to the clipboard.

# Usage: py.exe mcb.pyw save <heyword> - Saves keyword to clipboard.
#        py.exe mcb.pyw <keyword> - Loads keyword to clipboard.
#        py.exe mcb.pyw keys - Loads all keywords to clipboard.
#        py.exe mcb.pyw list - Loads entire object to clipboard.

import shelve, pyperclip, sys

mcbShelf = shelve.open('mcb')

# Output instructions if no arguments given
if len(sys.argv) < 2:
    pyperclip.copy("""Usage:\npy.exe mcb.pyw save <heyword> - Saves keyword to clipboard.\npy.exe mcb.pyw <keyword> - Loads keyword to clipboard.\npy.exe mcb.pyw keys - Loads all keywords to clipboard.\npy.exe mcb.pyw list - Loads entire object to clipboard.\n""")
    sys.exit()

# Save clipboard content.
if len(sys.argv) == 3 and sys.argv[1].lower() == 'save':
  mcbShelf[sys.argv[2]] = pyperclip.paste()

elif len(sys.argv) == 2:
  # List keywords.
  if sys.argv[1].lower() == 'keys':
    pyperclip.copy(str(list(mcbShelf.keys())))
  #  List keywords and values.
  if sys.argv[1].lower() == 'list':
    pyperclip.copy(str(list(mcbShelf.items())))
  #  Load items.
  elif sys.argv[1] in mcbShelf:
    pyperclip.copy(mcbShelf[sys.argv[1]])

mcbShelf.close()