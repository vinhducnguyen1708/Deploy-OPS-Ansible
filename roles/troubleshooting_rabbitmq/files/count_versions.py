#!/usr/bin/python3

import subprocess
import re

out = subprocess.getstatusoutput("rabbitmqctl cluster_status")
begin = out[1].index('Versions')
end = out[1].index('Alarms')

res = out[1][begin:end].strip("Versions")
reaesc = re.compile(r'\x1b[^m]*m')
new_text = reaesc.sub('', res)

list_all=new_text.strip()

print(list_all)
