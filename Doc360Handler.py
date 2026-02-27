#
#  config_reader.py
#  Slugfest2
#
#  Created by Colby Dyess on 2/26/26.
#
import json
import sys
import os.path
import csv
import requests
import time        # Basic delay method to avoid rate limits (100 / min) Dumb, but functional

standard_headers =  { 'api_token': '',
                      'Accept': 'application/json'
                    }

project_version_id="NONE"

###############################################################################
#
# read_slug_config
#
# Reads company specific settings from a config file so it's not stored in
# code. Accepts a filename, but will default to ".config" if none provided.
#
def loadConfig(*args):
    file_name=".config"
    config_dict=""
    if len(args)>0:
        file_name=args[0]
    if os.path.exists(file_name):
        try:
            config_dict=json.load(open(file_name))
        except:
            raise ValueError("Unable to read config file ["+ file_name + "].")
    else:
        raise ValueError("Config file ["+ file_name + "] does not exist.")
    return config_dict



###############################################################################
#
# CLASS:   Handler
#
class Handler:
    api_token=""
    standard_headers =  { 'api_token': '',
                          'Accept': 'application/json'
                        }
    project_version_id=""
    base_url = "https://apihub.us.document360.io/v2"
    versions_url = base_url + "/ProjectVersions"
    articles_url = base_url + "/Articles"
    category_url = base_url + "/Categories"
    project_version_id=""             #AppGate ZTNA Doc project ID - This contains the target bookset
    project_english_version_id=""     #AppGate ZTNA Doc Version ID (English)
    
    def __init__(self, file_name=".config"):
        config=loadConfig(file_name)
        self.project_version_id=config['project_version_id']
        self.api_token=config['api_token']
        self.project_english_version_id=config['project_english_version_id']
        self.standard_headers={ 'api_token': self.api_token,
                                'Accept': 'application/json'
                                }
        return

    def get_bookset(self):
        request_url = self.versions_url + "/" + self.project_version_id + "/categories?excludeArticles=false&langCode=en&includeCategoryDescription=false"
        try:
            response = requests.get(request_url, headers=self.standard_headers)
        except:
            raise ValueError("ERROR: Unable to retrieve bookset. Is the API token valid?" )
        if response.status_code!=200:
            raise ValueError("ERROR: HTTP return code (%d) indicates an issue" % (response.status_code))
        data = json.loads(json.dumps(response.json()))
        return data


    ###############################################################################
    #
    # update_article_slug
    #
    # Updates the specified article with the given slug value.
    #
    def update_article_slug(self, article_id, article_lang, article_slug):
        update_url = self.articles_url + "/" + article_id + "/" + article_lang + "/settings"
        request_data = {'slug' : article_slug }
        response = requests.put(update_url, json=request_data, headers=standard_headers)
        time.sleep(0.7)
        return


    ###############################################################################
    #
    # update_category_slug
    #
    # Updates the specified category with the given slug value.
    #
    def update_category_slug(self, category_id, category_lang, category_slug):
        update_url = self.category_url + "/" + category_id + "/" + category_lang + "/settings"
        request_data = {'slug' : category_slug }
        response = requests.put(update_url, json=request_data, headers=standard_headers)
        time.sleep(0.7)
        return

