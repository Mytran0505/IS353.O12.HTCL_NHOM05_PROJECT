from collections import Counter
import pickle
import snap
from sys import argv, exit
from random import choice

from project_helpers import read_data_from_binary, customer_product_graph, customer_category_graph, customer_graph, split_communities, standard_recommendation, expert_recommendation, product_similarity, read_customers_original, test_expert_recommendation
from plots import plotDegreeDist, plotDegreeDist_mult

categories_list = {('DVD', '163313'): 'Art House & International',  ('DVD', '163431'): 'Science Fiction & Fantasy', ('Book', '17'): 'Literature & Fiction',     ('Video', '126'): 'Art House & International',  ('Music', '30'): 'Alternative Rock',        ('Music', '42'): 'Soundtracks',                 ('Book', '53'): 'Nonfiction', \
                    ('Book', '18'): 'Mystery & Thrillers',          ('Video', '129'): 'Drama',                      ('Book', '28'): 'Teens',                    ('Book', '4'): 'Children\'s Books',             ('Book', '20'): 'Parenting & Families',     ('Book', '9'): 'History',                       ('DVD', '163345'): 'Classics',                  ('DVD', '163379'): 'Drama',                   ('Music', '37'): 'Pop',\
                    ('Music', '7'): 'Dance & DJ',                   ('Book', '22'): 'Religion & Spirituality',      ('Book', '10'): 'Health, Mind & Body',      ('Book', '26'): 'Sports',                       ('DVD', '163357'): 'Comedy',                ('Video', '132'): 'Kids & Family',              ('DVD', '163414'): 'Kids & Family', ('DVD', '163296'): 'Action & Adventure',        ('Video', '144'): 'Science Fiction & Fantasy', \
                    ('Video', '141'): 'Action & Adventure',         ('DVD', '508532'): 'Documentary',               ('Video', '131'): 'Horror',                 ('DVD', '512030'): 'Mystery & Suspense',        ('Book', '75'): 'Science',                  ('Book', '25'): 'Science Fiction & Fantasy',    ('Book', '49'): 'Horror',           ('Book', '23'): 'Romance',                      ('Video', '128'): 'Comedy', \
                    ('DVD', '466674'): 'Cult Movies',               ('Book', '27'): 'Travel',                       ('DVD', '467970'): 'Sports',                ('DVD', '163396'): 'Horror',                    ('DVD', '163312'): 'Westerns',              ('Music', '40'): 'Rock',                        ('DVD', '163450'): 'Television',    ('Video', '136'): 'Television',                 ('Book', '1'): 'Arts & Photography',     		('Book', '21'): 'Reference', \
                    ('Book', '6'): 'Cooking, Food & Wine',          ('Music', '84'): 'Opera & Vocal',               ('Music', '85'): 'Classical',               ('DVD', '517956'): 'Anime & Manga',             ('DVD', '586156'): 'Military & War',        ('Book', '5'): 'Computers & Internet',                          ('Video', '133'): 'Music Video & Concerts',      \
                                             ('Music', '34'): 'Jazz',                        ('Book', '2'): 'Biographies & Memoirs',                               ('Video', '135'): 'Special Interests',      ('Book', '3'): 'Business & Investing',       ('Music', '33'): 'International',   			('DVD', '163420'): 'Music Video & Concerts',    ('Music', '32'): 'Folk',                            ('Music', '39'): 'R&B', \
                    ('DVD', '508528'): 'Musicals & Performing Arts',('DVD', '163448'): 'Special Interests',         ('DVD', '578324'): 'Fitness & Yoga',        ('DVD', '712256'): 'Animation',                 ('Music', '38'): 'Rap & Hip-Hop',           ('Music', '35'): 'Miscellaneous',               ('Book', '86'): 'Miscellaneous',    ('Book', '48'): 'Home & Garden',                ('Music', '31'):  'Blues', \
                    ('Music', '16'): 'Country',                     ('Book', '87'): 'Computer & Video Games',       ('Music', '36'): 'New Age',                 ('Video', '127'): 'Classics',                   ('DVD', '290738'): 'Educational',                                                   		('DVD', '538708'): 'African American Cinema',                                 ('DVD', '301667'): 'Gay & Lesbian'}#('Book', '8'): None,('Book', '12'): None, ('Book', '19'): None, ('Music', '21'): None, ('Book', '90'): None, ('Book', '11'): None, ('Book', '0'): None,  ('Music', '20'): None,('Book', '32'): None}

