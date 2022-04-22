#systemctl status aclogger.service
#systemctl status acdisplay.service
journalctl -u aclogger.service | tail -n 50

