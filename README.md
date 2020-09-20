# piCopilot
piCopilot is 100% feedback driven.  If you like piCopilot and wish to contribute, simply fork and PR; or raise an issue.

Certain aspects of piCopilot may not be legal in every Country or locality.  Ensure that you check the rules and regulations for where you will be operating prior to use.  The operator is fully and wholly responsible for any legal and/or civil issues that may arise from their usage of piCopilot.

### Core packages
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

### Definitions
* ecosystem
  * Any objects in memory, files, folders or system processes which make up how piCopilot operates
* kBlue
  * The underlying framework for Ubertooth and PostgreSQL interaction
* kSnarf
  * The underlying framework for 802.11 sniffing and PostgreSQL interaction
* pipeline network
  * The IPv4 network between the user and the ecosystem
  * Built on an 802.11 model
  * Can be 802.3 based with minor modifications
  * Responsible for all interactions with piCopilot
    * 3000 - Grafana
    * 8000 - piCopilot-unmanned control panel
    * 8001 - kSnarf and kBlue control panel
    * 8765 - Motioneye
    * 9001 - Supervisor
    * 9090 - idrop visuals

### Why does most of the system run as root!?
piCopilot expects a secured network.  It is not recommended to connect the pipeline network to any network where untrusted users are present or have the ability to sniff traffic.  "Pick one thing and do it well".

### Getting started
1. Create the piCopilot image for the Raspberry Pi
    - Refer to notes in RELEASE
    - Minimum 8GB SD card required
    - Burn the image
    - Boot the Raspberry Pi

2. When piCopilot first boots it will be running in hostapd mode.
    - Set your wifi NIC to 192.168.10.10/24
    - Connect to the wifi ESSID called myPi
    - The password is piCopilotAP

3. Verify piCopilot-idrop is running and setup external USB NIC for 802.11
    - Ports 8001 and 9001 should now be in use
    - Plug in USB NIC
    - Open a browser and proceed to http://192.168.10.254:8001/
    - Select NIC prep
    - The system will shutdown

### Performance boosts (Recommended - Required for kBlue)
For SD card preservation, dphys-swapfile is disabled.  It is preferable to offload any swapping to a USB:
1. Prepare a USB thumb-drive of ideally at least 8GB in size split evenly on the partitions.
    - /dev/sda1 should be swap
    - /dev/sda2 should be ext4

2. ***Optional thrashing including***
    - If not worried about the SD card, then do
```
systemctl enable dphys-swapfile
```

3. Setup /etc/fstab for mounts:
```
mkdir -p /mnt/usb_storage
echo '/dev/sda1 swap swap defaults 0 0' >> /etc/fstab
echo '/dev/sda2 /mnt/usb_storage ext4 noauto,nofail,x-systemd.automount,x-systemd.idle-timeout=2,x-systemd.device-timeout=2' >> /etc/fstab
```

4. Final steps
    - Power down the Raspberry Pi
    - Plugin USB drive and ubertooth
    - Power on the Raspberry Pi


### Grafana visualizations (Optional)
Setup Grafana and visualize your findings
    - systemctl start grafana-server
    - Proceed to http://192.168.10.254:3000/login
    - Login with admin:admin
    - Change the default Grafana password
    - A sample dashboard for idrop is waiting on you

### Tuning kBlue (Optional)
Benchmark on Raspberry Pi 3 Model B+ as determined by [blRip.py](https://github.com/stryngs/workshops/blob/master/DC28/blRip.py) w/ no print:
```
$ python3 blRip.py
Total time: 24.86375856399536
Packets processed: 19235
Packets per second: 773.6159418734769
```
With the limited horsepower of a Raspberry Pi, any shortcuts we can take are vital to keeping up with the live data flow.  By ignoring MAC Addresses that are known and unwanted for monitoring we can cut down on the chaff in the database.  To invoke this feature place a file named /opt/piCopilot-idrop/ignore.lst.  This file should consist of MAC addresses separated by a newline.  For now the only checking done on this is a character count.  The case of the string does not matter.  MAC addresses should be in colon format, i.e.:
```
aa:bb:cc:dd:ee:ff
```

#### Unmanned Vehicle Operations (Optional)
The picopilot-unmanned package has been pre-installed as part of the 20200824 release.  In an effort to make the best of both idrop and the unmanned platform in a single image, the decision was made to have the controller running -- but none of the unmanned core services turned on.  The following files are of interest to anyone who wants to have the core services turned on at boot:
    - /etc/supervisor/conf.d/gsPrep.conf
    - /etc/supervisor/conf.d/motionPrep.conf
    - /etc/supervisor/telemetry_Service.conf

piCopilot has been tested and verified with the Pixhawk IMU.  The unmanned package works seemlessly with either QGroundControl or Mission Planner.  For further information on both Ground Control Systems, please refer to their respective websites:
    - http://qgroundcontrol.com/
    - https://ardupilot.org/planner/

#### Connecting piCopilot to the Internet (Optional)
    - piCopilot wants to be on a 192.168.10.254/24
    - Modify /etc/wpa_supplicant/wpa_supplicant.conf accordingly
    - Remove the # in /etc/network/interfaces.d/wlan0
    - Give /etc/resolv.conf a nameserver

### Known bug(s)
    - For the page on /, the idrop Service gets confused by the presence of kBlue and how sh.sysMode is used.  When enabling kBlue and returning to the main menu, the idrop Service will now read as kBlue.  This will be worked out in later releases.  To force it proper, cycle the idrop service off and then back on.  It will correct by virtue of sh.sysMode flipping through the original idrop logic.
    - kBlue makes use of the Ubertooth by way of ubertooth-btle and reading from a pre-recorded stream.  The streams default to 20 seconds per stream in real-time.  As kBlue currently does not rip stdout for ubertooth-btle, there is no time association just yet.  Every packet within a given burst of packets on a given bluesPipe will have the timestamp until a workaround is found.

### Up next
    - Further kSnarf and kBlue method integrations.
    - OUI integrations for kBlue module.
    - A confirmation for nicPREP prior to firing.
        - The current workaround is to erase piCopilot browser tab history after firing nicPREP.  This will ensure you do not accidently re-fire it during operational use.


### Contacting support
For help with any of the steps or to inquire how piCopilot can support your integration needs for unmanned systems, please contact us via email:
```
support [at] configitnow.com
```
