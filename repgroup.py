# -*- coding: utf-8 -*-
from rtshell import rtconf


class ReplicaGroup:
    #The group of components which share same config parameter "group_name"
    #This class manages members of groups and thier primary components state 
    
    def __init__(self, name):
        self.name              = name
        self.comp_dic          = {}
        self.primary_conns     = None     
        
        self.current_primary = None
    
        self.primary_state = {}
    
    def find_primary_comp(self):
        #Set the smallest priority component as a current primary comp
        self.current_primary = self.comp_dic[min(self.comp_dic.keys())]
        
    def load_primary_state(self):
        
        for conf in self.current_primary.configuration_sets[0].configuration_data:
            self.primary_state[conf.name] = conf.data
    
    def find_next_primary(self):
        #Exclude the old primary comp and set new primary comp
        self.comp_dic.pop(min(self.comp_dic.keys()))
        self.current_primary = self.comp_dic[min(self.comp_dic.keys())]            
        return self.current_primary               
        
    def switch_next_primary(self):
        #Assumption that primary comp and replicate comps have same ports
        #Switch connection source from old primary to new primary 
        try:
            for conn in self.primary_conns:
                conn.change_source_comp(self.current_primary)
        except:
            print('connecting error')
            return 0
        
        return 1
        
    def set_state_for_reps(self,t):
        #Broadcast the states of primary to replicates
        for k in self.comp_dic.keys():
            if not k == min(self.comp_dic.keys()):
                for param, value in self.primary_state.iteritems():
                    arg = [self.comp_dic[k].path_uri, "set", param.lstrip(), value]
                    rtconf.main(argv=arg,tree = t)
                    #print self.comp_dic[k].properties['naming.names']+" conf update"
                    
