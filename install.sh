if [ "$(whoami)" != "root" ]; then
    echo "Error: Must be run as root; exiting."
    exit
fi
cp hyperion-timer.service /etc/systemd/system/hyperion-timer.service
systemctl daemon-reload
systemctl enable hyperion-timer
systemctl start hyperion-timer
