#!/usr/bin/env python
# coding:utf-8
import rtctree.tree
import rtctree.path

class Synchronizer:
    #Managing synchromization of components internal states between primary comp and rep comps
    
    def __init__(self):
        self.__repgroups = []
        
    def set_repgroups(self, groups):
        self.__repgroups = groups
    
    def conf_changed(self, node, value, cb_args):
        #Definition of the call back function
        #node:Rep1.rtc, value:('tlin.5', 'UPDATE_CONFIG_PARAM')
        if value[1] == 'UPDATE_CONFIG_PARAM':
            for group in self.__repgroups:
                if group.current_primary.properties['naming.names'] == node.name:
                    #value[0]=[conf name].[value]
                    group.primary_state[value[0].split('.')[0]] = value[0].split('.')[1]
                group.set_state_for_reps(self.__tree_dic[node.name])
                
    def set_observed_comp(self, callback, comp):
        #Set observed nodes
        path, port = rtctree.path.parse_path("/" + comp.path_uri)
        t = rtctree.tree.RTCTree(paths=path)
        self.__tree_dic[comp.properties['naming.names']] = t
        self.__nodes.append(t.get_node(path))     
        self.__nodes[-1].add_callback('config_event', callback)
        self.__nodes[-1].dynamic = True
        
            
    def start_obs(self):
        #Set nodes and trees and attach call back
        self.__nodes = []
        self.__tree_dic = {}
        
        for group in self.__repgroups:
            self.set_observed_comp(self.conf_changed, group.current_primary)
        
        print "start observation"
    
    def stop_obs(self):
        self.__nodes = []
        self.__tree_dic = {}
