systemctl stop  con-beacon.service con-ap.service
sudo ip link set wlp6s0 down
sudo iw dev wlp6s0 set type managed
sudo ip link set wlp6s0 up
systemctl start NetworkManager
