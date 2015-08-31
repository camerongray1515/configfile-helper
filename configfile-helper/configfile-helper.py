import argparse
import configparser
import os
import sys

CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), "config.ini")

class ConfigFileHelper():
    def main(self):
        parser = argparse.ArgumentParser(description="Configuration File Helper")

        action_group = parser.add_mutually_exclusive_group()

        action_group.add_argument("--set-repo",
            action="store", metavar="REPO_PATH",
            help="Set the path to the config file repository to be used")
        args = parser.parse_args()

        self.config = configparser.ConfigParser()
        self.config.read(CONFIG_FILE_PATH)

        # Check which method was specified and route it to the appropriate
        # method
        if args.set_repo:
            self._set_repo(args.set_repo)

    def _set_repo(self, repo_path):
        if not os.path.isdir(repo_path):
            print("Path specified is not a valid directory")
            sys.exit()

        if not "Paths" in self.config:
            self.config["Paths"] = {}

        self.config["Paths"]["repo_directory"] = repo_path
        self._save_config_file()
        print("Repo path has been updated successfully")

    def _save_config_file(self):
        with open(CONFIG_FILE_PATH, "w") as configfile:
            self.config.write(configfile)

if __name__ == "__main__":
    c = ConfigFileHelper()
    c.main()