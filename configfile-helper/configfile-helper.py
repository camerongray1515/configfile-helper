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

    action_group.add_argument("--list-files", action="store_true",
        help="Lists all config files in the repository")

    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)

    # Check which method was specified and route it to the
    # appropriate method
    if args.set_repo:
        set_repo(config, args.set_repo)
    elif args.set_var_file:
        set_var_file(config, args.set_var_file)
    elif args.list_files:
        list_files(config)
    else:
        parser.print_help()

def set_repo(config, repo_path):
    repo_path = os.path.abspath(repo_path)

    if not os.path.isdir(repo_path):
        print("Path specified is not a valid directory")
        sys.exit()

    set_config_value(config, "Paths", "repo_path", repo_path)
    save_config_file(config)
    print("Repo path has been updated successfully")

def set_var_file(config, file_path):
    file_path = os.path.abspath(file_path)

    if not os.path.isfile(file_path):
        print("Path specified is not a file")
        sys.exit()

    set_config_value(config, "Paths", "variable_file", file_path)
    save_config_file(config)
    print("Variable file path has been updated successfully")

def list_files(config):
    repo_path = get_config_value(config, "Paths", "repo_path")
    if not repo_path:
        print("You must set a config file repo first")
        sys.exit()

    for path, subdirs, files in os.walk(repo_path):
        for name in files:
            print(os.path.join(path.replace(repo_path, ""), name))

def get_context_for_file(config, filename):
    variable_file_path = get_config_value(config, "Paths", "variable_file")

    variables = configparser.ConfigParser()
    variables.read(variable_file_path)

    # First build up a dictionary of the variables in the GLOBAL section
    # then go through the file sepecific ones and add them to the dict.
    # If there is a variable in both the local and global sections,the
    # local one should be used
    template_context = {}
    try:
        for (key, value) in variables.items("GLOBAL"):
            template_context[key] = value

        for (key, value) in variables.items(filename):
            template_context[key] = value
    except configparser.NoSectionError:
        pass # Don't care if either section is missing

    return template_context

def save_config_file(config):
    with open(CONFIG_FILE_PATH, "w") as configfile:
        config.write(configfile)

def set_config_value(config, section, index, value):
    if section not in config:
        config[section] = {}

    config[section][index] = value

def get_config_value(config, section, index):
    if section not in config:
        return None

    if index not in config[section]:
        return None

    return config[section][index]

if __name__ == "__main__":
    main()
