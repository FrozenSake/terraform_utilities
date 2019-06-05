"""Utilities for importing vsphere with terraform.

Imports subprocess, to run commands.
Imports json, to read json objects.
Imports os, for file path stuff.
Imports glob, because it's great
"""

import subprocess
import glob
import json
import os
import tf_state_reader

classifiers = {
    "vsphere_virtual_machine": "vm"
}

class vsphere_compiler:
    """Vsphere_compiler object.

    Prompts for, and contains, necessary information to create a terraform import command for a vsphere resource for terraform.
    Will not succesfully build import statements where the (resource "type" "name" {}) block does not correspond to the resource name on vsphere.
    """

    def __init__(self):
        """Init vsphere_compiler class, takes inputs, parses resources, compiles commands, and runs commands."""
        self.datacenter = input("Enter the datacenter name: ")
        self.file = input("Enter the terraform file to parse: ")
        self.resources = {}
        self.commands = []

        #print("Above command block")

        self.Parse_Resource(self.file)
        self.Compile_Commands()
        self.Run_Commands()
        

    def Compile_ID(self, resource_type, resource_name):
        """Compile the ID that terraform import will use."""
        #print("inside Compile_ID")

        classifier = classifiers[resource_type]
        return f"/{self.datacenter}/{classifier}/{resource_name}"

    def Parse_Resource(self, file):
        """Open the .tf file and parses through it to extract resources."""
        #print("inside Parse_Resouce")

        with open(file, "r") as f:
            #print("File is open")
            lines = f.readlines()
            for line in lines:
                sections = line.split(" ")
                if sections[0] == "resource":
                    resource_type = sections[1].strip('\"')
                    resource_name = sections[2].strip('\"')
                    self.resources[resource_name] = resource_type

    def Compile_Commands(self):
        """Compile a list of commands required to import all the specified resources."""
        #print("inside Compile_Commands")

        command_list = []
        resources = self.resources
        for resname in resources:
            id = self.Compile_ID(resources[resname], resname)
            command = f"terraform import {resources[resname]}.{resname} {id}"
            command_list.append(command)
        self.commands = command_list

    def Run_Commands(self):
        """Run all the resources from the command list."""
        #print("inside Run_Commands")

        for comm in self.commands:
            #print(comm)
            subprocess.call(comm)

if __name__ == '__main__':
    if input("Compile terraform imports? (y/n): ").lower() == "y":
        vcomp = vsphere_compiler()
    vread = tf_state_reader.state_reader()
    #vread.create_resource_block()
