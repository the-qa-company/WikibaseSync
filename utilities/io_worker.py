import csv
import fnmatch
import os

import numpy as np
import logging


def print_status(message, is_screen=True, is_log=True):
    if is_screen:
        print(message)
    if is_log:
        logging.info(message)


def create_dir(file_dir):
    folder_dir = os.path.dirname(file_dir)
    if not os.path.exists(folder_dir):
        os.makedirs(folder_dir)


def load_object_csv(file_name, encoding="utf8"):
    content = []
    if os.path.exists(file_name):
        with open(file_name, "r", encoding=encoding, errors="ignore") as f:
            reader = csv.reader(f, delimiter=",")
            for r in reader:
                row_norm = []
                for c in r:
                    row_norm.append(c)
                content.append(row_norm)
    else:
        raise FileNotFoundError
    return content


def save_object_csv(file_name, rows):
    create_dir(file_name)
    temp_file = "%s.temp" % file_name
    with open(temp_file, "w") as f:
        try:
            writer = csv.writer(f, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL)
            for r in rows:
                if (
                    isinstance(r, list)
                    or isinstance(r, tuple)
                    or isinstance(r, np.ndarray)
                ):
                    writer.writerow(r)
                else:
                    writer.writerow([r])
        except Exception as message:
            print(message)
    if os.path.exists(file_name):
        os.remove(file_name)
    os.rename(temp_file, file_name)


def get_files_from_dir_subdir(folder_path, extension="*"):
    all_files = []
    for root, _, file_dirs in os.walk(folder_path):
        for file_dir in fnmatch.filter(file_dirs, "*.%s" % extension):
            if ".DS_Store" not in file_dir:
                all_files.append(os.path.join(root, file_dir))
    return all_files


def get_files_from_dir(
    folder_path, extension="*", limit_reader=-1, is_sort=False, reverse=False
):
    all_file_dirs = get_files_from_dir_subdir(folder_path, extension)

    if is_sort:
        file_with_size = [(f, os.path.getsize(f)) for f in all_file_dirs]
        file_with_size.sort(key=lambda f: f[1], reverse=reverse)
        all_file_dirs = [f for f, _ in file_with_size]
    if limit_reader < 0:

        limit_reader = len(all_file_dirs)
    return all_file_dirs[:limit_reader]
