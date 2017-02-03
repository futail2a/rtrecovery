# -*- coding: utf-8 -*-
import recoverymanager
import synchronizer
import sys
import time

if __name__ == '__main__':
    if len(sys.argv) != 2:
	print "plese pass a name of a xml file to the argument"
        sys.exit()
        #rm = recoverymanager.RecoveryManager("TestRepGroup.xml")

    rm = recoverymanager.RecoveryManager(sys.argv[1])

    sync = synchronizer.Synchronizer()
    sync.set_repgroups(rm.get_repgroups())

    while True:
        sync.start_obs()
        print 'Input Fault Component Path'
        fault_path = raw_input() #Ex.) localhost/Rep1.rtc
        sync.stop_obs()
        try:
	    s = time.clock()
            group = rm.recovery(fault_path)
        except:
            print 'recovery failed'
            continue
        print 'recovery succeed'
        if group != 1:
            sync.state_update(group)
	e = time.clock()

        f = open('recovery_time.txt', 'a') 
        f.write(str(e-s)+'\n')
        f.close()
