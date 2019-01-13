from setuptools import setup, find_packages
import getpass
import os
import shutil
import subprocess

installService = True
installPath = '/etc/hyperion-timer'
username = getpass.getuser()
service = """
[Unit]
Description=hyperion-timer

[Service]
User={}
Type=simple
ExecStart=/usr/bin/python3 {}
StandardOutput=syslog
StandardError=syslog

[Install]
After=hyperion.service
WantedBy=default.target
""".format(username, installPath + '/main.py')

if installService and path.exists('/etc/systemd'):
    os.makedirs(installPath)
    shutil.copy2('main.py', installPath)
    with open('/etc/systemd/system/hyperion-timer.service', 'w') as f:
        f.write(service)
    commands = (
            'chown {} {}/main.py'.format(username, installPath)
            'chmod +x {}/main.py'.format(installPath)
            'systemctl daemon-reload',
            'systemctl enable hyperion-timer',
            'systemctl start hyperion-timer',
        )
    for command in commands:
        split = command.split()
        split.insert(0, 'sudo')
        subprocess.run(split)

setup(
        name='Hyperion Timer',
        version='0.1.0',
        description='Starts and stops hyperion-based lighting on a timer.',
        long_description='Periodically sends json messgaes to local or remote hyperion instance to illuminate based on current time.',
        url='https://github.com/khaudio/hyperion-timer',
        author='Kyle Hughes',
        author_email='kyle@kylehughesaudio.com',
        packages=find_packages(exclude=[]),
        install_requires=['datetime', 'json', 'socket', 'time'],
        classifiers=[
                'Programming Language :: Python :: 3.5.3'
                'Programming Language :: Python :: 3.7.0'
            ]
    )