#configuration for pywikibot
import sys

from util.util import import_one

arg = sys.argv[1]
print(f"Importing {arg}")
import_one(arg)