import argparse
import configparser
import os
import sys
import re

from jinja2 import Environment, DictLoader
from tabulate import tabulate
from argparse import RawTextHelpFormatter

CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), "config.ini")
APPROVE_ALL_INSTALLS = False

def main():
    command_table = [
        ["set-context-file", "FILE", "Set the path to the context file"],
        ["set-vcs-update-command", "COMMAND", "Set the shell command to cause "
            "the VCS used for the file repo to update to the latest"],
        ["list-files", "", "Lists all config files in the repository"],
        ["install-file", "FILE", "Installs a given file.  Path should be "
            "relative to the repository"],
        ["sync-all", "", "Installs all files that in the repo are eligible to "
            "be installed in this context"]
    ]
    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter,
        description="The following are valid commands:\n" + 
            tabulate(command_table, headers=["Command", "Args", "Description"])
    )

    parser.add_argument("command", action="store")
    parser.add_argument("args", action="store", nargs="*")

    # action_group.add_argument("set-context-file",
    #     action="store", metavar="PATH",
    #     help="Set the path to the context file")

    # action_group.add_argument("set-vcs-update-command",
    #     action="store", metavar="COMMAND",
    #     help="Set the shell command to cause the VCS used for the file "
    #         "repo to update to the latest version, e.g. 'git pull'")

    # action_group.add_argument("list-files", action="store_true",
    #     help="Lists all config files in the repository")

    # action_group.add_argument("install-file", action="store",
    #     metavar="PATH", help="Installs a given file.  Path should "
    #         "be relative to the repository")

    # action_group.add_argument("sync-all", action="store_true",
    #     help="Installs all files that in the repo are eligible to be "
    #         "installed in this context")

    parser.add_argument("--vcs-update", action="store_true", help="Run the "
        "predefined VCS update command (e.g. git pull) on the file repo before"
        " executing the specified command")

    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)

    if args.vcs_update:
        vcs_update_repo(config)

    # Check which method was specified and route it to the
    # appropriate method
    if args.command == "set-repo":
        set_repo(config, get_arg(parser, args.args, 0))
    elif args.command == "set-context-file":
        set_context_file(config, get_arg(parser, args.args, 0))
    elif args.command == "set-vcs-update-command":
        set_vcs_update_command(config, get_arg(parser, args.args, 0))
    elif args.command == "list-files":
        list_files(config)
    elif args.command == "install-file":
        install_file(config, get_arg(parser, args.args, 0), True)
    elif args.command == "sync-all":
        sync_all(config)
    else:
        print("'{0}' is not a valid command.  See '{1} --help'".format(
            args.command, sys.argv[0]))

def get_arg(parser, args, index):
    try:
        arg = args[index]
        return arg
    except IndexError:
        print("One or more required arguments are missing. See '{0} --help'"
            "".format(sys.argv[0]))
        sys.exit()

def vcs_update_repo(config):
    # Switch to the repo directory and run the VCS update command
    command = get_config_value(config, "Commands", "vcs_update")
    if not command:
        print("You must set a VCS update command with the "
            "--set-vcs-update-command option.")
        sys.exit()

    repo_path = get_config_value(config, "Paths", "repo_path")
    if not repo_path:
        print("You must set a config file repo first")
        sys.exit()

    os.chdir(repo_path)
    os.system(command)

def set_repo(config, repo_path):
    repo_path = os.path.abspath(repo_path)

    if not os.path.isdir(repo_path):
        print("Path specified is not a valid directory")
        sys.exit()

    set_config_value(config, "Paths", "repo_path", repo_path)
    save_config_file(config)
    print("Repo path has been updated successfully")

def set_context_file(config, file_path):
    file_path = os.path.abspath(file_path)

    if not os.path.isfile(file_path):
        print("Path specified is not a file")
        sys.exit()

    set_config_value(config, "Paths", "context_file", file_path)
    save_config_file(config)
    print("Context file path has been updated successfully")

def set_vcs_update_command(config, command):
    set_config_value(config, "Commands", "vcs_update", command)
    save_config_file(config)
    print("VCS update command has been updated successfully")

