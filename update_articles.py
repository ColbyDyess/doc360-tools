#
#  update_articles.py
#
#  Created by Colby Dyess on 03/05/2026.
#
#  Updates slugs used within articles. This is intended to be used in conjunction
#  with edit_slugs.py, which generates a file with the new slug values.
#
#
import sys
import os.path
import csv
import Doc360Handler
import re

FILE_OUTPUT_FAILS = "failures.log"
FILE_LOG = "update.log"

###############################################################################
#
# open_redirect_file
#
# Opens the file that contains redirect rules exported from Doc360. This is 
# used to identify which slugs have been changed and need to be updated within 
# articles.
#
def open_redirect_file(file_name="redirect-rule-list.csv"):
    # Check that the file exists
    if os.path.isfile(file_name):
        print("Read slug values from: " + file_name)
        return open(file_name,"r")
    else:
        print("ERROR: File '" + file_name + "' does not exist\n")
        quit()
    return

###############################################################################
#
# read_redirect_rules
#
# Reads the redirect file and builds a mapping of old slugs to new slugs. This
# is used to identify which internal links within articles need to be updated.
# Returns a set of old and new slug pairs.
#
def read_redirect_rules():
    redirect_mapping = {}
    reader = csv.reader(open_redirect_file())
    next(reader)  # Skip header
    for row in reader:
        old_slug = row[0].strip()
        new_slug = row[1].strip()
        redirect_mapping[old_slug] = new_slug
    return redirect_mapping


###############################################################################
#
# read_article_list
#
# Opens the file that contains list of articles to update.
#
def read_article_list(args):
    # Make sure we got at least one parameter beyond the python command
    if len(args)<=1:
        print("ERROR: Must provide a file to read\n")
        quit()
    # Check that the file exists
    if os.path.isfile(args[1]):
        print("Read article list from: " + args[1])
        reader = csv.reader(open(args[1],"r"))
        next(reader)  # Skip header
        return reader

    else:
        print("ERROR: File '" + args[1] + "' does not exist\n")
        quit()
    return


###############################################################################
#
# get_internal_slugs
#
# Retrieves the list of internal links used within the specified article. This is
# used to identify which links need to be updated when slugs are changed. It
# takes in an HTML string and parses it for links that match the internal link
# format and returns that list.
#
# Eaxmple internal slug reference: href="/v1/docs/sites-1"
#
def get_internal_slugs(content):    
    pattern = r'href="/v1/[^"]+"'
    matches = re.findall(pattern, content)
    slugs = [match[6:-1] for match in matches]
    return slugs
    

###############################################################################
#
# build_slug_mapping
#
# Takes in a list of internal slugs and returns a dictionary mapping the old 
# slug to the new slug. This is used to update internal links within articles
# after slugs have been changed.
#
def build_slug_mapping(slugs, redirect_rules):
    slug_set = set(slugs)  # Remove duplicates
    slug_mapping = {}
    for slug in slug_set:
        part = slug[8:]
        anchor_index = part.find("#")
        if anchor_index != -1:
            part = part[:anchor_index]
        new_slug = "/v1/docs/" + redirect_rules[part]
        if anchor_index != -1:
            new_slug += "#" + slug.partition("#")[2]
        if new_slug:
            slug_mapping[slug] = new_slug
    return slug_mapping

###############################################################################
#
# update_internal_slugs_using_redirect_rules
#
# Takes in an article's content, extracts the internal slugs, calculates the
# new slugs, then updates the article content with the new slugs.
# It returns the updated content as a string.
#
def update_internal_slugs_using_redirect_rules(content):
    internal_slugs = get_internal_slugs(content)
    redirect_rules = get_redirect_rules()
    slug_mapping = build_slug_mapping(internal_slugs, redirect_rules)
    updated_content = content
    for old_slug, new_slug in slug_mapping.items():
        updated_content = updated_content.replace(f'href="{old_slug}"', f'href="{new_slug}"')
    return updated_content


###############################################################################
#
# build_internal_slug_mapping
#
# Takes in a list of internal slugs, then checks to see if it's internal slug
# is consistent with the target version. If not, it calculates the new slug and
# returns a dictionary mapping the old slug to the new slug.
#
def build_internal_slug_mapping(slugs, version):
    slug_set = set(slugs)  # Remove duplicates
    slug_mapping = {}
    for slug in slug_set:
        part = slug[8:]
        anchor_index = part.find("#")
        if anchor_index != -1:
            part = part[:anchor_index]
        if part.endswith(version):
            continue
        
        new_slug = "/v1/docs" + set_slug_version(part, version)
        
        if anchor_index != -1:
            new_slug += "#" + slug.partition("#")[2]
        if new_slug:
            slug_mapping[slug] = new_slug
    return slug_mapping

###############################################################################
#
# set_slug_version
#
# Appends or replaces a version suffix on a slug string.
# If the slug already ends with a version-like string (v-<int>-<int>),
# that suffix is replaced with the given version. Otherwise, the version
# is appended.
#

def set_slug_version(slug: str, version: str) -> str:
    # Strip a trailing version string and its preceding dash (if any).
    base = re.sub(r'-?v-?\d+-\d+(?:-\d+)?$', '', slug)
    base = re.sub(r'-\d', '', base)

    if base:
        return f"{base}-{version}"
    else:
        # slug was entirely a version string; return just the new version
        return version


