from collections import Counter
from matplotlib import pyplot as plt
import pickle
import snap
from math import sqrt
from random import choice, sample
import numpy as np

threshold = 3.5

# Unpickle and return customers and products maps
def read_data_from_binary():
    print('Loading data... This takes ~ 90 seconds')

    # key: ASIN, value: {title (string), group (string), categories (set of category Ids), reviews (list of customer Ids)}
    p = open("products.pkl", "rb")
    products = pickle.load(p)
    p.close()

    # key: Id, value: {ASIN: [rating, votes, helpful]} of products purchased 
    c = open("customers.pkl", "rb")
    customers = pickle.load(c)
    c.close()

    print('Loading done!')
    return customers, products

def read_customers_original():
    c = open("backups/customers.pkl", "rb")
    customers_original = pickle.load(c)
    c.close()
    return customers_original

# Creates Customer-Product graph
def customer_product_graph(customers):
    customers_string_to_int = {}
    products_string_to_int = {}
    customer_product_weights = {} 

    C_P_graph = snap.TUNGraph.New() 

    cust_num = len(customers)

    customer_counter = 0 
    product_counter = 0 

    for customer_i in customers:
        products_map_i = customers[customer_i]
        num_prod_i = len(products_map_i)

        # If bought less than 3 products, discard
        if num_prod_i < 3:
            continue

        if num_prod_i > 95:
            print('MORE THAN 100')
            continue

        if np.random.uniform() < 0.98:
            continue

        # Add customer node to graph
        customers_string_to_int[customer_i] = customer_counter # maps string customer id to an integer id 
        C_P_graph.AddNode(customer_counter)
        customer_counter += 1

        for product_j in products_map_i: #loop over each product the customer bought
            # if product not seen before, add as a node in graph. 
            if (product_j not in products_string_to_int): 
                products_string_to_int[product_j] = product_counter + cust_num
                C_P_graph.AddNode(product_counter + cust_num) 
                product_counter += 1    

            # Add edge, store edge weight in map
            values_of_product = customers[customer_i][product_j]
            product_rating = values_of_product[0]
            C_P_graph.AddEdge(customers_string_to_int[customer_i], products_string_to_int[product_j])
            customer_product_weights[(customers_string_to_int[customer_i], products_string_to_int[product_j])] = product_rating

    customers_int_to_string = {y:x for x,y in customers_string_to_int.iteritems()}
    products_int_to_string = {y:x for x,y in products_string_to_int.iteritems()}

    return C_P_graph, cust_num, customers_int_to_string, products_int_to_string, customer_product_weights, products_string_to_int

# Creates Customer-Category graph
def customer_category_graph(C_P_graph, products, cust_num, customers_int_to_string, products_int_to_string, customer_product_weights):
    categories_tuple_to_int = {} # key: unique int, value: tuple (Group, category #)
    categories_to_products = {} # key: tuple (Group, category #), value: set() of product graph ids
    customer_category_weights = Counter()
    customer_category_n_edges = Counter()

    C_C_graph = snap.TUNGraph.New()
    for nid in customers_int_to_string:
        #print(nid)
        C_C_graph.AddNode(nid)

    categories_counter = 0

    for customer_i in customers_int_to_string:
        customer_i_node = C_P_graph.GetNI(customer_i)
        customer_i_degree = customer_i_node.GetDeg()

        for j in range(customer_i_degree):
            product_j_id = customer_i_node.GetNbrNId(j) # this is a product id
            categories_j = products[products_int_to_string[product_j_id]]['categories']
            group_j = products[products_int_to_string[product_j_id]]['group']

            for c in categories_j:
                tuple_j_c = (group_j, c)

                # Add this node if doesn't exist
                if tuple_j_c not in categories_to_products:
                    categories_to_products[tuple_j_c] = set()
                    C_C_graph.AddNode(cust_num + categories_counter)
                    categories_tuple_to_int[tuple_j_c] = cust_num + categories_counter
                    categories_counter += 1
                
                tuple_id = categories_tuple_to_int[tuple_j_c]

                # Add product to node
                categories_to_products[tuple_j_c].add(product_j_id)

                # Add edge between
                C_C_graph.AddEdge(tuple_id, customer_i)
                customer_category_weights[(customer_i, tuple_id)] += customer_product_weights[(customer_i, product_j_id)]
                customer_category_n_edges[(customer_i, tuple_id)] += 1.0

    # Normalize edge weights, bring between 0 and 1!
    for t in customer_category_weights:
        customer_category_weights[t] /= (5 * customer_category_n_edges[t])

    categories_int_to_tuple = {y:x for x,y in categories_tuple_to_int.iteritems()}

    return C_C_graph, categories_int_to_tuple, categories_to_products, customer_category_weights

