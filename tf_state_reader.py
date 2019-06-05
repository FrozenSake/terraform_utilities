"""A json reader for importing with terraform.

Imports subprocess, to run commands.
Imports json, to read json objects.
Imports os, for file path stuff.
Imports glob, because it's great
"""

import subprocess
import glob
import json
import os

class state_reader:
    """state compiler object.

    Consumes the terraform state json to produce a.tf file matching the state of objects.
    """

    def __init__(self):
        """Init state_reader class."""
        self.state_files = []
        self.set_directory()
        self.read_state()

    def set_directory(self):
        """Set current working directory."""
        pass

    def find_tfstate(self, directory=None):
        """Find tfstate file in given directory, if no directory, in current working directory."""
        if directory == None:
            dir_path = os.getcwd()
        else:
            dir_path = directory
        os.chdir(dir_path)
        self.state_files = glob.glob('*.tfstate')
    
    def read_state(self):
        """Read the tfstate, and if it hasn't been located, call find_tfstate() to find it."""
        if not self.state_files:
            self.find_tfstate()
            if not self.state_files:
                print("ERROR: Cannot find a .tfstate file in the supplied directory.")
                exit(2)
        for file in self.state_files:
            with open(file) as json_file:
                name = input("Please name the .tf file name (*.tf) !!NOTE: this will append to the file, or create it!! : ")
                data = json.load(json_file)
                self.create_tf_file(data, name)

    def create_tf_file(self, data, name):
        """Create a .tf file for each state file."""
        try:
            terraform_file = open(name, "a")
            terraform_file.write("\n\n")
        except:
            terraform_file = open(name, "a+")
        for i in range(len(data["resources"])):
            for instance in data["resources"][i]["instances"]:
                resource_block = self.create_resource(data["resources"][i]["type"], data["resources"][i]["name"], instance["attributes"])
                resource_block = self.style_conversion(resource_block)
                terraform_file.write(resource_block)
        terraform_file.close()

    def style_conversion(self, block):
        """Convert variables, etc. to terraform standard (e.g. True -> true)."""
        block = str(block).replace("True", "true")
        block = block.replace("False", "false")
        return block

    def create_resource(self, res_type, res_name, block):
        """Create the .tf format for a resource given the passed block."""
        return f"resource \"{res_type}\" \"{res_name}\" {{\n{self.create_instance_block(block)}}}\n"

    def create_instance_block(self, block, isList = False):
        """Create a resource block for an instance in the .tf file."""
        resource_block = ""
        lists = {}
        dicts = {}
        if isList == True:
            spacing = "    "
        else:
            spacing = "  "
        for piece in block:
            if type(block) is str:
                resource_block += f"{spacing}{block}\n"
                break
            elif type(block[piece]) is dict:
                dicts[piece] = self.create_instance_block(block[piece])
            elif type(block[piece]) is list:
                for instance in block[piece]:
                    lists[piece] = self.create_instance_block(instance, True)
            else:
                resource_block += f"{spacing}{piece} = {block[piece]} \n"
        for ls in lists:
            resource_block += f"\n{spacing}{ls} {{\n{lists[ls]}{spacing}}}\n"
        for dct in dicts:
            resource_block += f"{spacing}{dct}\n"
        return(resource_block)

