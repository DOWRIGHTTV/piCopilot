# piCopilot
piCopilot is 100% feedback driven.  If you like piCopilot and wish to contribute, simply fork and PR.

Certain aspects of piCopilot may not be legal in every Country or locality.  Ensure that you check the rules and regulations for where you will be operating prior to use.  The operator is fully and wholly responsible for any legal and/or civil issues that may arise from their usage of piCopilot.

### Publically shared packages
* piCopilot
  * The ecosystem
* piCopilot-idrop
  * Intrusion Detection Reaction Observation Platform
* piCopilot-scripts
  * Useful scripts for piCopilot usage across the ecosystem
* piCopilot-unmanned
  * Pi powered Copilot for Unmanned Systems
* piCopilot-wifi
  * WiFi meta-package for piCopilot

### Getting started
1. Create an image for a Raspberry Pi
    - Refer to notes in RELEASE
    - Burn the image
    - Boot the Raspberry Pi

2. When piCopilot first boots it will be running in hostapd mode.
    - Set your wifi NIC to 192.168.10.10/24
    - Connect to the wifi ESSID called myPi
    - The password is piCopilotAP

3. Connecting piCopilot to the Internet.
    - Modify /etc/wpa_supplicant/wpa_supplicant.conf accordingly
    - Remove the # in /etc/network/interfaces.d/wlan0
    - Give /etc/resolv.conf a nameserver

4. Setup piCopilot-idrop
    - wget https://github.com/stryngs/piCopilot
    - dpkg -i piCopilot/DEBs/picopilot-idrop_0.4.2_all.deb
    - shutdown
    - power on

5. Verify piCopilot-idrop is running and setup external USB NIC for 802.11
    - Ports 8001 and 9001 should now be in use
    - Plug in usb nic
    - Open a browser and proceed to http://192.168.10.254:8001/
    - Select NIC prep
    - The system will shutdown

6. Setup piCopilot-idrop database
    - Power on the system
    - systemctl enable postgresql
    - systemctl start postgresql

```
## As root, do:
su postgres
cd
createuser root -P --interactive
    #Enter password for new role: <idrop>
    #Shall the new role be a superuser? (y/n) n
    #Shall the new role be allowed to create databases? (y/n) y
    #Shall the new role be allowed to create more new roles? (y/n) y
psql
## ALTER ROLE root WITH PASSWORD 'password'; ## << how to change root for later
CREATE DATABASE idrop;
GRANT pg_write_server_files TO root;
crtl+d
exit
mkdir /opt/piCopilot-idrop/logs
chown -R postgres /opt/piCopilot-idrop/logs
```

7. Prep threading, packetEssentials and Grafana
    - git clone https://github.com/stryngs/easy-thread
    - ```python -m pip install easy-thread/easy-thread-*.tar.gz```
    - git clone https://github.com/stryngs/packetEssentials
    - ```python -m pip install packetEssentials/RESOURCEs/packetEssentials-*.tar.gz```
    - Modify /etc/supervisor/conf.d/kSnarfPsql.conf accordingly
    - Proceed to http://192.168.10.254:8001/
    - Select idrop
    - Select ListenPsql
    - Select Change Status
    - ```dpkg -i piCopilot/kickstart/grafana_*.deb```

8. Let the system run for at least 5 minutes to collect initial information about your location

9. Setup Grafana and visualize your findings
    - Proceed to http://192.168.10.254:3000/login
    - Login with admin:admin
    - Change the default Grafana password
    - Select Add data source
    - Choose PostgreSQL
        - 127.0.0.1:5432
        - disable ssl mode
    - Select Save & test
    - Select back
    - Proceed back to http://192.168.10.254:3000/
    - Select the + | Create | Import
    - Select Upload .json file
    - Choose the example json in kickstart/IDS_Example.json
    - Import
        - Example data should now be visible

### Ready to go
The Raspberry Pi in front of you is now a fully functional autonomous assistant.  In its current configuration it will connect to the Wireless Access Point it was previously connected to.  To revert to HostAPD mode reverse the step listed in the second bullet of step 3 and reboot.

### Known bug(s)
There exists a bug when trying to download the postgresql logs.  The workaround for the time being is down run kExporter and then grab the logs from /opt/piCopilot-idrop/logs/.

### Contacting support
For help with any of the steps or to inquire how piCopilot can support your integration needs for unmanned systems, please contact us via email:
```
support [at] configitnow.com
```
