# -*- coding: utf-8 -*-
"""
Created on Sat Nov 21 18:09:43 2020

@author: Mikes_Surface2
"""



from networks import network_construction
from forks import Fork_Network

fn = Fork_Network(True)

fork_net = network_construction(False,fn.fork_list,("repo_org","forker_org"),"fork_networkx")

fork_net.draw_network()
deg = fork_net.return_degrees()

