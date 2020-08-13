# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request, send_file
import json
import os
import time
import sqlite3 as lite
import shutil
import subprocess

class QUERY(object):
    """Class for all things Query"""

    def __init__(self, sh):

        ## Grab our shared object
        self.sh = sh

        ## Call up our blueprint
        self.query = Blueprint('query',
                                __name__,
                                template_folder = 'templates')

###############################################################################



        ## Homepages ##
        @self.query.route('/Queries')
        def index():
            #if sh.sysMode = 'None':

            return render_template('query/index.html',
                                   _kSnarf = sh.rlCheck('kSnarfPsql'),
                                   logSize = sh.logSize(),
                                   hddAvail = sh.bashReturn("df -h | grep '/dev/root' | awk '{print $4}'"))
###############################################################################



        ## Configurations ##
        @self.query.route('/Query/Log-Delete')
        def logDelete():
            query_status = self.sh.rlCheck('query_Service')
            if query_status == 'RUNNING':
                return render_template('query/control/logDelete.html',
                                       action = 'deleted')
            else:
                try:
                    os.remove('/opt/piCopilot-idrop/downloads/logs.zip')
                except:
                    pass
                shutil.rmtree('/opt/piCopilot-idrop/logs')
                os.mkdir('/opt/piCopilot-idrop/logs')
                return render_template('query/index.html',
                                       _kSnarf = self.sh.rlCheck('kSnarf'),
                                       logSize = self.sh.logSize(),
                                       hddAvail = sh.bashReturn("df -h | grep '/dev/root' | awk '{print $4}'"))
###############################################################################




        ## No-Click Functions ##
        @self.query.route('/System/Log-Download')
        def logDownload():
            """Controls the download capabilities"""
            query_status = self.sh.rlCheck('kSnarf')
            print ('OUR QUERY STAT')
            print(query_status)
            if query_status == 'RUNNING':
                return render_template('system/control/logDelete.html',
                                       action = 'downloaded')
            else:
                try:
                    os.remove('/opt/piCopilot-idrop/downloads/logs.zip')
                except:
                    pass
                shutil.make_archive('/opt/piCopilot-idrop/downloads/logs/', 'zip', root_dir='/opt/piCopilot-idrop/logs')
                return send_file('/opt/piCopilot-idrop/downloads/logs.zip', as_attachment=True)


        @self.query.route('/System/Log-Download_pgsql')
        def pgLogDownload():
            """Controls the download capabilities for pgsql"""
            try:
                os.remove('/opt/piCopilot-idrop/downloads/logs.zip')
            except:
                pass
            os.system('/usr/bin/python2 /opt/piCopilot-idrop/kExporter.py')
            shutil.make_archive('/opt/piCopilot-idrop/downloads/logs/', 'zip', root_dir='/opt/piCopilot-idrop/logs')
            return send_file('/opt/piCopilot-idrop/downloads/logs.zip', as_attachment=True)
