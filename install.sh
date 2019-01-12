systemctl stop hyperion
cp hyperion-timer.service /etc/systemd/system/hyperion-timer.service
systemctl daemon-reload
systemctl start hyperion
systemctl start hyperion-timer
