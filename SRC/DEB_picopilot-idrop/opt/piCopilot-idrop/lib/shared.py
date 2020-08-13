import subprocess

class Shared(object):
    """Shared idrop class"""

    def __init__(self):
        self.sysMode = 'None'


    def rlCheck(self, relay):
        """Check the status of the relay"""
        return subprocess.check_output('supervisorctl status {0}'.format(relay),
                                       shell = True).decode().split()[1]


    def rlControl(self, button, relay):
        """Control the relay"""
        self.sysMode = relay
        subprocess.check_output('supervisorctl {0} {1}'.format(button, relay),
                                shell = True)


    def logSize(self):
        """Return the total size of all sql and pcap for idrop"""
        return subprocess.check_output('du -h /opt/piCopilot-idrop/logs/ | tail -n 1 | cut -f1',
                                       shell = True).decode().strip()


    def bashReturn(self, cmd):
        """Cheap bash return"""
        return subprocess.check_output(cmd,
                                       shell = True).decode().strip()
