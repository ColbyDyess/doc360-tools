#
#  update_slugs.py
#
#  Created by Colby Dyess on 12/17/25.
#
#  Takes in a file that has all the articles and their target slugs.
#
#
import sys
import os.path
import csv
import Doc360Handler

doc_handler=None
    
    
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
# update_articles
#
# Takes in a csv file that contains all the updated slugs.
# The file must follow the very specific format, or things'll break.
#
def update_articles(in_file, handler):
    csvFile = csv.reader(in_file)
    # skip the header
    next(csvFile)
    for lines in csvFile:
        update_slug(lines, handler)
    return


###############################################################################
#
# update_slug
#
# Updates an individual article. This function is intended to be
# called by update_articles()
#
def update_slug(data, handler):
    article_id = data[0]
    article_lang = data[1]
    article_type = data[2]
    article_title = data[3]
    article_slug = data[4]
    response = None
    
    # Call different endpoints based on record type
    if article_type == 'a':
        handler.update_article_slug(article_id, article_type, article_slug)
    elif article_type == 'c':
        handler.update_category_slug(article_id, article_type, article_slug)
    return



###############################################################################
###############################################################################
###                           MAIN CODE                                     ###
###############################################################################
###############################################################################


# Make sure we can open the slug update file first
input_file = get_input_file(sys.argv)

# Get a doc360 handler to push updates
try:
    doc_handler=Doc360Handler.Handler()
except Exception as error:
    print(error)
    sys.exit(1)
    
# Update each article
print("Updating slugs.....")
update_articles(input_file, doc_handler)
