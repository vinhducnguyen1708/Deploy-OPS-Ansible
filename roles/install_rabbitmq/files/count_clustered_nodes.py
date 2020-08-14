#!/usr/bin/python

import commands

out = commands.getstatusoutput("rabbitmqctl cluster_status")
begin = out[1].index('running_nodes')
end = out[1].index('cluster_name')

data = out[1][begin:end].strip("running_nodes,")

nodes = data[:-5].strip('[').strip(']').split(',')

print len(nodes)

