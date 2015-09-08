# ConfigFileHelper
ConfigFileHelper is a simple Python script that makes managing configuration files/dotfiles easy across multiple systems where each system may require slight modifications in what files are required or the content of the files themselves.


## Terminology
### File Repo
Your config files must be kept in a directory called the "file repo", this can also contain subdirectories to make it easier to organise files.  Ideally you would want to use some sort of VCS to manage this repo but this is not required.

### Context
This script uses what is known as a "context file" - This is a file in INI format.  In this file you can define variables that are then passed to Jinja2 when it is rendering the template for a given file.  The context file has a "GLOBAL" section where variables are passed to all templates and can also have sections for each file (the section should be named the same as the file it is for).  If a variable exists in both the global and file specific sections, the file specific value will be used.

## Command Line Usage
Below are some examples of how to invoke the script.  Full usage can be found by using the `--help` command line flag.

### Settings
Before being able to use the script, you must set the path to the context file and the path to the file repository as follows

`configfile-helper.py set-context-file /path/to/context/file.ini`

`configfile-helper.py set-repo /path/to/file/repo/`

### Managing config files
Once the settings above have been configured, it is now possible to use the script to manage the config files in your repository.

**List files in repository** - The following command will list all files in the repository as well as a location to which they will be installed.  You will need to use the paths from here to install individual files.

`configfile-helper.py list-files`

**Install a single file** - This command will render and install a single file from the repository to the correct location on the system.  \<PATH\> should be the path relative to the repository as shown by the list-files command above.

`configfile-helper.py install-file <PATH>`

**Install all files** - This command will install all files in the repository (assuming the file has a destination path given the context).

`configfile-helper.py sync-all`

### VCS Update
It is also possible to sync your VCS repository (e.g. run a `git pull`) from the script.  First of all you must set the command that you use to sync your VCS with the following command:

`configfile-helper.py set-vcs-update-command "<COMMAND>"`

For example, if you use Git to provide version control for your file repository you would run:

`configfile-helper.py set-vcs-update-command "git pull"`

You can now update the VCS before running any command with the script simply by providing the --vcs-update flag.  For example, to update the VCS repository before running the `sync-all` command to install all files, you would run:

`configfile-helper.py --vcs-update sync-all`


## Config File Format
The config files are rendered using Jinja2 and provided variables from the context file.  The Jinja2 docs would be the best place to look for informaiton on templating.

All files must, once rendered, specify the path which the file will be copied to once rendered.  This should be done by placing the symbol `#>` on the first line of the file followed by the path.  For example

```
#> /path/where/file/should/be/installed.conf

[Rest of the config file here]
foo="bar"
```
If this line is not present, the file will not be installed.  This means that you can do clever stuff with the context file and templating to only install a file on certain machines.  For example, in your context file you have a variable called "machine_type" which can either be "laptop" or "desktop".  To install a config file only on laptops (say to monitor the battery level), you could do the following

```
{% if machine_type == "laptop" %}
#> /path/where/file/should/be/installed.conf
{% endif %}

[Rest of the config file here]
foo="bar"
```
When this file is rendered with the variable set to laptop, the `#>` line is rendered  and the file will be installed, if the variable is set to desktop however the line will not be redered and the file will not be installed.  It is also possible to use more advanced logic to install the file to a path that varies based on the context.  Say for example you have a variable "username" in the context file set to "foobar".  You could do something like this:

```
#> /home/{{ username }}/file.conf

[Rest of the config file here]
foo="bar"
```