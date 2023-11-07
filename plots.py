from collections import Counter
from matplotlib import pyplot as plt
import snap
import numpy as np

def plotDegreeDist(Graph, title, c, x_u, y_d):
    distribution = snap.TIntPrV()
    snap.GetInDegCnt(Graph, distribution)
    nodes = Graph.GetNodes()
    
    X, Y = [], []
    for d in distribution:
        X.append(d.GetVal1())
        Y.append(float(d.GetVal2()) / nodes)

    '''
    plt.loglog(X, Y, color = c)
    plt.title(title)
    plt.xlabel('Node Degree (log)')
    plt.ylabel('fraction of nodes(log)')
    plt.show()
    '''
    g = plt.scatter(X, Y, marker='.', color = c)
    plt.xlabel("degree")
    plt.ylabel("fraction of nodes")
    plt.title(title)

    plt.xscale('log')
    plt.yscale('log')

    plt.xlim(1, x_u)
    plt.ylim(y_d, 0.1)

    plt.show()

def plotDegreeDist_mult(Graph, title, c, x_u, y_d, customers_int_to_string, name_other):
    cust_distr = Counter()
    cust_n = 0

    other_distr = Counter()
    other_n = 0

    for n in Graph.Nodes():
        nid = n.GetId()

        if nid in customers_int_to_string:
            cust_distr[n.GetDeg()] +=  1
            cust_n += 1
        else:
            other_distr[n.GetDeg()] +=  1
            other_n += 1

    # Plot degree distributions
    cust_x = []
    cust_y = []
    for i in cust_distr:
        cust_x.append(i)
        cust_y.append(cust_distr[i])

    other_x = []
    other_y = []
    for i in other_distr:
        other_x.append(i)
        other_y.append(other_distr[i])

    # Plot gene distribution
    g = plt.scatter(cust_x, np.array(cust_y)/float(cust_n), alpha=1, marker='.')
    d = plt.scatter(other_x, np.array(other_y)/float(other_n), alpha=1, marker='.')
    plt.xlabel("degree")
    plt.ylabel("fraction of nodes")
    plt.title(title)

    plt.legend((g, d), ('Customers', name_other), fontsize=15)

    plt.xscale('log')
    plt.yscale('log')

    plt.xlim(1, x_u)
    plt.ylim(y_d, 0.1)

    plt.show()