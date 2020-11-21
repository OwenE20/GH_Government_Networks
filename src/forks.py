# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 10:11:14 2020

@author: Mikes_Surface2
"""

#CREATE FORK NETWORK 


import utils
from individuals import Government_Collaborators
from orgs import GovernmentOrganiations
import pandas as pd
import traceback

class Fork_Network:
    
    def __init__(self, built):
        fork_fields = ["watchers_count","created_at","updated_at","pushed_at"]
        gov_devs = Government_Collaborators(True).get_members()
        go = GovernmentOrganiations()
        self.org_list = go.get_org_list()
        self.org_dict = go.org_dept
        
        repos_df = go.org_repos
        repos_df = repos_df[repos_df["forks_count"] > 0]
        
        if(not built):
            self.fork_list = self.get_fork_records(repos_df,fork_fields,gov_devs) 
        else:
            self.fork_list = utils.load_results("forks_df")
            
        
    def get_fork_records(self,gov_repos,fork_fields,devs):
        
        """
        Parameters
        ----------
        gov_repos: dataframe of all government agency repos
        
        pull_fields: a list of fields from the api call that we want to look at
        
        devs: dataframe with developers in government organizations on github
    
        Returns
        -------
        
        a dataframe with details on every fork made by a government developer
    
        """
        
        devs_list = set(devs["login"])
        result = []

        for index,repo in gov_repos.iterrows():
            repo_name = repo["repo_name"]
            repo_owner = repo["owner"]
            repo_dept = repo["department"]
            
            print(f"working on:{repo_name}",flush=True)
            try:
                #first, get forks of a repo
                query = f"https://api.github.com/repos/{repo_owner}/{repo_name}/forks?per_page=100&page={{}}"
                
                forks = utils.iterate_pages(query,[None,])
                
                #second, iterate through forks, filter fork author, collect relevant deets
                for fork in forks:
                    fork_data = []
                    fork_author = fork["owner"]["login"]
                    if(fork_author in devs_list):
                        #add info about parent repo:
                        fork_data.extend([repo_name,repo_owner,repo_dept])
                        
                        #add info about forker affiliation:
                        #incase of duplicates, get first entry
                        forker_info = devs[devs["login"] == fork_author]
                        forker_dept = forker_info["department"].values[0]
                        forker_agency = forker_info["agency"].values[0]
                        fork_data.extend([fork_author,forker_dept,forker_agency])
                    
                        
                        #add field info
                        fork_data.extend(utils.format_links(fork,
                                                      fork_fields,"fork"))
                        #append to total results
                        result.append(fork_data)
                        
                        
                    elif(fork_author in self.org_list):
                        #add info about parent repo:
                        fork_data.extend([repo_name,repo_owner,repo_dept])
                        
                        forker_dept = self.org_dict[fork_author]
                        forker_agency = fork_author
                        fork_data.extend([fork_author,forker_dept,forker_agency])
                    
                        
                        #add field info
                        fork_data.extend(utils.format_links(fork,
                                                      fork_fields,"fork"))
                        #append to total results
                        result.append(fork_data)
                        
                        
                    else:
                        pass
                    
            except KeyboardInterrupt:
                print(f"stoped at {index}")
                utils.save_results(result,"forks_temp_list")   
            
            except Exception :
               print(f"BROKE AT {repo}")
               traceback.print_exc()
               pass
           
                    
        col_names = ["repo_name","repo_org","repo_dept",
                     "forker_name","forker_dept","forker_org","idk"]
        
        col_names.extend(fork_fields)
        df = pd.DataFrame(data = result,
                          columns = col_names)
        
        utils.save_results(df,"forks_df")
        
        
        return df
    
    """
    def get_network(fork_df,built):
        if not built:
            
        else:
  """      


fn = Fork_Network(True)

from networks import network_construction

fork_net = network_construction(False,fn.fork_list,("repo_org","forker_org"),"fork_networkx")

fork_net.draw_network()
deg = fork_net.return_degrees()


