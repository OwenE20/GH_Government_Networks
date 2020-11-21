# -*- coding: utf-8 -*-
"""
Created on Sun Nov 15 16:14:08 2020

@author: Mikes_Surface2
"""



import traceback
import utils
from orgs import GovernmentOrganiations
import pandas as pd

class Government_Collaborators:
    """
    Class that manages the acquiring and storing of government-affiliated
    users on Github
    
    """
    
    def __init__(self,built):
        
        self.go = GovernmentOrganiations()
        fields = ["login","url"]
        
        if(not built):
            indivs = self.construct_individuals(fields)
            cols = ["agency","department"]
            cols.extend(fields)
            gov_members = pd.DataFrame(indivs,columns = cols) 
            
            utils.save_results(gov_members,"government_developers")
        
            
    
    def construct_individuals(self,fields):
        """

        Parameters
        ----------
        fields : tuple
        fields of the API response that we want to record

        Returns
        -------
        users : List
        list of user lists that contain ids and field attributes

        """
        
        org_list = self.go.org_dept
        query = "https://api.github.com/orgs/{0}/public_members?per_page=100&page={1}"
        users = []
        for org in org_list.keys():
            try:
                query_result  = utils.iterate_pages(query, [org,])
            except:
                traceback.print_exc() 
            
            print(len(query_result))
            for result in query_result:
                user = []
                user.append(org)
                user.append(self.go.org_dep_lookup(org))
                for field in fields:
                    user.append(result[field])
                    
                users.append(user)
        return users
                    
                
    def get_members(self):
        return utils.load_results("government_developers")
        

gc = Government_Collaborators(True)
        

