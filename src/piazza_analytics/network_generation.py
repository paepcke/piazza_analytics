import networkx as nx
from utils import *

class Graph:
    def __init__(self,path):
        self.path = path
        self.title = self.path.upper()
        self.nodes,self.weighted_edges = get_nodes_and_edges(path)
        self.nodes = list(self.nodes)
        self.edges = list(self.weighted_edges)
        self.G = nx.DiGraph()
        self.G.add_nodes_from(self.nodes)
        self.G.add_weighted_edges_from(self.weighted_edges)

    def get_page_rank(self,page_rank_out_file):
        pr = nx.pagerank(self.G, alpha=0.9)
        fieldnames = ['user1','pagerank']
        writer = csv.DictWriter(open(page_rank_out_file,'w'), fieldnames=fieldnames)
        for k, v in pr.items():
            writer.writerow({'user1': k,'pagerank':v})
        
        # pr = nx.pagerank_numpy(self.G, alpha=0.9)
        # fieldnames = ['user1','pagerank']
        # writer = csv.DictWriter(open("page_rank_numpy.csv",'w'), fieldnames=fieldnames)
        # for k, v in pr.items():
        #     writer.writerow({'user1': k,'pagerank':v})


        # pr = nx.pagerank_scipy(self.G, alpha=0.9)
        # fieldnames = ['user1','pagerank']
        # writer = csv.DictWriter(open("page_rank_scipy.csv",'w'), fieldnames=fieldnames)
        # for k, v in pr.items():
        #     writer.writerow({'user1': k,'pagerank':v})