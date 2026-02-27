#
#  get_slugs.py
#
#  Created by Colby Dyess on 12/16/25.
#
#  Generates a list of articles and their slugs based on the
#  specific bookset and version of interest.
#
#
import sys
import json
import Doc360Handler

output_file_name="articles.csv"
doc_handler=None

###############################################################################
#
# select_bookset
#
# This one lists the main categories (like: Introduction, AppGate ZTNA Guide,
# AppGate User Guide...) so user can select the bookset they want to update.
#
#
def select_bookset(doc_handler):
    data = doc_handler.get_bookset()    # as Doc360Handler object to get the list of books
    count = len(data)
    i = 1
    print("There are " + str(count) + " booksets")
    for category in data['data']:
       print(str(i) + ") " + category['name'])
       i += 1
    choice = int(get_option_number(count))-1
    print("")   # add line feed to make things easier to read
    return (select_bookset_version(data['data'][choice]))
 
###############################################################################
#
# select_bookset_version
#
# After selecting the bookset, the user then selects the specific version they
# want to update.
#
def select_bookset_version(data):
    category = json.loads(json.dumps(data))
    count = len(category)
    selected_data = json.loads("{}")
    data_array = [None] * 20    # Hardcoded array size is a bad idea, but quick to make it work
    i = 1
    # List top line folders which appear as folders
    for entry  in category['articles']:
       print(str(i) + ") " + entry['title'])
       data_array[i] = entry
       i += 1
    # List top line categories that appear as folders
    for entry in category['child_categories']:
        print(str(i) + ") " + entry['name'])
        selected_data = entry
        data_array[i] = entry
        i += 1
    choice = get_option_number(i-1)
    return data_array[int(choice)]

###############################################################################
#
# write_article_list
#
# Writes an entry for each article and all child articles & cateogires
#
def write_article_list(data, out_file):
    try:
        for entry  in data['articles']:
            article_id = entry['id']
            article_language = entry['language_code']
            article_title = "\"" + entry['title'] + "\""
            article_slug = entry['slug']
            out_file.write(format(article_id + "," + article_language + ",a," + article_title + "," + article_slug + "\n"))
            try:
                for category in entry['child_categories']:
                    write_child_categories(category, out_file)
            except:
                pass
    except:
        pass
    
    try:
        for category in data['child_categories']:
            write_child_categories(category, out_file)
    except:
        pass
        #print(f"An exception occurred: {e}")

    return

###############################################################################
#
# write_child_categories
#
# Writes the selected category and all child articles to the output file.
#
def write_child_categories(data, out_file):
    try:
        for entry  in data['child_categories']:
            entry_id = entry['id']
            entry_language = entry['language_code']
            entry_title = "\"" + entry['name'] + "\""
            entry_slug = entry['slug']
            out_file.write(format(entry_id + "," + entry_language + ",c," + entry_title + "," + entry_slug + "\n"))
            write_article_list(entry, out_file)
    except:
        return
    return

###############################################################################
#
# write_table_of_contents
#
# Writes the header to the output file.
#
def write_table_of_contents(data, out_file):
    write_child_categories(data, out_file)
    try:
        for entry  in data['child_categories']:
            name = entry['name']
    except:
        pass
    write_article_list(data, out_file)

    return

###############################################################################
#
#
#
def generate_article_list(data, file_name):
    header_string ="id,language,type,title,slug"
    f = open(file_name,"w")
    # Print out the table header
    f.write(header_string+"\n")
    write_table_of_contents(data, f)
    return

###############################################################################
#
# get_option_number
#
# Intended to be used after presenting the user with a list of options.
# This function will exit the application if the user chooses 'q' to quit.
#
def get_option_number(highest):
    choice = ""
    while choice=="" and choice!="q":
        print("Select from above or 'q' to quit")
        choice = input()
    if choice=="q" or choice=="Q":
        print("You selected 'quit'")
        sys.exit(0)  # Exits with success code
    return choice


###############################################################################
#
# print_usage
#
# Gives the user a hint about how to call this app.
#
def print_usage():
    print("Invoke this utility using this command")
    print("python3 " + configurationsys.argv[0] + " [config.file]")
    print("")
    print("config.file: The file containing configuration settings.")
    print("             Default file is .config")
    print("")
    return


###############################################################################
###############################################################################
###                           MAIN CODE                                     ###
###############################################################################
###############################################################################
try:
    doc_handler=Doc360Handler.Handler()
except Exception as error:
    print(error)
    sys.exit(1)
# prompt user to specify the bookset and version.
bookset = select_bookset(doc_handler)
# dump the category and articles for the selected bookset/version
output_file_name = bookset['name'] + ".csv"
generate_article_list(bookset, output_file_name)
print("Output file: " + output_file_name)
print()
