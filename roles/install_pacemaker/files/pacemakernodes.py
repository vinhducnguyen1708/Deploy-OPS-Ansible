#!/usr/bin/python

import commands


out = commands.getstatusoutput("pcs status")
begin = out[1].index('Online')
end = out[1].index('Full list of resources')

data = out[1][begin:end].strip("Online: [ ")

nodes = data[:-5].strip('[').strip(']').split(' ')

print len(nodes)

