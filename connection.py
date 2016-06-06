# -*- coding: utf-8 -*-
import sys
from rtshell import rtcon
from rtshell import rtdis


class Connection(object):
    #Connection data set    
        
    def source_comp_path(self):
        return self.__source_comp_path
    
    def source_port_name(self):
        return self.__source_port_name
    
    def target_comp_path(self):
        return self.__target_comp_path
    
    def target_port_name(self):
        return self.__target_port_name
    
    def disconn_target_comp(self, comp_path):
        #diservice_connect all connection
        tmp = sys.argv
        sys.argv = [sys.argv[0], comp_path]
        try:
            rtdis.main()
        except:
            print "failed disconnection: " + str(comp_path)
        print "succeeded disconnection"
        sys.argv = tmp
        
                
class DataFlowConnection(Connection):
    #Data flow connection
    
    def __init__(self, source_comp_path, source_port_name, target_comp_path, target_port_name,
                  data_flow_type,subscription_type):
        self.__source_comp_path   = source_comp_path
        self.__source_port_name   = source_port_name
        self.__target_comp_path   = target_comp_path 
        self.__target_port_name   = target_port_name
        self.__data_flow_type     = data_flow_type
        self.__subscription_type  = subscription_type
    
    def data_flow_type(self):
        return self.__data_flow_type
    
    def subscription_type(self):
        return self.__subscription_type
    
    def check_port_name(self, comp):
        #If the component have same name port, return True
        for p in comp.data_ports:
            if self.__source_port_name ==  p._name.split(".")[1]:
                return True
        return False
    
    def change_source_comp(self, new_src):
        #Previous component and new component should have same name port
        if not self.check_port_name(new_src):
            return 0        
        
        self.disconn_target_comp(self.__source_comp_path)
        self.__source_comp_path = new_src.path_uri
        
        arg=[self.__source_comp_path + ":" + self.__source_port_name,
            self.__target_comp_path + ":" + self.__target_port_name]#,
            #"-p", "dataport.dataflow_type=%s" % self.__data_flow_type,
            #"-p", "dateport.subscription_type=%s" % self.__subscription_type]
        try:    
            rtcon.main(argv=arg, tree=None)
        except:
            print "failed connect: " + arg
        print "succeeded disconnection"

class ServicePortConnection(Connection):
    #Service port connection
    
    def __init__(self, source_comp_path, source_port_name, target_comp_path, target_port_name):
        self.__source_comp_path   = source_comp_path
        self.__source_port_name   = source_port_name
        self.__target_comp_path   = target_comp_path 
        self.__target_port_name   = target_port_name    
    
    def check_port_name(self, comp):
        #If the component have same name port, return True
        for p in comp.service_ports:
            if self.__source_port_name ==  p._name.split(".")[1]:
                return True
        return False
    
    def change_source_comp(self, src_comp):
        #Previous component and new component should have same name port
        if not self.check_port_name(src_comp):
            return 0
        
        self.disconn_target_comp(self.__source_comp_path)
        self.__source_comp_path = src_comp.path_uri
        
        arg = [self.__source_comp_path + ":" + self.__source_port_name,
               self.__target_comp_path + ":" + self.__target_port_name]
        
        rtcon.main(argv=arg, tree=None)