# Creates Customer Network
def customer_graph(C_C_graph, customers_int_to_string, customer_category_weights, categories_int_to_tuple, threshhold):
    customer_weights = Counter()
    customer_n_edges = Counter()

    C_Net = snap.TUNGraph.New()
    for n in C_C_graph.Nodes():
        nid = n.GetId()
        if nid in customers_int_to_string:
            C_Net.AddNode(nid)

    # Pre-process categories
    cat_degree = {}
    cat_neighbors = {}

    for category_j in categories_int_to_tuple:
        category_j_node = C_C_graph.GetNI(category_j)
        cat_degree[category_j] = category_j_node.GetDeg()
        cat_n = []
        for k in range(cat_degree[category_j]):
            n = category_j_node.GetNbrNId(k)
            if len(cat_n) != 0:
                assert(n > cat_n[-1])
            cat_n.append(n)
        cat_neighbors[category_j] = cat_n
    
    # for each pair of customers, find all common neighbors (categories)
    # add +1 if they both liked or disliked, +0 if dissimilar
        # either way, +1 to count
    for customer_i in customers_int_to_string:
        # some nodes were lost in edgelist because they had no edges
        if not C_Net.IsNode(customer_i):
            continue

        customer_i_node = C_C_graph.GetNI(customer_i)
        customer_i_degree = customer_i_node.GetDeg()
        customer_i_categories = []

        # find purchased categories (neighbors)
        for j in range(customer_i_degree):
            category_j = customer_i_node.GetNbrNId(j)
            category_degree = cat_degree[category_j]

            rating_i = customer_category_weights[(customer_i, category_j)]

            # Add edges between customer_i and 2-hop neighbors thru category j, 
            #     depending on similar tastes
            for neigh_k in cat_neighbors[category_j]:
                if neigh_k <= customer_i:
                    continue
                rating_j = customer_category_weights[(neigh_k, category_j)]
                
                if (rating_i >= threshhold + 0.2 and rating_j >= threshhold + 0.2) or \
                   (rating_i <= threshhold - 0.2 and rating_j <= threshhold - 0.2):
                    if customer_weights[(customer_i, neigh_k)] == 0:
                        #i.e. if edge doesn't exist yet
                        C_Net.AddEdge(customer_i, neigh_k)
                    customer_weights[(customer_i, neigh_k)] += 1.0
                    customer_n_edges[(customer_i, neigh_k)] += 1.0
                elif customer_n_edges[(customer_i, neigh_k)] != 0:
                    customer_n_edges[(customer_i, neigh_k)] += 1.0

    # Normalize edge weights, bring between 0 and 1!
    print('length')
    print(len(customer_weights)) # 9120642

    # Retain edges above threshhold
    for t in customer_weights:
        customer_weights[t] /= customer_n_edges[t]
        if customer_weights[t] < threshhold: # remove weak edges
            C_Net.DelEdge(t[0], t[1])

    # Remove low-degree nodes
    for n in C_Net.Nodes():
        nid = n.GetId()
        d = n.GetDeg()
        if d < 5:
            C_Net.DelNode(nid)

    return C_Net, customer_weights

def split_communities(C_Net):
    CmtyV = snap.TCnComV()
    modularity = snap.CommunityCNM(C_Net, CmtyV)
    print(len(CmtyV)) # number of communities
    Cs = []
    for Cmty in CmtyV:
        NIdV = snap.TIntV()
        for NI in Cmty:
            NIdV.Add(NI)
        Cs.append(NIdV)
    return Cs

# PRODUCTS
# key: ASIN, value: {title (string), group (string), categories (set of category Ids), reviews (list of customer Ids)}

# CUSTOMERS
# key: Id, value: {ASIN: [rating, votes, helpful]} of products purchased 

