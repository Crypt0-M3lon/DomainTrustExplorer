######
# Author: @sixdub
# Description: Shell based wrapper for networkx library that 
# provides functionality to analyze domain trust relationships 
# generated by powerview
#
######

import networkx as nx
import matplotlib.pyplot as plt
from cmd import Cmd
import sys,os, argparse

#Define my graph and the filename read in
G = nx.DiGraph()
filename=""

#Instance of cmd.Cmd object which gives us the shell
class GraphShell(Cmd):
	global G
	global filename
	last_output=''

	#Set our custom prompt
	def __init__(self):
		Cmd.__init__(self)
		self.prompt = "TrustExplore> "

	#Allow user to run local shell commands and print output
	def do_shell(self, line):
		"Run a shell command"
		print "running shell command:", line
		output = os.popen(line).read()
		print output
		self.last_output = output

	#Handle our commands for exit, Ctrl-D and EOF
	def do_exit(self,line):
		"Exit the application. Can also use Ctrl-D"
		return True

	def do_EOF(self, line):
		"Exit the application with Crtl-D"
		return True

	#Dump the graph in GML format
	def do_gml_dump(self, line):
		"Creates output as GML"
		ofile = filename+".gml"
		nx.write_gml(G, ofile)
		print "%s written!"%ofile

	#Dump the graph in GraphML format
	def do_graphml_dump(self, line):
		"Creates output as GraphML"
		ofile = filename+".graphml"
		nx.write_graphml(G, ofile)
		print "%s written!"%ofile

	def do_list_nodes(self,line):
		for n in nx.nodes_iter(G):
			print n

	#Command go show all shortest paths
	def do_path(self, args):
		"Display the shortest path between two nodes"
		#Grab the args
		node1=args.split(" ")[0].upper()
		node2=args.split(" ")[1].upper()

		#ensure they exist
		if G.has_node(node1) and G.has_node(node2):
			if (nx.has_path(G,node1,node2)):
				#Get the shortest paths
				paths = nx.all_shortest_paths(G, node1, node2)

				#Print all paths in pretty format
				for p in paths:
					outputpath = "[*] "
					for n in p:
						outputpath+=n+" -> "
					print outputpath[:-4]
			else:
				print "No path exist :("
		else:
			print "Node %s or %s does not exist :(" % (node1, node2)

	#Show all paths
	def do_all_paths(self,args):
		"Display all paths between two nodes"
		#Grab the args
		node1=args.split(" ")[0].upper()
		node2=args.split(" ")[1].upper()

		#ensure they exist
		if G.has_node(node1) and G.has_node(node2):
			if (nx.has_path(G,node1,node2)):
				#Get the shortest paths
				paths = nx.all_simple_paths(G, node1, node2)

				#Print all paths in pretty format
				for p in paths:
					outputpath = "[*] "
					for n in p:
						outputpath+=n+" -> "
					print outputpath[:-4]
			else:
				print "No path exist :("
		else:
			print "Node %s or %s does not exist :(" % (node1, node2)

	#Print all neighbors of a certain node
	def do_neighbors(self,args):
		"Show all the neighbors for a certain node"
		node = args.upper()
		if G.has_node(node):
			l = G.neighbors(node)
			
			print "Neighbors:"
			for n in l:
				print n
		else:
			print "No node in the graph"

	#print all isolated nodes
	def do_isolated(self, args):
		"Show all nodes that are isolated"
		print "Isolated Nodes:"
		for n in G.nodes():
			if len(G.neighbors(n)) ==1:
				print n

	#calculate degree centrality and print top 5
	def do_center(self,args):
		"Show the top 5 most central nodes"
		d = nx.out_degree_centrality(G)
		cent_items=[(b,a) for (a,b) in d.iteritems()]
		cent_items.sort()
		cent_items.reverse()

		for i in range(0,5):
			if cent_items[i]:
				print cent_items[i]

	#print some statistics
	def do_summary(self, args):
		"Show statistics on my trust map"
		ncount = len(G)
		ecount = G.number_of_edges()
		print "Summary:"
		print "Filename: %s"%filename
		print "Node Count: %d"%ncount
		print "Edge Count: %d"%ecount

	#notify the user if a node exist
	def do_is_node(self, args):
		print G.has_node(args.upper())

if __name__ == '__main__':
	#open our file
	with open(sys.argv[1],"r") as f:
		data = f.readlines()
	#save the name for later
	filename=os.path.basename(sys.argv[1])
	c = 0

	#for every line in our CSV
	for line in data[1:]:
		#strip off quotes and newline characters
		stripdata = line.replace('"',"").replace('\n','')

		#split the CSV and store normalized values
		values = stripdata.split(',')
		node1 = values[0].upper()
		node2 = values[1].upper()
		relationship = values[2].upper()
		edgetype=values[3].upper()

		#Add the nodes with labels
		G.add_node(node1, label=node1)
		G.add_node(node2, label=node2)

		#assign edge colors based on the kind of relationship
		ecolor ='#000000'
		if "CROSSLINK" in relationship:
			ecolor='#0000CC'
		elif "PARENTCHILD" in relationship:
			ecolor='#FF0000'
		elif "EXTERNAL" in relationship:
			ecolor='#009900'

		#add the edges to the graph
		if "BIDIRECTIONAL" in edgetype:
			G.add_edge(node1, node2, color=ecolor)
			G.add_edge(node2, node1, color=ecolor)
		elif "OUTBOUND" in edgetype:
			G.add_edge(node1, node2, color=ecolor)
		elif "INBOUND" in edgetype:
			G.add_edge(node2, node1, color=ecolor)
		else:
			print "UNRECOGNIZED RELATIONSHIP DIRECTION"
			exit()

		c+=1
	print "%d relationships read in... starting shell" % c
	GraphShell().cmdloop()