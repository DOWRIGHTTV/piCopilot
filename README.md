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
    - piCopilot wants to be on a 192.168.10.254/24
    - DO NOT PROCEED PAST STEP 4 WITHOUT SWITCHING BACK TO 192.168.10.254/24
    - Modify /etc/wpa_supplicant/wpa_supplicant.conf accordingly
    - Remove the # in /etc/network/interfaces.d/wlan0
    - Give /etc/resolv.conf a nameserver

4. Prep easy-thread, packetEssentials and idrop
    - git clone https://github.com/stryngs/easy-thread.git
    - git clone https://github.com/stryngs/packetEssentials.git
    - git clone https://github.com/stryngs/piCopilot.git
    - ```python3 -m pip install easy-thread/easy-thread-*.tar.gz```
    - ```python3 -m pip install packetEssentials/RESOURCEs/packetEssentials-*.tar.gz```
    - ```dpkg -i piCopilot/DEBs/picopilot-scripts_*.deb```
    - ```dpkg -i piCopilot/DEBs/picopilot-idrop_*.deb```
    - ```apt-get install python3-netaddr```
    - shutdown
    - power on

5. Verify piCopilot-idrop is running and setup external USB NIC for 802.11
    - Ports 8001 and 9001 should now be in use
    - Plug in USB NIC
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
```

7. Prep Grafana
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

### kBlue setup (Optional)
1. Prepare a USB thumbdrive of ideally at least 8GB in size split evenly on the partitions.
    - /dev/sda1 should be swap
    - /dev/sda2 should be ext4

2. Install the needed packages for the Ubertooth integration
    - ```apt-get install libbtbb-dev libubertooth-dev ubertooth```

3. Setup /etc/fstab for mounts
    - ```mkdir -p /mnt/usb_storage```
    - ```echo '/dev/sda1 swap swap defaults 0 0' >> /etc/fstab```
    - ```echo '/dev/sda2 /mnt/usb_storage ext4 noauto,nofail,x-systemd.automount,x-systemd.idle-timeout=2,x-systemd.device-timeout=2' >> /etc/fstab```

4. Final steps
    - Power down the Raspberry Pi
    - Plugin USB drive and ubertooth
    - Power on the Raspberry Pi


### Ready to go
The Raspberry Pi in front of you is now a fully functional autonomous assistant.  In its current configuration it will connect to the Wireless Access Point it was previously connected to.  To revert to HostAPD mode reverse the step listed in the second bullet of step 3 and reboot.

### Known bug(s)
For the page on /, idrop Service can be confused by the presence of kBlue and how sh.sysMode is used.  When enabling kBlue and returning to the main menu, the idrop Service will now read as kBlue.  This will be worked out in later releases.  To force it proper, cycle the idrop service off and then back on.  It will correct by virtue of sh.sysMode flipping through the original idrop logic.

### Up next
OUI integrations for kBlue module.
A new .img with all of the aforementioned steps pre-ran.  Keep an eye out for it soon!

### Contacting support
For help with any of the steps or to inquire how piCopilot can support your integration needs for unmanned systems, please contact us via email:
```
support [at] configitnow.com
```