# Given customer_i, category tuple (group, category_id), return 5 highest-rating experts within their community
# Cs is community assignments; cat-tuple is of the form ('DVD', '163431')
def find_category_experts(C_Net, customers, customer_id, Cs, cat_tuple, customers_int_to_string, products_int_to_string, products_string_to_int, categories_int_to_tuple, categories_to_products, customer_weights):
    # Sanity checks
    if not C_Net.IsNode(customer_id):
        print('No customer with ID = ' + str(customer_id) + ' in C_Net. Quitting...')
        exit()
    if not cat_tuple in categories_int_to_tuple.values():
        print('No tuple (' + str(cat_tuple[0]) + ', ' + str(cat_tuple[1]) + ') in categories_int_to_tuple. Quitting...')
        exit()

    c = -1 # community of customer customer_id
    for comm in range(len(Cs)):
        if customer_id in Cs[comm]:
            c = comm
            break

    expert_scores = {}
    expert_score_info = {}
    category_products = categories_to_products[cat_tuple]
    # for every node in the community
    for nid in C_Net.Nodes():
        n = nid.GetId()
        products_map_i = customers[customers_int_to_string[n]]
        total_products_n = len(products_map_i)
        products_revelant = 0.0
        products_helful_votes = 0.0
        products_total_votes = 0.0
        products_sum_ratings = 0.0
        frac_helpful = 0.0
        av_rating = 0.0

        for prod in products_map_i:
            # if product belongs to tuple category
            if products_string_to_int[prod] in category_products:
                products_revelant += 1
                products_helful_votes += products_map_i[prod][2]
                products_total_votes += products_map_i[prod][1]
                products_sum_ratings += products_map_i[prod][0]

        # compute fraction of reviews posted on cat_tuple products
        frac_reviews = products_revelant / total_products_n
        # compute average rating
        if products_revelant != 0:
            av_rating = products_sum_ratings / products_revelant
        # compute fraction of helpful reviews on products of category
        if products_total_votes != 0:
            frac_helpful = products_helful_votes / products_total_votes
        else:
            frac_helpful = 0.3 # nobody has rated the review, fair prior

        # finally, compute expert score
        sh_path = snap.GetShortPath(C_Net, customer_id, n)         # TODO: try removing total_products_n
        expert_scores[n] =  frac_reviews * frac_helpful * av_rating * (1 / np.log(sh_path + 1)) * customer_weights[(min(n, customer_id), max(n, customer_id))] * np.log(total_products_n + 1)
        expert_score_info[n] = [frac_reviews, frac_helpful, total_products_n, customer_weights[(min(n, customer_id), max(n, customer_id))]]
    # Return 100 experts ranked
    experts = sorted(expert_scores, key=expert_scores.get, reverse=True)[:100]
    return experts, expert_scores, expert_score_info

def ten_most_similar_cust(graph, cust_Id, customer_product_weights, customers_int_to_string):
    global threshold 

    customers_to_JA_likes = {}
    customers_to_JA_dislikes = {}

    # find neighbors of that node 
    customer = graph.GetNI(cust_Id)
    neigh_count = customer.GetDeg()
    customer_products_liked = set()
    customer_products_disliked = set() 

    for z in range(0 , neigh_count): 
        product_purchased = customer.GetNbrNId(z)
        product_liking = customer_product_weights[(cust_Id, product_purchased)] 
        if (product_liking >= threshold):
            customer_products_liked.add(product_purchased) 
        elif product_liking <= threshold - 1:
            customer_products_disliked.add(product_purchased)

    # For all other customers, find products they purchased. 
    all_cust_ids = customers_int_to_string.keys()
    for a in range(0, len(all_cust_ids)): 
        cust_id_a = all_cust_ids[a]
        #print(cust_id_a)
        if (cust_id_a != customer): 
            cust_a = graph.GetNI(cust_id_a) 
            a_neigh_count = cust_a.GetDeg() 
            a_neighbors_liked = set()
            a_neighbors_disliked = set()  
        for b in range(0 , a_neigh_count): 
            neigh_b_id = cust_a.GetNbrNId(b) 
            neigh_b_weight = customer_product_weights[(cust_id_a, neigh_b_id)]
            if (neigh_b_weight >= threshold):
                a_neighbors_liked.add(neigh_b_id) 
            elif product_liking <= threshold - 1:
                a_neighbors_disliked.add(neigh_b_id)
                
            
        # compute metrics on a_neighbors and customer_products
        intersection_liked = customer_products_liked.intersection(a_neighbors_liked)
        union_liked = customer_products_liked.union(a_neighbors_liked) 
        
        if (len(union_liked) == 0):
            JA_like = 0 #to prevent division by zero 
        else: 
            JA_like = float(len(intersection_liked))/ len(union_liked)
        customers_to_JA_likes[cust_id_a] = JA_like

        intersection_disliked = customer_products_disliked.intersection(a_neighbors_disliked)
        union_disliked = customer_products_disliked.union(a_neighbors_disliked)

        if (len(union_disliked) == 0):
            JA_dislike = 0
        else:
            JA_dislike = float(len(intersection_disliked))/ len(union_disliked) 

        customers_to_JA_dislikes[cust_id_a] = JA_dislike

        customers_to_JA = {}
        for customer in customers_to_JA_likes:
            customers_to_JA[customer] = 2 * customers_to_JA_likes[customer] + customers_to_JA_dislikes[customer]

    #this list has the ids of the 10 most similar customers to a given customer    
    JA_top = sorted(customers_to_JA, key=customers_to_JA.get, reverse=True)
    return JA_top

