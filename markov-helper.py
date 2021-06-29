from networkx.algorithms.bipartite.basic import color
from networkx.drawing.nx_pylab import draw
import numpy as np
import random
import networkx as nx
import matplotlib.pyplot as plt 


#creates random directed graph matrix. i, j is 1 if i beats j. 0 otherwise
def create_random_G(n):
    G = np.zeros((n,n))
    for a in range(n):
        for b in range(a):
            i, j = random.choice([(a,b), (b,a)]) #selects random winner
            G[i][j] = 1
    return G

#returns diagonal matrix of copeland scores
def find_diagCO(G):
    n = len(G)
    diagCO = [[0 for _ in range(n)] for _ in range(n)]
    COlist = [sum(row) for row in G]
    return np.diag(COlist)

# creates the markov move probability matrix from G and the diagonal copeland score matrix
def find_Q(G, diagCO):
    n = len(G)
    return (G + diagCO)/(n-1)

# finds stable probability distribution from move probability matrix. I.e. finds p st. pQ = p. 
# From https://stackoverflow.com/questions/31791728/python-code-explanation-for-stationary-distribution-of-a-markov-chain
def find_p(Q):
    evals, evecs = np.linalg.eig(Q)
    evec1 = evecs[:,np.isclose(evals, 1)]
    #Since np.isclose will return an array, we've indexed with an array
    #so we still have our 2nd axis.  Get rid of it, since it's only size 1.
    evec1 = evec1[:,0]

    stationary = evec1 / evec1.sum()

    #eigs finds complex eigenvalues and eigenvectors, so you'll want the real part.
    stationary = stationary.real
    return stationary

# converts from adjacency matrix to adjacency list
def get_adjacency_list(G):
    n = len(G)
    lst = []
    for i in range(n):
        for j in range(n):
            if G[i][j] == 1:
                lst.append((i,j))
    return lst

#gets coordinates of points around a circle
def get_pos(n, radius):
    pos=[]
    for i in range(n):
        pos.append((radius * np.cos(2*np.pi*i/n), radius * np.sin(2*np.pi*i/n)))
    return pos


def get_color_from_probability(probability):
    rounded_decimal_val = int((probability**0.3)*256)
    #TODO: fix this function
    hexval = hex(rounded_decimal_val)[2:]
    if len(hexval) == 1:
        hexval = "0"+hexval
    return "#8000"+hexval

# returns the markov set given the stationary distribution
def get_markov_set(p):
    maxprob = max(p)
    print(p)
    print(maxprob)
    return [i for i in range(len(p)) if np.around(p[i]-maxprob, 4)==0]

#gets the single elimination winner of a tournament. 1 is 
def play_SE(G):
    remaining = list(range(len(G)))
    played_games = []
    while len(remaining) > 1:
        new = []
        for i in range(0, len(remaining)-1, 2): #the -1 is to avoid crashes for odd n
            a = remaining[i+1]
            b = remaining[i]
            new.append([b,a][int(G[a][b])])
            played_games.append((a,b))
        if len(remaining)%2 == 1:
            new.append(remaining[-1])
        print(played_games, new)
        remaining = new
    return remaining[0], played_games


#draws a tournament with the following options: [TODO: describe options]
def draw_tourney(G,  copeland_set_color = None,  SE_winner_color = None, markov_set_color = None, labels = "default", SE_seed = "default", pos = "default"):
    
    #the following section calculates needed variables only if the settings require them
    n = len(G) #number of vertices
    if labels == "markov" or markov_set_color != None:
        p = get_p(G) # markov probabilities for each vertex
    if labels == "copeland" or copeland_set_color != None:
        co = get_co(G)  # copeland scores for each vertex
    
    if pos == "default":
        pos = get_pos(n, 1)
    
    if labels == "default":
        labels = {i: i for i in range(n)}
    elif labels == "copeland":
        labels = {i : co[i] for i in range(n)}
    elif labels == "markov":
        labels = {i : np.around(p[i], 3) for i in range(n)}
    
    nxG = nx.MultiDiGraph()
    nxG.add_edges_from(get_adjacency_list(G))
    plt.figure(figsize=(7,7))
    nx.draw_networkx_edges(nxG, pos, width = 1, arrowsize = 10, arrows=True, min_source_margin=20, min_target_margin=20)
    nx.draw_networkx_nodes(nxG, pos, node_size=1000, node_color="white", edgecolors="black")

    if copeland_set_color != None:
        copeland_set = get_copeland_set_from_scores(co)
        nx.draw_networkx_nodes(nxG, pos, nodelist = copeland_set, node_size = 1000, node_color = copeland_set_color, edgecolors = "black")

    if markov_set_color != None:
        markov_set = get_markov_set_from_scores(p)
        nx.draw_networkx_nodes(nxG, pos, nodelist = markov_set, node_size=700, node_color="red", edgecolors="black")

    if SE_winner_color != None:
        SE_winner, SE_games = play_SE(G)
        nx.draw_networkx_edges(nxG, pos, edgelist=SE_games, width = 5, arrows=False, edge_color="blue", alpha=0.3, min_source_margin=20, min_target_margin=20)
        nx.draw_networkx_nodes(nxG, pos, nodelist = [SE_winner], node_size=1000, node_color="blue", edgecolors="black")

    nx.draw_networkx_labels(nxG, pos, labels, font_size=10)
    plt.axis("off")
    plt.show()

for _ in range(10):
    G = create_random_G(16)
    diagCO = find_diagCO(G)
    Q = find_Q(G, diagCO)
    print(G)
    p = find_p(Q)
    draw_tourney(G,p)

#TODO: clean everything up
