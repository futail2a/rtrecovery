#!/usr/bin/env python
# coding:utf-8
import rtsprofile.rts_profile
from repgroup import ReplicaGroup

from connection import DataFlowConnection as dfc
from connection import ServicePortConnection as spc


class RecoveryManager():
   """Managing replicated components groups

    :param __rtsp: RTSProfile
    :param __repgroups: List of ReplicaGroup
    """
    #
    def __init__(self, profile):
        """RecoveryManager should have one RTSystemProfile
        """
        with open(profile) as f:
            self.__rtsp = rtsprofile.rts_profile.RtsProfile(xml_spec = f)
        self.__repgroups = []
    
    def repgroups(self):
        """Setter of __repgrouops
        """
        return self.__repgroups
    
    def get_target_repgroup(self, name):
        """
        Return a same name of repgroup in self.__repgroups
        If there were not one, return None
        """
        for group in self.__repgroups:
            if group.name == name:
                return group
        return None
    
    def conf_getter(self, comp, conf_name):
        """
        Return configuration data named conf_name in the comp
        If it were not, return None
        """
        for cfg in comp.configuration_sets[0].configuration_data:
            if cfg.name == conf_name:
                return cfg.data
        return None
            
    def init(self):
        """
        Initialize repgoups
        Add repgroup to self.__repgroups in rtsp
        Components' configuration that named "group_name" are used
        """
        for c in self.__rtsp.components:
            g_name =  self.conf_getter(c, "group_name")
            if g_name:
                repgroup = self.get_target_repgroup(g_name)
                
                if repgroup:
                    repgroup.comp_dic[self.conf_getter(c, "priority")] = c

                else:
                    tmp = ReplicaGroup(g_name)
                    tmp.comp_dic[self.conf_getter(c, "priority")] = c
                    self.__repgroups.append(tmp)
        
        #Initialize each repgroup
        for repgroup in self.__repgroups:    
            repgroup.init()
            repgroup.primary_conns = self.extract_connected_ports(repgroup.current_primary)
    
    def find_comp_by_path(self, path):
        """
        Find a component from rtsp with a  path of the component
        """
        for c in self.__rtsp.components:
            #print c.path_uri
            if path == c.path_uri:
                return c
            
    def extract_connected_ports(self, comp):
        """
        Create a list of data that describe all comp's connection 
        """
        connected_ports = []
        
        #Data port
        for data_conn in self.__rtsp.data_port_connectors:
            #if "comp" is a target comp, source comp is a connection destination
            if comp.path_uri == data_conn.source_data_port.properties["COMPONENT_PATH_ID"]:
                connected_ports.append(dfc(data_conn.source_data_port.properties["COMPONENT_PATH_ID"],
                                           data_conn.source_data_port.port_name.split(".")[1],
                                           data_conn.target_data_port.properties["COMPONENT_PATH_ID"], 
                                           data_conn.target_data_port.port_name.split(".")[1],
                                           data_conn.data_flow_type,
                                           data_conn.subscription_type)
                                       )
            #If "comp" is a source comp, target comp is a connection destination     
            elif comp.path_uri == data_conn.target_data_port.properties["COMPONENT_PATH_ID"]:
                connected_ports.append(dfc(data_conn.target_data_port.properties["COMPONENT_PATH_ID"],
                                           data_conn.target_data_port.port_name.split(".")[1],
                                           data_conn.source_data_port.properties["COMPONENT_PATH_ID"], 
                                           data_conn.source_data_port.port_name.split(".")[1],
                                           data_conn.data_flow_type,
                                           data_conn.subscription_type)
                                       )
                
        #Service port
        for service_conn in self.__rtsp.service_port_connectors:
            if comp.path_uri == service_conn.source_service_port.properties["COMPONENT_PATH_ID"]:
                connected_ports.append(spc(service_conn.source_service_port.properties["COMPONENT_PATH_ID"],
                                           service_conn.source_service_port.port_name.split(".")[1],
                                           service_conn.target_service_port.properties["COMPONENT_PATH_ID"], 
                                           service_conn.target_service_port.port_name.split(".")[1]
                                           )
                                       )
            elif comp.path_uri == service_conn.target_service_port.properties["COMPONENT_PATH_ID"]:
                connected_ports.append(spc(service_conn.target_service_port.properties["COMPONENT_PATH_ID"],
                                           service_conn.target_service_port.port_name.split(".")[1],
                                           service_conn.source_service_port.properties["COMPONENT_PATH_ID"], 
                                           service_conn.source_service_port.port_name.split(".")[1]
                                           )
                                       )
        return connected_ports
    
    def recovery(self, fault_path):
        """
        Start recovery
        """
        fault_comp  = self.find_comp_by_path(fault_path)
        rep_group = self.get_target_repgroup(self.conf_getter(fault_comp, "group_name")) 
        if fault_comp != rep_group.current_primary:
		print "faulty comp is not primary comp"
		return 1
        
        rep_group.find_next_primary()            
                
        if rep_group.switch_next_primary():  
            return 0
                