def create_CPG(customers):
	### Create Customer-Product Graph ###

	C_P_graph, cust_num, customers_int_to_string, products_int_to_string, customer_product_weights, _ = customer_product_graph(customers)
	snap.SaveEdgeList(C_P_graph, 'C_P_graph', 'Customer-Product graph edgeslist')
	p = open("customer_product_graph.pkl", "wb")

	pickle.dump(customers_int_to_string, p)
	print('customers_int_to_string')
	print(len(customers_int_to_string)) # 9,740

	pickle.dump(products_int_to_string, p)
	print('products_int_to_string')
	print(len(products_int_to_string)) # 37,964

	pickle.dump(customer_product_weights, p)

	return C_P_graph, cust_num, customers_int_to_string, products_int_to_string, customer_product_weights

def create_CCG(products, C_P_graph, cust_num, customers_int_to_string, products_int_to_string, customer_product_weights):
	### Create Customer-Category Graph ###

	C_C_graph, categories_int_to_tuple, categories_to_products, customer_category_weights = customer_category_graph(C_P_graph, products, cust_num, customers_int_to_string, products_int_to_string, customer_product_weights)
	snap.SaveEdgeList(C_C_graph, 'C_C_graph', 'Customer-Category graph edgeslist')
	p = open("customer_category_graph.pkl", "wb")
	pickle.dump(categories_int_to_tuple, p)
	pickle.dump(categories_to_products, p)
	pickle.dump(customer_category_weights, p)
	p.close()

	return C_C_graph, categories_int_to_tuple, customer_category_weights

def create_CNet(C_C_graph, customers_int_to_string, customer_category_weights, categories_int_to_tuple):
	#### CREATE CUSTOMER NET ####

	threshhold = 0.5
	C_Net, customer_weights = customer_graph(C_C_graph, customers_int_to_string, customer_category_weights, categories_int_to_tuple, threshhold)
	snap.SaveEdgeList(C_Net, 'C_Net', 'Customer network edgeslist')

	Cs = split_communities(C_Net)
	Cs = [list(c) for c in Cs]
	# 0 - 3309 nodes
	# 1 - 1604 nodes
	# 2 - 4144 nodes

	p = open("customer_graph.pkl", "wb")
	pickle.dump(customer_weights, p)
	pickle.dump(Cs, p)
	p.close()

	return C_Net, customer_weights

### CREATE GRAPHS - RUN ONCE ###
def create_graphs():
	customers, products = read_data_from_binary()
	C_P_graph, cust_num, customers_int_to_string, products_int_to_string, customer_product_weights = create_CPG(customers)
	print(C_P_graph.GetNodes()) # 47704
	print(C_P_graph.GetEdges()) # 75407
	'''
	# Re-write reduced customers file after sampling
	cust_remaining = customers_int_to_string.values()
	customers_new = {}
	for c in customers:
		if c in cust_remaining:
			customers_new[c] = customers[c]
	c = open("customers.pkl", "wb")
	pickle.dump(customers_new, c)
	c.close()
	'''
	C_C_graph, categories_int_to_tuple, customer_category_weights = create_CCG(products, C_P_graph, cust_num, customers_int_to_string, products_int_to_string, customer_product_weights)
	print(C_C_graph.GetNodes()) # 9824 - so 84 product categories
	print(C_C_graph.GetEdges()) # 44040

	print('CHECK-in')
	print(len(customers_int_to_string)) # 9740
	# HERE customers_int_to_string should run from 0 to C_C_graph.GetNodes() - does it?

	C_Net, customer_weights = create_CNet(C_C_graph, customers_int_to_string, customer_category_weights, categories_int_to_tuple)
	print(C_Net.GetNodes())	# Nodes: 9,055 - (degree 0: )
	print(C_Net.GetEdges()) # Edges: 9,120,620

	print('CREATED REDUCED GRAPHS')

