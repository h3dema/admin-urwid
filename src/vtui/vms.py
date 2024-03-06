import subprocess
import re
import logging
import datetime


def run_cmd(ssh_cmd: str) -> subprocess.CompletedProcess:
    logging.debug(f"cmd: {ssh_cmd}")
    result = subprocess.run([ssh_cmd], shell=True, capture_output=True, text=True)
    return result


class virtualbox(object):

    def __init__(self, hostname):
        self.hostname = hostname
        self.ssh = f"ssh {hostname}"

    def run_ssh(self, cmd: str) -> subprocess.CompletedProcess:
        ssh_cmd = "{ssh} '{cmd}'".format(ssh=self.ssh, cmd=cmd)
        return run_cmd(ssh_cmd)

    def hostinfo(self) -> str:
        """ basic information (mem, processors, OS, etc) about the host
        """
        result = self.run_ssh("vboxmanage list hostinfo")
        return result.stdout

    def vms(self) -> list[dict]:
        result = self.run_ssh("vboxmanage list vms")
        r = re.findall(r"\"(.*)\" {(.*)}", result.stdout)
        r = [{"name": _name, "uid": _id} for _name, _id in r]
        return r

    def runningvms(self) -> list[dict]:
        result = self.run_ssh("vboxmanage list runningvms")
        r = re.findall(r"\"(.*)\" {(.*)}", result.stdout)
        r = [{"name": _name, "uid": _id} for _name, _id in r]
        return r

    # ------------------------------------------------------------------------
    # VMs
    # ------------------------------------------------------------------------

    def showvminfo(self, vmname: str) -> str:
        """ basic information about the vm configuration
        """
        result = self.run_ssh(f"vboxmanage showvminfo {vmname}")
        return result.stdout

    def stop_vm(self, vmname: str, force: bool = False) -> str:
        shutdown = "poweroff" if force else "acpipowerbutton"
        result = self.run_ssh(f"vboxmanage controlvm {vmname} {shutdown}")
        return result.stdout

    def start_vm(self, vmname: str, headless: bool = True) -> str:
        is_headless = "--type headless" if headless else "acpipowerbutton"
        result = self.run_ssh(f"vboxmanage startvm {vmname} {is_headless}")
        return result.stdout

    # ------------------------------------------------------------------------
    # SNAPSHOTS
    # ------------------------------------------------------------------------

    def list_snapshots(self, vmname: str) -> str:
        result = self.run_ssh(f"vboxmanage snapshot {vmname} list")
        r = re.findall(r"Name: (.*) \(UUID: (.*)\)(.*)", result.stdout)
        r = [{"name": _name, "uuid": _id, "active": _active.strip() == "*"} for _name, _id, _active in r]
        return r

    def take_snapshot(self, vmname: str) -> str:
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        result = self.run_ssh(f'vboxmanage snapshot {vmname} take "{date_str}" --description "snapshot at `date`"')
        return result.stdout

    def delete_snapshot(self, vmname: str, snapname: str) -> str:
        result = self.run_ssh(f'vboxmanage snapshot {vmname} delete {snapname}')
        return result.stdout


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    foice = virtualbox("foice")
    for entry in foice.runningvms():
        print(entry)
