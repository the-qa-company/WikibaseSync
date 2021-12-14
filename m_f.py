import configparser
import os

from pywikibot import config2

import others_config as cf
from utilities import io_worker as iw
import logging


def init(is_log=True):
    if is_log:
        iw.create_dir(cf.DIR_LOG)
        logging.basicConfig(
            filename=cf.DIR_LOG, format="%(message)s", level=logging.INFO
        )

    pre_load_services()


def pre_load_services():
    wikibase_login()


def wikibase_login():
    app_config = configparser.ConfigParser()
    app_config.read("config/application.config.ini")
    family = "my"
    mylang = "my"
    familyfile = os.path.relpath("./config/my_family.py")
    if not os.path.isfile(familyfile):
        print("family file %s is missing" % (familyfile))
    config2.register_family_file(family, familyfile)
    config2.password_file = "user-password.py"
    config2.usernames["my"]["my"] = app_config.get("wikibase", "user")
    #
    # app_config = configparser.ConfigParser()
    # app_config.read(f"{cf.DIR_ROOT}/config/application.config.ini")
    # dir_family = os.path.relpath(f"{cf.DIR_ROOT}/config/my_family.py")
    # if not os.path.isfile(dir_family):
    #     raise FileNotFoundError
    # config2.register_family_file("my", dir_family)
    # config2.password_file = f"{cf.DIR_ROOT}/config/user-password.py"
    # config2.usernames["my"]["my"] = app_config.get("wikibase", "user")
