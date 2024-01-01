from matplotlib import pylab, pyplot as plt
import snap
import pickle
from project_helpers import read_data_from_binary
from plots import plotDegreeDist, plotDegreeDist_mult
#customers, products = read_data_from_binary()

C_P_graph = snap.LoadEdgeList(snap.PUNGraph, "C_P_graph", 0, 1)

p = open("customer_product_graph.pkl", "rb")
customers_int_to_string = pickle.load(p)
products_int_to_string = pickle.load(p)
customer_product_weights = pickle.load(p)
p.close()

# Visualize C_P_graph
plotDegreeDist(C_P_graph, 'Customer - Product Graph Degree Distribution1', 'r', 100, 0.00001)
plotDegreeDist_mult(C_P_graph, 'Customer - Product Graph Degree Distribution2', 'r', 100, 0.00001, customers_int_to_string, 'Products')

print(len(customers_int_to_string)) # 9,740
products_string_to_int = {y:x for x,y in products_int_to_string.iteritems()}

################ READ CC GRAPH ##################

C_C_graph = snap.LoadEdgeList(snap.PUNGraph, "C_C_graph", 0, 1)

p = open("customer_category_graph.pkl", "rb")
categories_int_to_tuple = pickle.load(p)
categories_to_products = pickle.load(p)
customer_category_weights = pickle.load(p)
p.close()

print(categories_int_to_tuple.values())

# Visualize C_C_graph
plotDegreeDist(C_C_graph, 'Customer - Category Graph Degree Distribution1', 'g', 10000, 0.0001)
plotDegreeDist_mult(C_C_graph, 'Customer - Category Graph Degree Distribution2', 'g', 10000, 0.00005, customers_int_to_string, 'Categories')

print(C_C_graph.GetNodes()) # 9799 customers
print(C_C_graph.GetEdges()) # 44040

print(len(categories_int_to_tuple)) # 84
print(len(customer_category_weights)) # = number of edges

################# READ C_NET ###################

print('Loading C_Net...')
C_Net = snap.LoadEdgeList(snap.PUNGraph, "C_Net", 0, 1)

p = open("customer_graph.pkl", "rb")
customer_weights = pickle.load(p)
Cs = pickle.load(p)
p.close()

plotDegreeDist(C_Net, 'Customer Network Degree Distribution1', 'g', 10000, 0.0001)

print(C_Net.GetNodes()) # 9057
print(C_Net.GetEdges()) # 8,995,947

print('BEGIN TESTS:')
print('---------------------')
###### EDGES LISTS FOR INDUCED SUBGRAPHS ######
# CPG
nd_MAX = snap.GetMxDegNId(C_P_graph)
NIdV = snap.TIntV()
snap.GetNodesAtHop(C_P_graph, nd_MAX, 1, NIdV, False) # 1-hop
NIdV.Add(nd_MAX)

NIdV2 = snap.TIntV()
snap.GetNodesAtHop(C_P_graph, nd_MAX, 2, NIdV2, False) #2-hop
for i in NIdV2:
    NIdV.Add(i)

SubGraph = snap.GetSubGraph(C_P_graph, NIdV)
if nd_MAX in customers_int_to_string:
    print('IS CUSTOMER')
    print(nd_MAX)
    print(customers_int_to_string[nd_MAX])
elif nd_MAX in products_int_to_string:
    print('IS PRODUCT')
else:
    print('FUUUUUUUCK')

snap.SaveEdgeList(SubGraph, 'CPG_node_'+str(nd_MAX)+'.csv', 'Subgraph')

print('---------------------')

# CCG
nd_MAX = 1500
NIdV = snap.TIntV()
snap.GetNodesAtHop(C_C_graph, nd_MAX, 1, NIdV, False)
NIdV.Add(nd_MAX)

NIdV2 = snap.TIntV()
snap.GetNodesAtHop(C_C_graph, nd_MAX, 2, NIdV2, False) #2-hop
for i in NIdV2:
    NIdV.Add(i)

SubGraph = snap.GetSubGraph(C_C_graph, NIdV)
if nd_MAX in customers_int_to_string:
    print('IS CUSTOMER')
elif nd_MAX in categories_int_to_tuple:
    print('IS CATEGORY')
    print(nd_MAX)
    print(categories_int_to_tuple[nd_MAX])
else:
    print('FUUUUUUUCK')

snap.SaveEdgeList(SubGraph, 'CCG_node_'+str(nd_MAX)+'.csv', 'Subgraph')

exit()