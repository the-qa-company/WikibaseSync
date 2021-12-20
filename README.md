# WikibaseSync documentation
This is an open-source project developed by [The QA Company](https://the-qa-company.com).

*You can use this project to sync Wikidata Items and Properties with your arbitrary Wikibase.*

This tool is actively used at [https://linkedopendata.eu](https://linkedopendata.eu).

## Features
* Import Wikidata Items and Properties
* Track the changes on Wikidata and Keep synchronized
* Monitor the changes in Wikibase and import corresponding Wikidata properties and statements. etc 

## Installation remarks

- ensure you have python3 and `sudo yum install python3-devel` or `sudo apt install python3-dev`
- `sudo apt install virtualenv`
- `virtualenv venv --python=python3`
- `source venv/bin/activate`
- `pip install -r requirements.txt`

## Setup

 1. Login in the Wikibase instance (for example using the **admin** account)
 2. Go to "Special Pages" -> "Bot passwords" and type the name of your bot (for example **WikidataUpdater**)
 3. Give him the follwing rights: "High-volume editing", "Edit existing pages" and "Create, edit, and move pages"
 4. Copy your username in "user-config.py"
 5. Copy your username, the name of the bot and the password in "user-password.py"
 6. Update the application.config.ini  [`config/application.config.ini`]
     
### Application config

Define the Wikibase properties in this file. 
> ### *application.config.ini*
>
> located in `config/application.config.ini` in the repository 
>   
>  Customize this file based on your Wikibase properties. Check the example properties below (it matches the default properties of a [Wikibase Docker installation](https://github.com/wmde/wikibase-release-pipeline))
> 
>  ```
> [wikibase]
> user = admin
> sparqlEndPoint = http://localhost:8834/proxy/wdqs/bigdata/namespace/wdq/sparql
> domain = localhost:80
> protocol = http
> apiUrl= http://localhost:80/w/api.php
> entityUri=http://wikibase.svc/entity
> propertyUri=http://wikibase.svc/prop
> 
>  ```

## Usage
 - `python import_one.py Q1` to import Q1 from Wikidata (if already imported the entity will be put in sync)
 - `python import_one.py P31` to import P31 from Wikidata (if already imported the entity will be put in sync)
 - `python import_all_changes.py` to sync all currently imported items
 - `python import_recent_changes.py` to sync all entities that where changed in Wikidata (calling this regularly allows to maintain all instances and properties in sync with Wikidata) 
