#!/usr/bin/python3

import subprocess
import re

out = subprocess.getstatusoutput("rabbitmqctl cluster_status")
begin = out[1].index('Running Nodes')
end = out[1].index('Versions')

res = out[1][begin:end].strip("Running Nodes")
reaesc = re.compile(r'\x1b[^m]*m')
new_text = reaesc.sub('', res)
print(len(new_text.split()))
