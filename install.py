from os import getuid, system, mkdir, popen, setuid, setgid
from pathlib import Path


def run_command(command: str):
    status = system(command)
    if status != 0:
        exit(status)


if getuid() != 0:
    print("You must run it as root")
    exit(1)

if Path("/etc/debian_version").exists():
    # Ubuntu/Debian
    run_command("apt install -y postgresql-client")
elif Path("/etc/system-release").exists():
    # CentOS
    run_command("dnf install -y postgresql-client")
else:
    print("Your OS is not supported")
    exit(1)

if not Path("/opt/pgDump/").exists():
    mkdir("/opt/pgDump/")

run_command("groupadd -f pgDump")
if system("id -u pgDump") != 1:
    run_command("useradd -g pgDump -b /opt/pgDump/ pgDump")

uid = int(popen("id -u pgData").read())
gid = int(popen("id -g pgData").read())

if Path("/opt/pgData/venv").exists():
    run_command("rm -r /opt/pgData/venv")
run_command("python -m venv /opt/pgData/venv; . /opt/pgData/venv/bin/activate; pip install requirements.txx")

run_command("cp -r src/* /opt/pgData/")
run_command(f"cp {'config.yml' if Path('config.yml').exists() else 'config.sample.yml'} /opt/pgData/config.yml")

run_command("chown -R pgData:pgData /opt/pgData/")

setgid(gid)
setuid(uid)

run_command("crontab -l > /opt/pgData/mycron")
with Path("/opt/pgData/mycron").open("a") as file:
    file.write("00 20 * * * /opt/pgData/venv/bin/python /opt/pgData/main.py")
run_command("crontab /opt/pgData/mycron")
run_command("rm /opt/pgData/mycron")
