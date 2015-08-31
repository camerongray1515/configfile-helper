import argparse
import configparser
import os
import sys

CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), "config.ini")

class ConfigFileHelper():
    def main(self):
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

        self.config = configparser.ConfigParser()
        self.config.read(CONFIG_FILE_PATH)

        # Check which method was specified and route it to the
        # appropriate method
        if args.set_repo:
            self._set_repo(args.set_repo)
        elif args.set_var_file:
            self._set_var_file(args.set_var_file)
        else:
            parser.print_help()

    def _set_repo(self, repo_path):
        if not os.path.isdir(repo_path):
            print("Path specified is not a valid directory")
            sys.exit()

        self._set_config_value("Paths", "repo_directory", repo_path)
        self._save_config_file()
        print("Repo path has been updated successfully")

    def _set_var_file(self, file_path):
        if not os.path.isfile(file_path):
            print("Path specified is not a file")
            sys.exit()

        self._set_config_value("Paths", "variable_file", file_path)
        self._save_config_file()
        print("Variable file path has been updated successfully")

    def _save_config_file(self):
        with open(CONFIG_FILE_PATH, "w") as configfile:
            self.config.write(configfile)

    def _set_config_value(self, section, index, value):
        if section not in self.config:
            self.config[section] = {}

        self.config[section][index] = value

if __name__ == "__main__":
    c = ConfigFileHelper()
    c.main()