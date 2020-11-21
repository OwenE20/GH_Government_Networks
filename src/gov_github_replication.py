# -*- coding: utf-8 -*-
"""
Created on Thu Nov  5 10:54:41 2020

@author: Mikes_Surface2
"""

#Recreating results from gov social coding paper
"""
__________________________________________
______DEPRICATED PLANNING/SKETCH DOC______
__________________________________________


API should be the same as it was 5 years ago: apples-to-apples results
-TODO: look at the perils paper to make any adjustments


Overall Q: how have efforts of open government data and software changed within
the last 5 years?

-Do we see a clear abandonment of certain projects and/or a ramp up in others?
-Do we see a dropoff in unique users contributing to these projects?
    -Perhaps a protest of civic coders and involvement with a Trump government
-Does the structure of fork and pull networks looks fundamentally different?
-Do member contributions looks fundamentally different than 

Paper looks at behaviors of certain organizations: do we look at members of that org?

1. get all gov orgs from https://github.com/digitalgov/code-gov-github-metrics/blob/master/government-wide-repo-metrics/agencies-full.json
 - note: verify type of org w/ .gov link in bio
2. go through repo list, determine fork at this step? - recreate fork network
 - also look at every pull request: open and closed
 - just have a big list of forks and pulls, w/ variables on repo, org, user, etc.
     i.e. long dataset, follow tidy procedures
  - make sure to document time
3.


import pandas as pd

import urllib
import requests
import json
import pickle

with urllib.request.urlopen("https://raw.githubusercontent.com/digitalgov/code-gov-github-metrics/master/government-wide-repo-metrics/agencies-full.json") as url:
    data = json.loads(url.read().decode())
org_list = []
for org in data.items():
    org_list.extend(org[1])
    
org_dept = dict()

for dept in data.keys():
    orgs = data[dept]
    for org in orgs:
        org_dept[org] = dept
    


#%%

headers = headers = {"Authorization": "token "}
fields_of_interest = ("owner","fork","forks_count",
                      "created_at","pushed_at","updated_at",
                      "pulls_url")

#hard coding this rn
exclude = set(["usinterior",])


#could just save url for field of interest, append pagination info

def get_org_repos(dept_org_dict, fields):
    
    takes in dept_org_dict: dict w/ department keys, github org values
    return df with every repo for every org as an observation

    query = "https://api.github.com/orgs/{0}/repos?page={1}&per_page=100"
    
    #turn result into df?
    col_list = ["repo_name","department"]
    col_list.extend(fields)
    result = pd.DataFrame(columns=col_list)
    
    for department in dept_org_dict.keys():
        for org in dept_org_dict[department]:
            page_results = iterate_pages(query,org) 
            
            try:
                result = result.append(format_observations(page_results,
                                                           department,
                                                       fields),
                                       ignore_index = True)
            except Exception as e:
                print(e)
                print(f"broke at: {org}")
                pass
            
    save_results(result,"dept_repo_df")
    return result
    
         
            
def iterate_pages(query, *args):
    result = []
    empty = False
    page = 1
    #print("Working on query: {0}".format(args[0]))
    # Will need to sample and/or limit to not go over cap
    if(args[0] not in exclude):
        new_result = []
        while not empty:
            #args[0] is temporary
            if(args[0] != None):
                try:
                    payload = query.format(args[0])
                    print(payload)
                    new_result = requests.get(payload, page, 
                                              headers=headers,
                                              timeout = 5).json()
                except Exception as e:
                    print(e)
                    pass
            else:
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
    
    
    result = []
    for repo in page_result:
        repo_data = []
        
        
        for field in fields:   
            print(field)
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
    
    pull_data = []
    if call_type == "pull": pull_data.append(page_result["user"]["login"])    
    elif call_type == "fork": pull_data.append(page_result["owner"]["login"]) 
    
    for field in fields:
        try:
            if(":" in field):
                cut_field = field.split(":")
                pull_data.append(page_result[cut_field[0]][cut_field[1]])
            
            else:
                pull_data.append(page_result[field])
                
        except KeyError:
            print(f"field not workin {field}")
            print(page_result["url"])

    return pull_data

#This is a little costlly, may want to sample?
# May want to think about this different: look at all gov. collaborators,
#look and see at the pulls they make, keep track of pull requests to other orgs.    

def get_pull_records(org_df, pull_fields):
    
    result = []
    for index, repo in org_df.iterrows():
        print(f"working on:{index}",flush=True)
        try:
            
            #data for owner, dept, name
            atts = [repo["repo_name"], repo["department"], repo["owner"]]
            url = repo["pulls_url"]
            query = url.replace("{/number}","")
            
            query += "?state=all&per_page=100&page={}"
            repo_pulls = iterate_pages(query,None)
            
            #If I want to add info about commit adds/dels, I can filter users
            #at this step
            for pull in repo_pulls:
                pull_data = []
                pull_data.extend(format_links(pull,pull_fields,"pull"))
                pull_data.extend(atts)
                result.append(pull_data)
        except Exception as e:
            print(f"BROKE AT {repo}")
            print(e)
            pass
            

    #hard coded for rn
    col_names = ['author'] + pull_fields
    col_names.extend(["repo_name","department","owner"])
    df = pd.DataFrame(data = result,
                      columns = col_names)
    
    save_results(df,"pull_requests_df")
    
    
    return df




This is a really dumb way of doing this:
-could recursively walk through network
- could just look at the origniators of government forks







def get_fork_records(forked_repos_df,pull_fields):
    
    
    Parameters
    ----------
    forked_repos_df: dataframe of all government agency repos that are forked
    
    pull_fields: a list of fields from the api call that we want to look at
    

    Returns
    -------
    
    
    
    
   
    
    
    result = []
    
    
    for index,repo in forked_repos_df.iterrows():
        name = repo["repo_name"]
        print(f"working on:{name}",flush=True)
        try:
            
            #data for owner, dept, name
            
            forker = repo["owner"]
            atts = [name, repo["department"], forker]
           
            query = "https://api.github.com/repos/{0}/{1}"
            query = query.format(forker,name)
            page_result = requests.get(query, 
                                      headers=headers,
                                      timeout=5).json()
           
            parent = page_result["parent"]["owner"]["login"]
            
            if parent in org_list:
                parent_dept = org_dept[str(parent)]
                atts.extend([parent,parent_dept])
                pull_data = []
                pull_data.extend(format_links(page_result,pull_fields,"fork"))
                pull_data.extend(atts)
                result.append(pull_data)
            else:
                pass
            
            
        except Exception as e:
           print(f"BROKE AT {repo}")
           print(e)
           pass
        
                
    col_names = ['forker'] + pull_fields
    col_names.extend(["repo_name","department","owner","parent","parent_dept"])
    df = pd.DataFrame(data = result,
                      columns = col_names)
    
    save_results(df,"forks_df")
    
    
    return df
                


#Note: more specific details about the pull contents can be found by going through
#commit pull url itself

pull_fields = ["title","state","created_at","updated_at",
               "merged_at", "author_association", "user:organizations_url"] 

a = load_results("dept_repo_df")
test = a[a["fork"] == True]

fork_fields = ["watchers_count","created_at","updated_at","pushed_at"]

forks = get_fork_records(test, fork_fields)
 




#need a more thought out sampling scheme
#b = get_pull_records(sample, pull_fields)



b = load_results("pull_requests_df")


inter_agency_pulls = b[b["author"] in org_list]



#def get pulls: get a df with all pulls from every df
#same thing w/ forks?
#how to do collaborators: maybe create a set of collabs from a top level org_df
#create network on different df, pass values from fork and pull dfs to networkx graph?



# query for pulls: GET /repos/:owner/:repo/pulls
#@doc https://developer.github.com/v3/pulls/#list-pull-requests

"""
