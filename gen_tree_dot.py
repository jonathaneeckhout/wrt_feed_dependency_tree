import os
import os.path
import sys
from pathlib import Path
import re


def parse_depends(depends):

    cleanup = depends.replace("DEPENDS", "")

    cleanup = re.sub(r'TARGET_.*:', '', cleanup)
    cleanup = re.sub(r'PACKAGE_.*:', '', cleanup)
    cleanup = re.sub(r'.*:', '', cleanup)

    cleanup = cleanup.replace(":=", "")

    cleanup = cleanup.replace("+", "")

    cleanup = cleanup.replace("=", "")
    cleanup = cleanup.replace("\\", "")
    cleanup = cleanup.replace("@", "")
    cleanup = cleanup.replace("$", "")
    cleanup = cleanup.replace("(", "")
    cleanup = cleanup.replace(")", "")
    cleanup = cleanup.replace("\t", "")
    cleanup = cleanup.replace("!", "")
    cleanup = cleanup.replace(' ', "\n")
    cleanup = cleanup.replace("-", "_")

    # print(cleanup)

    return cleanup.splitlines()


def parse_makefile(component, makefile):
    print("{}: Parsing makefile: {}".format(component, makefile))
    search = open(makefile)
    depends = ""
    overflow = False
    licences = []
    for line in search:
        if overflow or re.match(r'^\s*DEPENDS', line):
            depends += line
            if "\\" in line:
                overflow = True
            else:
                overflow = False
        if re.match(r'^\s*PKG_LICENSE', line):
            print("LICENCE:{}".format(line))
            licences.append(line)

    return parse_depends(depends), licences


def find_makefile(directory):
    component_basepath = Path(directory)
    files_in_component_basepath = component_basepath.iterdir()
    makefile = None
    for component_item in files_in_component_basepath:
        if component_item.is_file and component_item.name == "Makefile":
            makefile = component_item
    return makefile


def loop_and_find_makefile(directory, outfile, licenses_file):

    makefile = find_makefile(directory)
    depends = []

    if makefile:
        depends, licences = parse_makefile(directory.name, makefile)
        for depend in depends:
            if depend != '':
                outfile.write(
                    '    {} -> {}\n'.format(directory.name.replace("-", "_"), depend))
        for licence in licences:
            clean_licence = licence.replace('\n', "").replace("PKG_LICENSE_FILES:=", "").replace("PKG_LICENSE:", "").replace("LICENSE", "")
            if clean_licence != "":
                licenses_file.write('{} = {}\n'.format(directory.name.replace("-", "_"), clean_licence))
    else:
        basepath = Path(directory)
        files_in_basepath = basepath.iterdir()
        for item in files_in_basepath:
            if item.is_dir() and item.name != ".git":
                depends = depends + loop_and_find_makefile(item, outfile, licenses_file)

    return depends


############## main program ######################
if len(sys.argv) != 4:
    print(
        "at least 2 argument ./gen_tree_dot.py [path_to_feed] [outfile] [licenses_file]")
    sys.exit(-1)

#open dir
full_path = os.path.abspath(sys.argv[1])
print("Checking dependencies for feed:{}".format(full_path))

outfile = open(sys.argv[2], "w")
outfile.write('digraph G {\n')
outfile.write('    rankdir=LR\n')
outfile.write('    splines=true\n')
outfile.write('    layout=neato\n')
outfile.write('    overlap = false;\n')
outfile.write('    node[width=.25,height=.375,fontsize=9]\n')

licenses_file = open(sys.argv[3], "w")

loop_and_find_makefile(full_path, outfile, licenses_file)

outfile.write('}\n')

outfile.close()
licenses_file.close()