# Returns recommended products
def recommendation(graph, node_Id, tuple_requested, customers, products, customer_product_weights, customers_int_to_string, neighbors):
    global threshold

    possible_products = {} #product id to score
    possible_products_names = set()
    #main_cust_purchases = customers[node_Id].keys()
    main_cust_map = customers[customers_int_to_string[node_Id]]
    main_cust_purchases = main_cust_map.keys()

    group_requested = tuple_requested[0]
    cat_requested = tuple_requested[1]
    i = 0

    #find the top 3 products of the requested category (3 with highest ratings)
    for similar_node in neighbors:
        all_purchases = customers[customers_int_to_string[similar_node]] #that is a map 
        i += 1
        for product_key in all_purchases:
            product_features = products[product_key] #this is also a map 
            product_group = product_features["group"]
            product_categories = product_features["categories"]

            # TODO: Switch this around, to make more general?
            if (product_group == group_requested and cat_requested in product_categories):
                rating = all_purchases[product_key][0]
                if product_key in main_cust_purchases:
                    continue
                if product_key not in possible_products:
                    if products[product_key]['title'] in possible_products_names:
                        continue
                    possible_products[product_key] = rating
                    possible_products_names.add(products[product_key]['title'])
                else:
                    if(rating > possible_products[product_key]):
                        possible_products[product_key] = rating

        if len(possible_products) >= 10 and i >= 5:
            break

    top_products = sorted(possible_products, key=possible_products.get, reverse=True) #reverse order 
    
    top_20_products = top_products[:5] #TODO: next thing try to choose randomly instead of sort

    #print("possible products")
    #print(possible_products)
    #print("top products")
    #print(top_products)

    return top_20_products
    
def standard_recommendation(graph, node_Id, tuple_requested, customers, products, customer_product_weights, customers_int_to_string):
    #find the ten most similar 
    JA_top = ten_most_similar_cust(graph, node_Id, customer_product_weights, customers_int_to_string)
    return recommendation(graph, node_Id, tuple_requested, customers, products, customer_product_weights, customers_int_to_string, JA_top)

def expert_recommendation(C_Net, Cs, node_Id, tuple_requested, customers, products, customer_product_weights, customers_int_to_string, products_int_to_string, products_string_to_int, categories_int_to_tuple, categories_to_products, customer_weights):
    experts, expert_scores, expert_score_info = find_category_experts(C_Net, customers, node_Id, Cs, tuple_requested, customers_int_to_string, products_int_to_string, products_string_to_int, categories_int_to_tuple, categories_to_products, customer_weights)
    return recommendation(C_Net, node_Id, tuple_requested, customers, products, customer_product_weights, customers_int_to_string, experts)
    
def test_expert_recommendation(C_Net, Cs, node_Id, tuple_requested, customers, products, customer_product_weights, customers_int_to_string, products_int_to_string, products_string_to_int, categories_int_to_tuple, categories_to_products, customer_weights):
    experts, expert_scores, expert_score_info = find_category_experts(C_Net, customers, node_Id, Cs, tuple_requested, customers_int_to_string, products_int_to_string, products_string_to_int, categories_int_to_tuple, categories_to_products, customer_weights)
    print('----------------------')
    for e in experts:
        print(e)
        print(expert_scores[e])
        print(expert_score_info[e])
        print('----------------------')

#Given two products, this method computes their similarity based on the scores that the customers who purchased them BOTH assigned to them. 
def product_similarity(C_P_graph, p1_Id, p2_Id, customers, products, customer_product_weights):
    # key: ASIN, value: {title (string), group (string), categories (set of category Ids), reviews (list of customer Ids)} #PRODUCTS 
    
    # key: Id, value: {ASIN: [rating, votes, helpful]} of products purchased #CUSTOMERS

    #graph: C_P graph (bipartite)
    n1 = C_P_graph.GetNI(p1_Id)
    n2 = C_P_graph.GetNI(p2_Id)

    neigh_1_count = n1.GetDeg()
    neigh_1 = set()
    neigh_2_count = n2.GetDeg()
    neigh_2 = set()

    for z in range(0 , neigh_1_count): 
        customer_1_bought_by = n1.GetNbrNId(z)
        neigh_1.add(customer_1_bought_by) 

    for x in range(0 , neigh_2_count): 
        customer_2_bought_by = n2.GetNbrNId(x)
        neigh_2.add(customer_2_bought_by)

    comm_neigh = neigh_1.intersection(neigh_2)
    sum_both = 0.0
    sum_1_sq = 0.0
    sum_2_sq = 0.0

    for customer in comm_neigh:
        p_1_liking = customer_product_weights[(customer, p1_Id)]
        p_2_liking = customer_product_weights[(customer, p2_Id)]

        sum_both += (p_1_liking * p_2_liking)
        sum_1_sq += (p_1_liking)**2
        sum_2_sq += (p_2_liking)**2 

    if sum_1_sq * sum_2_sq == 0:
        product_sim = 0.2
    else:
        product_sim = sum_both/(sqrt(sum_1_sq)*sqrt(sum_2_sq))

    return product_sim

