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
    run_command("apt install -y cron python3-venv")

    run_command("groupadd -f pgDump")
    if system("id -u pgDump") == 256:
        run_command("useradd -g pgDump -G docker -b /opt/pgDump/ pgDump")
    uid = int(popen("id -u pgDump").read())
    gid = int(popen("id -g pgDump").read())
    run_command("chown -R pgDump:pgDump /opt/pgDump/")

    setgid(gid)
    setuid(uid)
elif Path("/etc/system-release").exists():
    # CentOS
    run_command("dnf install -y crontabs")
else:
    print("Your OS is not supported")
    exit(1)

if not Path("/opt/pgDump/").exists():
    mkdir("/opt/pgDump/")

if Path("/opt/pgDump/venv").exists():
    run_command("rm -r /opt/pgDump/venv")
run_command("python3 -m venv /opt/pgDump/venv; . /opt/pgDump/venv/bin/activate; pip install -r requirements.txt")

run_command("cp -r src/* /opt/pgDump/")
run_command(f"cp {'config.yml' if Path('config.yml').exists() else 'config.sample.yml'} /opt/pgDump/config.yml")

system("crontab -l > /opt/pgData/mycron")
with Path("/opt/pgDump/mycron").open("r") as f:
    if "pgDump" not in f.read():
        with Path("/opt/pgDump/mycron").open("a") as file:
            file.write("00 20 * * * /opt/pgDump/venv/bin/python /opt/pgDump/main.py\n")
run_command("crontab /opt/pgDump/mycron")
run_command("rm /opt/pgDump/mycron")
