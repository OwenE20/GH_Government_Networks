# -*- coding: utf-8 -*-
"""
Created on Sun Nov 15 16:16:08 2020

@author: Mikes_Surface2

Module containing housekeeping functions needed for the rest of the project



"""

import pickle
import urllib
import json
import requests
import pandas as pd
import traceback
import os

with urllib.request.urlopen("https://raw.githubusercontent.com/digitalgov/code-gov-github-metrics/master/government-wide-repo-metrics/agencies-full.json") as url:
    data = json.loads(url.read().decode())

exclude = set(["usinterior",])
oauth = os.getenv('GHUB_OAUTH')
headers = {"Authorization": f"token {oauth}"}
            
def iterate_pages(query, args):
   """
   Function that passes the API query and loops through the pages, appending
   the results and returning a list with all of the call results

    Parameters
    ----------
    query : String
        the REST query to pass
    args : list
        arguments that need to be added to the query string

    Returns
    -------
    result : List
        A list of api results captured as dictionaries.
    """ 
    
    
    result = []
    empty = False
    page = 1
    if(args[0] not in exclude):
        new_result = []
        while not empty:
            #args[0] is temporary
            if(args[0] != None):
                #for current use, only passing one argument, format that argument
                #to any open fields in the string
                try:
                    
                    new_result = requests.get(query.format(args[0],page),
                                              headers=headers,
                                              timeout = 5).json()
                except Exception as e:
                    traceback.print_exc() 
                    pass
            else:
                #If there are no arguments, the only formatting is the page number
                try:
                        new_result = requests.get(query.format(page), 
                                              headers=headers,
                                              timeout=5).json()
                except Exception as e:
                    print(e)
            
            result.extend(new_result)
            if(len(new_result) == 0):
                empty = True       
            page += 1
    else:
        print("didn't run")
    return result


def format_observations(page_result,agency, fields):
    """
    @TODO: recode to make more usable
    
    
    Parameters
    ----------
    page_result : dict
        returned value of iterate_pages: should be a list w/ atts as the value
        atts is a dict with name:value pairs
    agency : str
        Just the name of the organization the repo belongs to so we can keep that
        information with other repo characteristics
    *fields :  tuple
        What atts from the dict values we want to keep.
    Returns
    -------
    Should return a df w/ columns for repo name, org, and relevant fields w/
    either values or other rest api urls
    """
    
    result = []
    for repo in page_result:
        repo_data = []
        
        repo_data.append(repo["name"])
        repo_data.append(agency)
        
        
        for field in fields:   
            try:
                #temporary hard coding 
                if(field == "owner" or field == "user"):
                    repo_data.append(repo[field]["login"])
                    
                else:
                    repo_data.append(repo[field])
                
            except:
                print(f"key not found {field}")
            
        result.append(repo_data)
        
    col_list = ["repo_name","department"]
    col_list.extend(fields)
    result_df = pd.DataFrame(result, columns=col_list)    

    return result_df

def format_links(page_result,fields,call_type):
    """
    

    Parameters
    ----------
    page_result : Dict
        A dict containing of the API call results
    fields : list of strings
        A list of fields we want to get from the API call: these are the keys
        of the relevant values in the page_result dict
    call_type : string
        Temporary work around for the two current use cases: only differs
        in the field names for the user name.

    Returns
    -------
    pull_data : list
        A list of values from the API call for that one result

    """
    
    
    
    pull_data = []
    if call_type == "pull": pull_data.append(page_result["user"]["login"])    
    elif call_type == "fork": pull_data.append(page_result["owner"]["login"]) 
    
    for field in fields:
        try:
            if(":" in field):
                #some dict values are dicts themselves, using field1:field2
                #to pass through a key to the second layer of dict
                cut_field = field.split(":")
                pull_data.append(page_result[cut_field[0]][cut_field[1]])
            
            else:
                pull_data.append(page_result[field])
                
        except KeyError:
            print(f"field not workin {field}")
            print(page_result["url"])

    return pull_data


def save_results(df, file_name):
    #@TODO: add some check for if the file is there
    #@TODO: change path to project/data
    #@TODO: multiple file types
    
    file_name = "{}.pickle".format(file_name)
    try:
        open(file_name, "x")
        with open(file_name, 'wb') as f:
            pickle.dump(df, f)
                
    except:
        with open(file_name, 'wb') as f:
            pickle.dump(df, f)
                
        
def load_results(file_name):
    
    file = "{}.pickle".format(file_name)
    try:
        with open(file, 'rb') as f:
            return pickle.load(f)
    except:
        return None
    
    