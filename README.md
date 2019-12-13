# Wikibase Editor documentation

# Installation remarks
- ensure you have python3 and `sudo yum install python3-devel` or `sudo apt install python3-dev`
- `sudo apt install virtualenv`
- `virtualenv venv --python=python3`
- `source venv/bin/activate`
- `pip install -r requirements.txt`
-  git clone https://github.com/wikimedia/pywikibot.git
- change
https://github.com/wikimedia/pywikibot/blob/26deab88936cbf85aa24e1ddfc9b62e81d80a9bb/pywikibot/data/api.py#L1615
with:
messages = None
if 'messages' in error:
            messages = error['messages']
        #messages = error.pop('messages', None)
- pip install pywikibot/ to install the local dependency
-/Library/Frameworks/Python.framework/Versions/3.7/lib/python3.7/json/decoder.py
line 337 unnecessary output
- attach to new wiki
    - change url in config/my_family.py
    - change user-confing.py
    - change user-password.py