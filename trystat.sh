cat ~/Desktop/two_points/persist/1/var/log/emane.log | grep "pcr 0.33 <" | wc
cat ~/Desktop/two_points/persist/1/var/log/emane.log | grep "pcr 0.33 >=" | wc
emanesh node-1 clear stat 1 all
sleep 15
emanesh node-1 get stat 1 mac | grep numUpstreamPackets
cat ~/Desktop/two_points/persist/1/var/log/emane.log | grep "pcr 0.33 <" | wc
cat ~/Desktop/two_points/persist/1/var/log/emane.log | grep "pcr 0.33 >=" | wc

