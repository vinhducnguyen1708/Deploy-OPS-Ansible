#!/usr/bin/python3


import subprocess

out = subprocess.getstatusoutput("pcs status")
begin = out[1].index('Online')
end = out[1].index('Full List of Resources')

data = out[1][begin:end].strip("Online: [ ")

nodes = data[:-5].strip('[').strip(']').split(' ')

print (len(nodes))