def list_files(config):
    repo_path = get_config_value(config, "Paths", "repo_path")
    if not repo_path:
        print("You must set a config file repo first")
        sys.exit()

    # For each file on disk, we need to go through and render the
    # template using the context to check whether the file is actually
    # to be included or not and then print a list of files and
    # their destinations for the given context
    file_table = []

    i = 1
    for path, subdirs, files in os.walk(repo_path):
        for name in files:
            file_path = os.path.join(path, name)
            path_inside_repo = os.path.join(path.replace(repo_path, ""), name)
            context = get_context_for_file(config, name)
            rendered_tuple = render_template(config, context, path_inside_repo)


            if rendered_tuple:
                file_table.append([i, path_inside_repo, rendered_tuple[0]])
            else:
                file_table.append([i, path_inside_repo, "Not due for "
                    "installation in this context"])
            i += 1

    print(tabulate(file_table, headers=["#", "File", "Destination"]))

def sync_all(config):
    repo_path = get_config_value(config, "Paths", "repo_path")
    if not repo_path:
        print("You must set a config file repo first")
        sys.exit()

    print("Installing all files")
    for path, subdirs, files in os.walk(repo_path):
        for name in files:
            path_inside_repo = os.path.join(path.replace(repo_path, ""), name)
            install_file(config, path_inside_repo, False)
    print("Complete!")

def install_file(config, path, single_install):
    # single_install argument will remove the "yes/no to all" options
    # from the confirmation message.  Should therefore be set true when
    # we are only installing a single file

    if single_install:
        valid_options = ("y", "n")
        option_string = "[Y]es, [N]o"
    else:
        valid_options = ("y", "n", "a")
        option_string = "[Y]es, [N]o, Yes to [A]ll"

    global APPROVE_ALL_INSTALLS

    context = get_context_for_file(config, path)
    try:
        rendered_tuple = render_template(config, context, path)
    except FileNotFoundError:
        print("File {0} not found in repository. Skipping!".format(path))
        return

    if not APPROVE_ALL_INSTALLS:
        response = ""
        while response.lower() not in valid_options:
            response = input("Are you sure you want to install {0}, this will "
                "overwrite any existing files at the destination? {1}: "
                "".format(path, option_string))

        if response == "a":
            APPROVE_ALL_INSTALLS = True
        elif response == "n":
            print("Skipping install of {0}".format(path))
            return

    if rendered_tuple:
        destination_path, rendered_body = rendered_tuple
    else:
        print("File {0} is not due for installation in this context. Skipping!"
            "".format(path))
        return
    
    print("Installing {0} to {1}... ".format(path, destination_path), end="")

    try:
        # If the directory leading up to the destination path doesn't exist,
        # create it
        if not os.path.isdir(os.path.dirname(destination_path)):
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        with open(destination_path, "w") as f:
            f.write(rendered_body)
            print("Done!")
    except PermissionError:
        print("ERROR!")
        print("\tYou do not have permission for this location. Skipping!")

def get_context_for_file(config, filename):
    context_file_path = get_config_value(config, "Paths", "context_file")

    context = configparser.ConfigParser()
    try:
        context.read(context_file_path)
    except:
        print("Context file could not be located or is invalid")
        sys.exit()

    # First build up a dictionary of the context in the GLOBAL section
    # then go through the file sepecific ones and add them to the dict.
    # If there is a variable in both the local and global sections,the
    # local one should be used
    file_context = {}
    try:
        for (key, value) in context.items("GLOBAL"):
            file_context[key] = value

        for (key, value) in context.items(filename):
            file_context[key] = value
    except configparser.NoSectionError:
        pass # Don't care if either section is missing

    return file_context

def render_template(config, context, path_inside_repo):
    repo_path = get_config_value(config, "Paths", "repo_path")
    if not repo_path:
        print("You must set a config file repo first")
        sys.exit()

    if path_inside_repo[0] == "/":
        path_inside_repo = path_inside_repo[1:]

    file_path = os.path.join(repo_path, path_inside_repo)

    template_content = {}
    with open(file_path, "r") as f:
        template_content["template"] = f.read()

    jinja_env = Environment(loader=DictLoader(template_content))

    rendered = jinja_env.get_template("template").render(context).splitlines()

    # Separate the destination path on the first (non-empty) line from
    # the rest of the file or return None if this file does not exist
    # which would mean that the template should not be installed given
    # the current context
    dest_string = ""
    while dest_string == "":
        dest_string = rendered[0]
        rendered = rendered[1:]

    dest_match = re.search(r"^\s*#>\ +(.*)$", dest_string)

    if not dest_match or not dest_match.group(1):
        return None

    destination_path = dest_match.group(1)
    rendered_body = "\n".join(rendered)
    return (destination_path, rendered_body)

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
