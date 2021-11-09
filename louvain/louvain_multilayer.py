# Basic usage
import community as community_louvain
import networkx as nx

from matplotlib import pyplot as plt


G = nx.erdos_renyi_graph(100, 0.01)
partition = community_louvain.generate_dendrogram(G)

plt.figure(figsize=(10, 10))
plt.axis('off')
nx.draw_networkx(G)
outfile = "louvain_multilayer.pdf"
plt.savefig(outfile)
plt.close()