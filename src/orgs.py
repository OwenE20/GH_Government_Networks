# -*- coding: utf-8 -*-
"""
Created on Sun Nov 15 16:21:34 2020

@author: Mikes_Surface2
"""

import utils
import pandas as pd

class GovernmentOrganiations:
    
    """
    Class to source and store the data on government-affiliated Github
    Organizations.
    
    """
    
    
    def __init__(self):
        
        fields_of_interest = ("owner","fork","forks_count",
                      "created_at","pushed_at","updated_at",
                      "pulls_url")
        
        
        #list of organizations in utils.data is in dept:[org] form,
        #this loop unpacks that into a dict with org:dept to get the department
        #value given a org key
        data = utils.data
        self.org_dept = dict()
        for dept in data.keys():
            orgs = data[dept]
            for org in orgs:
                self.org_dept[org] = dept
                
        self.org_repos = utils.load_results("dept_repo_df")
    
    def get_org_list(self):
        org_list = []
        for org in utils.data.items():
            org_list.extend(org[1])
        return org_list
        

    def org_dep_lookup(self,org):
        return self.org_dept[org]

    def get_org_repos(self,dept_org_dict, fields):
        """
        takes in dept_org_dict: dict w/ department keys, github org values
        return df with every repo for every org as an observation
        """
        query = "https://api.github.com/orgs/{0}/repos?page={1}&per_page=100"
        
        #turn result into df?
        col_list = ["repo_name","department"]
        col_list.extend(fields)
        result = pd.DataFrame(columns=col_list)
        
        for department in dept_org_dict.keys():
            for org in dept_org_dict[department]:
                page_results = utils.iterate_pages(query,[org,]) 
                
                try:
                    result = result.append(utils.format_observations(page_results,
                                                               department,
                                                           fields),
                                           ignore_index = True)
                except Exception as e:
                    print(e)
                    print(f"broke at: {org}")
                    pass
                
        utils.save_results(result,"dept_repo_df")
        return result
    
    
gc = GovernmentOrganiations()