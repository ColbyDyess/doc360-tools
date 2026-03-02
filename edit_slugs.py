import re
import sys
import os.path
import csv



def set_slug_version(slug: str, version: str) -> str:
    """
    Appends or replaces a version suffix on a slug string.

    If the slug already ends with a version-like string (v-<int>-<int>),
    that suffix is replaced with the given version. Otherwise, the version
    is appended.

    Args:
        slug:    Alphanumeric slug with optional dash separators (e.g. "my-article").
        version: Version string in the format "v-xx-yy" (e.g. "v-7-12").

    Returns:
        The slug with the version appended or replaced.
    """
    # Strip a trailing version string and its preceding dash (if any).
    base = re.sub(r'-?v-?\d+-\d+(?:-\d+)?$', '', slug)

    if base:
        return f"{base}-{version}"
    else:
        # slug was entirely a version string; return just the new version
        return version

###############################################################################
#
# get_input_file
#
# Opens the file that contains updated slug values
#
def get_input_file(args):
    # Make sure we got at least one parameter beyond the python command
    if len(args)<=1:
        print("ERROR: Must provide a file to read\n")
        quit()
    # Check that the file exists
    if os.path.isfile(args[1]):
        print("Read slug values from: " + args[1])
        return open(args[1],"r")
    else:
        print("ERROR: File '" + args[1] + "' does not exist\n")
        quit()
    return


###############################################################################
#
# edit_slugs
#
# Takes in a csv file that contains all the updated slugs.
# The file must follow the very specific format, or things'll break.
#
def edit_slugs(in_file, slug_version, output_file_name):
    csvFile = csv.reader(in_file)
    # skip the header
    next(csvFile)
    output_file = open(output_file_name, "w")
    for lines in csvFile:
        article_id = lines[0]
        article_language = lines[1]
        article_type = lines[2]
        article_title = lines[3]
        article_slug = lines[4]
        new_slug = set_slug_version(article_slug, slug_version)
        output_file.write(f"{article_id},{article_language},{article_type},\"{article_title}\",{new_slug}\n")
    output_file.close()
    return

###############################################################################
#
# get_slug_version
#
# Retrieves the slug version to append from the command line arguments.
#
def get_slug_version(args):
    if len(args) <= 2:
        print("ERROR: Must provide a slug version to append (e.g. 'v7-12')\n")
        quit()
    return args[2]

###############################################################################
###############################################################################
###                           MAIN CODE                                     ###
###############################################################################
###############################################################################


# Make sure we can open the slug update file first
input_file = get_input_file(sys.argv)
new_slug_version = get_slug_version(sys.argv)
output_file_name = input_file.name + new_slug_version + ".csv"
edit_slugs(input_file, new_slug_version, output_file_name)
print("Output file: " + output_file_name)
print("")