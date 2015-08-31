import argparse
import configparser
import os
import sys

CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), "config.ini")

def main():
    parser = argparse.ArgumentParser(
        description="Configuration File Helper")

    action_group = parser.add_mutually_exclusive_group()

    action_group.add_argument("--set-repo",
        action="store", metavar="PATH",
        help="Set the path to the config file repository to be used")

    action_group.add_argument("--set-var-file",
        action="store", metavar="PATH",
        help="Set the path to the variable file")

    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)

    # Check which method was specified and route it to the
    # appropriate method
    if args.set_repo:
        set_repo(config, args.set_repo)
    elif args.set_var_file:
        set_var_file(config, args.set_var_file)
    else:
        parser.print_help()

def set_repo(config, repo_path):
    if not os.path.isdir(repo_path):
        print("Path specified is not a valid directory")
        sys.exit()

    set_config_value(config, "Paths", "repo_directory", repo_path)
    save_config_file(config)
    print("Repo path has been updated successfully")

def set_var_file(config, file_path):
    if not os.path.isfile(file_path):
        print("Path specified is not a file")
        sys.exit()

    set_config_value(config, "Paths", "variable_file", file_path)
    save_config_file(config)
    print("Variable file path has been updated successfully")

def save_config_file(config):
    with open(CONFIG_FILE_PATH, "w") as configfile:
        config.write(configfile)

def set_config_value(config, section, index, value):
    if section not in config:
        config[section] = {}

    config[section][index] = value

if __name__ == "__main__":
    main()