## SHOULD BE COMMENTED OUT ##
create_graphs()

################ READ CP GRAPH #################

customers, products = read_data_from_binary()

C_P_graph = snap.LoadEdgeList(snap.PUNGraph, "C_P_graph", 0, 1)

p = open("customer_product_graph.pkl", "rb")
customers_int_to_string = pickle.load(p)
products_int_to_string = pickle.load(p)
customer_product_weights = pickle.load(p)
p.close()

# Visualize C_P_graph
#plotDegreeDist(C_P_graph, 'Customer - Product Graph Degree Distribution', 'r', 100, 0.00001)
#plotDegreeDist_mult(C_P_graph, 'Customer - Product Graph Degree Distribution', 'r', 100, 0.00001, customers_int_to_string, 'Products')

print(C_P_graph.GetNodes()) # 9799 customers
print(C_P_graph.GetEdges()) # 44040
print(snap.GetClustCf(C_P_graph, 1000))

print(len(customers_int_to_string)) # 9,740
products_string_to_int = {y:x for x,y in products_int_to_string.iteritems()}
print('-----------------------------------------')
################ READ CC GRAPH ##################

C_C_graph = snap.LoadEdgeList(snap.PUNGraph, "C_C_graph", 0, 1)

p = open("customer_category_graph.pkl", "rb")
categories_int_to_tuple = pickle.load(p)
categories_to_products = pickle.load(p)
customer_category_weights = pickle.load(p)
p.close()

# Visualize C_P_graph
#plotDegreeDist(C_C_graph, 'Customer - Category Graph Degree Distribution', 'g', 10000, 0.0001)
#plotDegreeDist_mult(C_C_graph, 'Customer - Category Graph Degree Distribution', 'g', 10000, 0.00005, customers_int_to_string, 'Categories')

print(C_C_graph.GetNodes()) # 9799 customers
print(C_C_graph.GetEdges()) # 44040
print(snap.GetClustCf(C_C_graph, 1000))

print(len(categories_int_to_tuple)) # 84
print(len(customer_category_weights)) # = number of edges
print('-----------------------------------------')
################# READ C_NET ###################

print('Loading C_Net...')
C_Net = snap.LoadEdgeList(snap.PUNGraph, "C_Net", 0, 1)

p = open("customer_graph.pkl", "rb")
customer_weights = pickle.load(p)
Cs = pickle.load(p)
p.close()

#plotDegreeDist(C_Net, 'Customer Network Degree Distribution', 'g', 10000, 0.0001)

print(C_Net.GetNodes()) # 9057
print(C_Net.GetEdges()) # 8,995,947
print(snap.GetClustCf(C_Net, 100))

print('-----------------------------------------')
print('BEGIN TESTS:')

#node_Id = 118
#tuple_requested = ('DVD', '163357')
#test_expert_recommendation(C_Net, Cs, node_Id, tuple_requested, customers, products, customer_product_weights, customers_int_to_string, products_int_to_string, products_string_to_int, categories_int_to_tuple, categories_to_products, customer_weights)
#exit()

################################################
###			QUERY NETWORK FOR EXPERTS 		###
'''
customer_id = 0
cat_tuple = ('DVD', '163431')

experts, expert_scores, expert_score_info = find_category_experts(C_Net, customers, customer_id, Cs, cat_tuple, customers_int_to_string, products_int_to_string, products_string_to_int, categories_int_to_tuple, categories_to_products)

for i in range(5):
	print(experts[i])
	print(customers_int_to_string[experts[i]])

print(expert_score_info)
'''
################################################
#######				TESTS				 #######
#customer_id = 7000
#cat_tuple = ('Music', '30')

# Products of customer_id
#products_map_i = customers[customers_int_to_string[n]]

################################################
## MORE TESTS ##

