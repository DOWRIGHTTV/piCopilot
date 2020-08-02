#!/usr/bin/python2

import os
from flask import current_app
from flask import Flask
from flask import render_template
from lib.shared import Shared
from lib.web.system import SYSTEM
from lib.web.query import QUERY


app = Flask(__name__)

## Homepages ##
@app.route('/')
def index():

    if sh.sysMode == 'None':
        return render_template('index.html',
                               system_Service = sh.sysMode,
                               system_Mode = 'None',
                               system_Channel = sh.bashReturn("iwlist wlan1mon channel | grep Current | awk '{print $5}' | cut -d\) -f1| tail -n 1"),
                               query_logSize = sh.logSize(),
                               query_Exports = os.system('/opt/piCopilot-idrop/kExporter.py'),
                               system_hddAvail = sh.bashReturn("df -h | grep '/dev/root' | awk '{print $4}'"))
    if sh.sysMode == 'k9':
        return render_template('index.html',
                               system_Service = sh.sysMode,
                               system_Mode = sh.rlCheck('k9'),
                               system_Channel = sh.bashReturn("iwlist wlan1mon channel | grep Current | awk '{print $5}' | cut -d\) -f1| tail -n 1"),
                               query_logSize = sh.logSize(),
                               query_Exports = os.system('/opt/piCopilot-idrop/kExporter.py'),
                               system_hddAvail = sh.bashReturn("df -h | grep '/dev/root' | awk '{print $4}'"))
    if sh.sysMode == 'kSnarfSqlite':
        return render_template('index.html',
                               system_Service = sh.sysMode,
                               system_Mode = sh.rlCheck('kSnarfSqlite'),
                               system_Channel = sh.bashReturn("iwlist wlan1mon channel | grep Current | awk '{print $5}' | cut -d\) -f1| tail -n 1"),
                               query_logSize = sh.logSize(),
                               query_Exports = os.system('/opt/piCopilot-idrop/kExporter.py'),
                               system_hddAvail = sh.bashReturn("df -h | grep '/dev/root' | awk '{print $4}'"))
    if sh.sysMode == 'kSnarfPsql':
        return render_template('index.html',
                               system_Service = sh.sysMode,
                               system_Mode = sh.rlCheck('kSnarfPsql'),
                               system_Channel = sh.bashReturn("iwlist wlan1mon channel | grep Current | awk '{print $5}' | cut -d\) -f1| tail -n 1"),
                               query_logSize = sh.logSize(),
                               query_Exports = os.system('/opt/piCopilot-idrop/kExporter.py'),
                               system_hddAvail = sh.bashReturn("df -h | grep '/dev/root' | awk '{print $4}'"))
    if sh.sysMode == 'Off':
        return render_template('index.html',
                               system_Service = sh.sysMode,
                               system_Mode = 'Off',
                               system_Channel = sh.bashReturn("iwlist wlan1mon channel | grep Current | awk '{print $5}' | cut -d\) -f1| tail -n 1"),
                               query_logSize = sh.logSize(),
                               query_Exports = os.system('/opt/piCopilot-idrop/kExporter.py'),
                               system_hddAvail = sh.bashReturn("df -h | grep '/dev/root' | awk '{print $4}'"))
###############################################################################



## Static files
@app.route('/jquery-3.1.1.min.js')
def jquery():
    return current_app.send_static_file('jquery-3.1.1.min.js')
###############################################################################



## No clicks
@app.route('/NICprep')
def nicPrep():
    sh.rlControl('start', 'nicPrep')
###############################################################################

if __name__ == '__main__':
    ## Setup
    sh = Shared()
    # app = Flask(__name__)

    ## Instantiate needed classes
    systemClass = SYSTEM(sh)
    system = systemClass.system

    queryClass = QUERY(sh)
    query = queryClass.query


    ## Register children
    app.register_blueprint(system)
    app.register_blueprint(query)


    ## Launch app
    app.run(debug = True, host = '0.0.0.0', port = 8001, threaded = True)
