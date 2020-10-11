users=(jmanzano pmato mgamutan asoliven)
pass=(mIGHbZOk BzgwdRNa EGDYbdfu aUOquSLv)
ip=103.231.240.131
port1=10148
port2=10107

for i in {0..3};
do
	for port in $port1 $port2;
	do
		echo "sshpass -p ${pass[$i]} ssh -p $port ${users[$i]}@$ip 'python3 worker.py' &"
		sshpass -p ${pass[$i]} ssh -p $port ${users[$i]}@$ip 'python3 worker.py' &
		sleep 2
	done
done
