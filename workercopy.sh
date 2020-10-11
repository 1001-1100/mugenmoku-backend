users=(jmanzano pmato mgamutan asoliven)
pass=(mIGHbZOk BzgwdRNa EGDYbdfu aUOquSLv)
ip=103.231.240.131
port1=10148
port2=10107

for i in {0..3};
do
	for port in $port1 $port2;
	do
		echo "sshpass -p ${pass[$i]} scp -P $port * ${users[$i]}@$ip:."
		sshpass -p ${pass[$i]} scp -P $port * ${users[$i]}@$ip:. 
	done
done