#random_node = 7000
#tuple_requested = ('Book', '18')
samples = []
#samples = [(7000, ('Book', '18')), (5000, ('Music', '30')), (3000, ('Music', '84')), (1500, ('Video', '131'))]
#more_samples = [(1234, ('Book', '87')), (2346, ('Book', '87')), (3456, ('Book', '22')), (5678, ('DVD', '578324')), (6789, ('DVD', '578324')), (7890, ('DVD', '517956')), (8000, ('DVD', '517956')), (555, ('DVD', '517956'))]
#samples.extend(more_samples)

# TODO: changed that now;  examine customers with >5 products
custs = []
for nid in C_Net.Nodes():
	id_n = nid.GetId()

	node = C_P_graph.GetNI(id_n)
	n = node.GetId()

	if node.GetDeg() > 10:
		custs.append(n)
		
for i in range(100):
	samples.append((choice(custs), choice(categories_list.keys())))

customers_LARGE = read_customers_original()
CP_LARGE, a, b, c, customer_product_weights_LARGE, products_string_to_int_LARGE = customer_product_graph(customers_LARGE)

acc_sum = 0.0
acc_n = 0.0
acc_std = []
acc_exp = []
acc_better = 0.0

iters = 100
#si = 0

for random_node, tuple_requested in samples:

	print('----------------------------------------------')
	print(random_node)
	print(tuple_requested)
	print('--------------')
	print("what the node has actually ordered")
	random_cust_map = customers[customers_int_to_string[random_node]]
	random_cust_purchases = []
	existing_names = set()

	for p in random_cust_map.keys():
		if products[p]['title'] not in existing_names:
			random_cust_purchases.append(p)
			existing_names.add(products[p]['title'])

	#print(random_cust_purchases)
	for p in random_cust_purchases:
		print(p)
		print(products[p]['title'])

	############ STANDARRD RECOMMENDATIONS #########

	#random_node = C_P_graph.GetRndNId()
	top_3_products_std = standard_recommendation(C_P_graph, random_node , tuple_requested , customers, products, customer_product_weights, customers_int_to_string)
	print("recommended products by the standard approach")
	#print(top_3_products)
	for p in top_3_products_std:
		print(p)
		print(products[p]['title'])

	#######		EXPERT RECOMMENDATIONS	    #######
	top_3_products_exp = expert_recommendation(C_Net, Cs, random_node, tuple_requested, customers, products, customer_product_weights, customers_int_to_string, products_int_to_string, products_string_to_int, categories_int_to_tuple, categories_to_products, customer_weights)
	print("recommended products by the EXPERT approach")
	#print(top_3_products)
	for p in top_3_products_exp:
		print(p)
		print(products[p]['title'])

	######		COMPUTE AND COMPARE PRODUCT SIMILARITY		######
	sim_std_sum = 0.0
	sim_std_tot = 0.0

	sim_exp_sum = 0.0
	sim_exp_tot = 0.0

	for p1 in top_3_products_std:
		for p2 in random_cust_purchases:
			s = product_similarity(CP_LARGE, products_string_to_int_LARGE[p1], products_string_to_int_LARGE[p2], customers_LARGE, products, customer_product_weights_LARGE)
			sim_std_sum += s
			sim_std_tot += 1

	sim_std_av = sim_std_sum / sim_std_tot
	print('PLEASE GOD BE THIS SMALLER THAN THE NEXT:')
	print(sim_std_av)

	for p1 in top_3_products_exp:
		for p2 in random_cust_purchases:
			s = product_similarity(CP_LARGE, products_string_to_int_LARGE[p1], products_string_to_int_LARGE[p2], customers_LARGE, products, customer_product_weights_LARGE)
			sim_exp_sum += s
			sim_exp_tot += 1

	sim_exp_av = sim_exp_sum / sim_exp_tot
	print('PLEASE GOD BE THIS LARGER THAN THE PREVIOUS')
	print(sim_exp_av)

	acc_sum += sim_exp_av - sim_std_av
	if sim_exp_av - sim_std_av > 0:
		acc_better += 1
	acc_n += 1
	acc_std.append(sim_std_av)
	acc_exp.append(sim_exp_av)

print(acc_std)
print(acc_exp)
print('average SIMILARITY GAIN:')
print(acc_sum)
print('BETTER:')
print(acc_better / acc_n)
