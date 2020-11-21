# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 10:11:33 2020

@author: Mikes_Surface2
"""

#NETWORK WRAPPER CLASS, look at what data can be included in networkx graphs
#Look at paper for details on construction
#Look at extractable adjaceny matrix and other general data that may be useful in R


import networkx as nx
import utils
import matplotlib.pyplot as plt
import pandas as pd

class network_construction:
    """
    Wrapper class for networkx functionality
    
    """
    
    
    def __init__(self, built, connections_df, edge_labels,net_name):
        if not built:

            #node names to index the Series values
            self.frm_nodename, self.to_nodename = edge_labels
            self.net = self.build_network(connections_df)
            utils.save_results(self.net, net_name)
        else:
            self.net = utils.load_results(net_name)

    def build_network(self,connections_df):
        """
        Parameters
        ----------
        connections_df : dataframe
            Dataframe that contains relevant network data that can be construded
            as edges between nodes
        edge_labels : tuple of two strings
            The lables of the columns that will be denoted as an edge e.g.
            "forker_department" and "repo_dept": first passed label will be the
            node from which the directed edge will be pointed towards the other node
            
        #possibly add fields we want to encode into the field
        
        Returns
        -------
        networkx graph object

        """
        network = nx.MultiDiGraph()
        
        for index,edge in connections_df.iterrows():
            from_node = edge[self.frm_nodename]
            to_node = edge[self.to_nodename]
            if(from_node != to_node):
                network.add_edge(from_node,to_node)
        
        return network

    def draw_network(self):
        """
        Wrapper class for networkx draw function
        inline with reolicateing paper, make node size proportional to in degree

        Returns
        -------
        prints image of graph

        """
        
        d = [{k:v} for k, v in self.net.degree()]
        degrees = dict()
        for pair in d:
            degrees.update(pair)
        
        
        nx.draw(self.net, nodelist=list(degrees.keys()), 
                node_size= list(degrees.values()),
                with_labels=True,
                pos= nx.circular_layout(self.net))
        plt.show()
        
    def return_degrees(self):
        in_degree = dict(self.net.in_degree)
        out_degree = dict(self.net.out_degree)
        
        df = pd.DataFrame.from_dict(in_degree,orient = "index", columns=["in_degree"])
        df["out_degree"] = out_degree.values()
        return df
            
            
        
        