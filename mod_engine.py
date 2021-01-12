import os
from pathlib import Path

from save_engine import my_games_path, install_path
from xmldiff.main import patch_text
from jsonpatch import apply_patch
import xmldiff

import configparser
config = configparser.ConfigParser()

def read_file(file_name):
    with open(file_name, 'rb') as f:
        print("Reading " + file_name)
        return f.read()


def is_mod(file_name):
    return is_xml_diff(file_name) or is_json_patch(file_name)


def is_xml_diff(file_name):
    return os.path.splitext(file_name)[1] == ".xmldiff"


def is_json_patch(file_name):
    return os.path.splitext(file_name)[1] == ".jsonpatch"


def apply_mod(source, mod_file, name):
    if is_xml_diff(name):
        return lambda: patch_text(read_file(mod_file), source())
    elif is_json_patch(name):
        return lambda: apply_patch(read_file(mod_file), source())
    else:
        return lambda: read_file(mod_file)


mod = {}
mod_folders = ['mods']

if my_games_path() != install_path():
    mod_folders += [os.path.join(my_games_path(), 'mods')]

print("Loading mods...")

for mod_folder in mod_folders:
    if os.path.isfile(os.path.join(mod_folder, "mods.conf")):
        # config.read(.../mods.conf)
        config.read_string(open(os.path.join(mod_folder, "mods.conf"), 'r').read())
        if "mods" in config:
            #for mod_name in os.listdir(mod_folder):
            #for mod_name in mod_folders:
            for mod_name in config['mods']:
                #print("mod " + mod_name)
                if config['mods'][mod_name] == "false":
                    print("* mod " + mod_name + " is disabled")
                elif config['mods'][mod_name] == "true":
                    print("* mod " + mod_name + " is enabled")
                    if os.path.isdir(os.path.join(mod_folder, mod_name)):
                        for root, _, files in os.walk(os.path.join(mod_folder, mod_name)):
                            for name in files:
                                print(" -> ", root, name, os.path.join(root, name))
                                rel = os.path.relpath(root, os.path.join(mod_folder, mod_name))
                                source_file = Path(os.path.join(rel, os.path.splitext(name)[0] if is_mod(name) else name)).as_posix()
                                mod_file = os.path.join(root, name)
                                print(" | - rel " + rel)
                                print(" | - source_file " + source_file)
                                print(" | - mod_file " + mod_file)

                                source = mod.get(source_file, lambda: read_file(source_file))  # lambda chaining
                                mod[source_file] = apply_mod(source, mod_file, name)
    else:
        print("mods.conf not found.")

print("mod " + repr(mod))



        # for name in dirs:
        #     print(os.path.join(root, name))