###############################################################################
#
# clean_image_links
#
# Takes in an article's content and updates image links to remove the query
# parameters. This is required because when downloading the content, Doc360
# appends query parameters to image links that break the preview function.
def clean_image_links(content):
    pattern = r'src="([^"]+)"'
    matches = re.findall(pattern, content)
    updated_content = content
    for match in matches:
        if "?" in match:
            clean_link = match.split("?")[0]
            updated_content = updated_content.replace(f'src="{match}"', f'src="{clean_link}"')
    return updated_content

###############################################################################
#
# update_internal_content
#
# Takes in an article's content, extracts the internal slugs, determine if
# current slug is consistent with the target version, then updates the article
# content wi th the new slugs.
#
def update_internal_content(content, version):
    updated_content = content
    internal_slugs = get_internal_slugs(content)
    # Only update slugs if there are internal slugs and at least one slug is inconsistent with the target version.
    if(internal_slugs):
        slug_mapping = build_internal_slug_mapping(internal_slugs, version)
        for old_slug, new_slug in slug_mapping.items():
            updated_content = updated_content.replace(f'href="{old_slug}"', f'href="{new_slug}"')
    # Clean image links to remove query parameters that break the preview function in Doc360.
    cleaned_content = clean_image_links(updated_content)
    return cleaned_content

###############################################################################
#
# validate_command_line
#
def validate_command_line(args):
    if len(args) != 3:
        print("ERROR: Incorrect number of arguments.\nUsage: python update_articles.py <article_list_file.csv> <target_version>")
        quit()

    version_pattern = r'^v\d+-\d+$'
    if not re.match(version_pattern, args[2]):
        print("ERROR: Target version must be in the format 'vXX-YY' (e.g. 'v7-12').")
        quit()
    return

###############################################################################
#
# update_category
#
def update_category(category_id, category_lang, version, handler):
    # get the category data to check if the slug needs to be updated
    category_data = handler.get_category(category_id, category_lang)
    category_slug = category_data['slug']

    new_slug = set_slug_version(category_slug, version)
    if new_slug == category_slug:
        return  # Slug is already consistent with target version, no update needed

    try:
        handler.post_category_slug(category_id, category_lang, new_slug)
    except Exception as error:
        print(f"Failed to update category slug for category '{category_id}': {error}")


###############################################################################
###############################################################################
###                           MAIN CODE                                     ###
###############################################################################
###############################################################################

# Make sure command line is valid
validate_command_line(sys.argv)

# Get a doc360 handler to push updates
try:
    doc_handler=Doc360Handler.Handler()
except Exception as error:
    print(error)
    sys.exit(1)

# Read in the list of articles to update
article_list = read_article_list(sys.argv)

# Read the target version string. (e.g. "v7-12")
version = sys.argv[2] # Target version to update internal slugs to. 

# Open a log file to track which articles were successfully updated and which failed.
f_log = open(FILE_LOG, "w")

# Initialize some variables to use below.
count_success = 0
count_fail = 0
list_of_failed_articles = {}

# Loop through the list of articles and update the internal slugs within each article's content
for article in article_list:
    status_text = None
    # print "." for each article to show progress since this can take a while
    sys.stdout.write(".")
    sys.stdout.flush() 
    #id,language,type,title,slug
    article_id = article[0]
    article_lang = article[1]
    article_type = article[2]
    article_title = article[3]
    article_slug = article[4]
    status_text = f"'{article_id}','{article_title}'"
    
    if article_type == "c": # only update categories, not articles
        try:
            update_category(article_id, article_lang, version, doc_handler)
            count_success += 1
            f_log.write(status_text+",success\n")
        except Exception as error:
            f_log.write(status_text+",fail\n")
            count_fail += 1
            list_of_failed_articles.update({article_id: []})
            list_of_failed_articles[article_id].append(article_title)
            list_of_failed_articles[article_id].append("https://portal.us.document360.io/e7482ce5-acfa-4c3b-b76c-b6c32472644a/document/v1/category/%s/en" % (article_id))
            list_of_failed_articles[article_id].append(str(error))
            continue

    if article_type=="a": # only update articles, not categories
        article_data = doc_handler.get_article(article_id, article_lang)
        new_article ={}
        new_article['id'] = article_id
        new_article['language'] = article_lang
        new_article['content'] = update_internal_content(article_data['html_content'], version)
        new_article['slug'] = set_slug_version(article_data['slug'], version)
        try:
            doc_handler.post_article_content(new_article)
            doc_handler.post_article_slug(new_article)
            f_log.write(status_text+",success\n")
            count_success += 1
        except Exception as error:
            f_log.write(status_text+",fail\n")
            count_fail += 1
            list_of_failed_articles.update({article_id: []})
            list_of_failed_articles[article_id].append(article_title)
            list_of_failed_articles[article_id].append("https://portal.us.document360.io/e7482ce5-acfa-4c3b-b76c-b6c32472644a/document/v1/view/%s/en" % (article_id))
            list_of_failed_articles[article_id].append(str(error))
            continue

print(f"\nFinished updating articles. Success: {count_success}, Fail: {count_fail}")
print(f"\tSuccess: {count_success}")
print(f"\tFail: {count_fail}")
if count_fail > 0:
    f = open(FILE_OUTPUT_FAILS, "w")
    for item in list_of_failed_articles:
        f.write(item+"\n")
        for detail in list_of_failed_articles[item]:
            f.write("\t" + detail + "\n")
    f.close()
    print(f"See '{FILE_LOG}' for details on which articles failed.")
f_log.close()
