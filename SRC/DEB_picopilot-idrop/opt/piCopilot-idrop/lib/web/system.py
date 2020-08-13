# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request
import os, time

import RPi.GPIO as GPIO
import subprocess
from datetime import datetime
import time

class SYSTEM(object):
    """Class for all things idrop or Pi Shutdown/Reboot"""

    def __init__(self, sh):

        ## Grab our shared object
        self.sh = sh

        ## Set mode to board and prep
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(23, GPIO.OUT)

        ## Cheap monitor
        self.monMode = None

        ## Get our blueprint
        self.system = Blueprint('system',
                                   __name__,
                                   template_folder = 'templates')
###############################################################################



        ## Homepages ##
        @self.system.route('/System')
        def index():
            """Start the service"""
            return render_template('system/control/index.html',
                                   uChoice = ['ListenSql', 'ListenPsql', 'k9', 'Off'])
###############################################################################


        ## No-Click Functions ##
        #@self.system.route('/System/NICprep', methods = ['POST'])
        #def nicPrep():
            #"""Prep the NIC by matching MACs

            #Cheap way to reboot
            #"""
            #self.sh.rlControl('start','nicPrep')
            ##self.sh.bashReturn('bash /opt/piCopilot-scripts/nicPrep.sh')
            #return render_template('index.html',
                                #system_Service = sh.rlCheck('kSnarf'),
                                #system_Channel = sh.bashReturn("iwlist wlan1mon channel | grep Current | awk '{print $5'} | cut -d\) -f1| tail -n 1"),
                                #query_logSize = sh.logSize(),
                                #system_hddAvail = sh.bashReturn("df -h | grep '/dev/root' | awk '{print $4}'"))

        @self.system.route('/System/Service-Control', methods = ['POST'])
        def serviceControl():
            """Change the idrop system Relay Controls"""

            self.sh.systemServiceControl = request.form.get('buttonStatus')

            ## Deal with k9 turning off
            if sh.systemServiceControl == 'Off':
                if self.sh.rlCheck('k9') == 'RUNNING':
                    self.sh.rlControl('stop', 'k9')
                    GPIO.output(23, GPIO.LOW)

                    ## Cheap way to snipe k9 as it is hanging
                    kPID = str(self.sh.bashReturn("ps aux | grep k[9] | awk '{print $2}'"))
                    print ('OUR k9 PID IS {0}'.format(str(kPID)))
                    print ('OUR k9 PID IS TYPE {0}'.format(str(type(kPID))))
                    try:
                        self.sh.bashReturn("kill -9 %s" % kPID)
                    except:
                        time.sleep(2)
                        try:
                            self.sh.bashReturn("kill -9 %s" % kPID)
                        except:
                            pass
                        pass


            ## If the service is running and we turn off
            if self.sh.rlCheck('kSnarfSqlite') == 'RUNNING':
                ### Really need to add more mature logic.  This is just to get us running with psql

                if self.sh.systemServiceControl == 'k9':
                    ret = '<strong>You cannot invoke k9 mode when idrop is in listen mode</strong>'
                    ret += '</br></br>'
                    ret += '<a href="/">'
                    ret += '    <button>Main Menu</button>'
                    ret += '</a>'
                    return ret

                if self.sh.systemServiceControl == 'Off':
                    self.sh.rlControl('stop', 'kSnarfSqlite')
                    GPIO.output(23, GPIO.LOW)


                    ## Cheap way to snipe kSnarf as it is hanging
                    kPID = str(self.sh.bashReturn("ps aux | grep kSnar[f] | awk '{print $2}'"))
                    print ('OUR kSnarf PID IS {0}'.format(str(kPID)))
                    print ('OUR kSnarf PID IS TYPE {0}'.format(str(type(kPID))))
                    try:
                        self.sh.bashReturn("kill -9 %s" % kPID)
                    except:
                        time.sleep(2)
                        try:
                            self.sh.bashReturn("kill -9 %s" % kPID)
                        except:
                            pass
                        pass


            ## If the service is running and we turn off
            if self.sh.rlCheck('kSnarfPsql') == 'RUNNING':
                ### Really need to add more mature logic.  This is just to get us running with psql

                if self.sh.systemServiceControl == 'k9':
                    ret = '<strong>You cannot invoke k9 mode when idrop is in listen mode</strong>'
                    ret += '</br></br>'
                    ret += '<a href="/">'
                    ret += '    <button>Main Menu</button>'
                    ret += '</a>'
                    return ret

                if self.sh.systemServiceControl == 'Off':
                    self.sh.rlControl('stop', 'kSnarfPsql')
                    GPIO.output(23, GPIO.LOW)


                    ## Cheap way to snipe kSnarf as it is hanging
                    kPID = str(self.sh.bashReturn("ps aux | grep kSnar[f] | awk '{print $2}'"))
                    print ('OUR kSnarf PID IS {0}'.format(str(kPID)))
                    print ('OUR kSnarf PID IS TYPE {0}'.format(str(type(kPID))))
                    try:
                        self.sh.bashReturn("kill -9 %s" % kPID)
                    except:
                        time.sleep(2)
                        try:
                            self.sh.bashReturn("kill -9 %s" % kPID)
                        except:
                            pass
                        pass

            ## If the service is not running and we turn on
            else:

                ## Check for monitor mode
                if self.monMode is None:
                    self.sh.rlControl('start', 'nicMon')
                    self.monMode = True

                ## Check for k9 mode
                if self.sh.systemServiceControl == 'k9':
                    self.sh.rlControl('start', 'k9')
                    GPIO.output(23, GPIO.HIGH)

                ## Check for listen mode sqlite
                if self.sh.systemServiceControl == 'ListenSql':
                    self.sh.rlControl('start', 'kSnarfSqlite')
                    GPIO.output(23, GPIO.HIGH)

                ## Check for listen mode psql
                if self.sh.systemServiceControl == 'ListenPsql':
                    self.sh.rlControl('start', 'kSnarfPsql')
                    GPIO.output(23, GPIO.HIGH)

            return render_template('system/index.html',
                                   serviceStatus = self.sh.rlCheck(self.sh.sysMode))
