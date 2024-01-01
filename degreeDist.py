from matplotlib import pyplot as plt
import snap

def plotDegreeDist(Graph):
    distribution = snap.TIntPrV()
    snap.GetInDegCnt(Graph, distribution)
    nodes = Graph.GetNodes()
    
    X, Y = [], []
    for d in distribution:
        X.append(d.GetVal1())
        Y.append(float(d.GetVal2()) / nodes)

    plt.loglog(X, Y, color = 'y', label = 'Customer - Product Graph')