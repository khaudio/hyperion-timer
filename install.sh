if [ "$(whoami)" != "root" ]; then
    echo "Error: Must be run as root; exiting."
    exit
fi

cp main.py /etc/hyperion-timer/main.py

cat << EOF > /etc/systemd/system/hyperion-timer.service
[Unit]
Description=hyperion-timer

[Service]
User=pi
Type=simple
ExecStart=/usr/bin/python3 /etc/hyperion-timer/main.py
StandardOutput=syslog
StandardError=syslog

[Install]
After=hyperion.service
WantedBy=default.target
EOF

systemctl daemon-reload
systemctl enable hyperion-timer
systemctl start hyperion-timer
