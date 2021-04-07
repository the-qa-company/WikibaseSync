# WikibaseSync documentation

# Installation remarks
- ensure you have python3 and `sudo yum install python3-devel` or `sudo apt install python3-dev`
- `sudo apt install virtualenv`
- `virtualenv venv --python=python3`
- `source venv/bin/activate`
- `pip install -r requirements.txt`

# Setup
- Login in the Wikibase instance
- Go to "Special Pages" -> "Bot passwords" and type the name of your bot
- Give him the follwing rights: "High-volume editing", "Edit existing pages" and "Create, edit, and move pages"
- Copy your username in "user-config.py" and in "main.py"
- Copy the name of the bot and the password in "user-password.py"
- In config/my_family.py specify the URL of the wikibase 
