#!/usr/bin/python3

import subprocess
import re

out = subprocess.getstatusoutput("rabbitmqctl cluster_status")
begin = out[1].index('Network Partitions')
end = out[1].index('Listeners')

res = out[1][begin:end].strip("Network Partitions")
reaesc = re.compile(r'\x1b[^m]*m')
new_text = reaesc.sub('', res)

list_all=new_text.strip()

print(list_all)