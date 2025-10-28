systemctl stop NetworkManager
sudo ip link set wlp6s0 down
systemctl start  con-beacon.service con-ap.service
