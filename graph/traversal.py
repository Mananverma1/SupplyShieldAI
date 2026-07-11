import networkx as nx

def get_blast_radius(G, source_node):
    """Returns a subgraph of all nodes downstream from the source node."""
    if source_node not in G:
        return nx.DiGraph()
    
    descendants = nx.descendants(G, source_node)
    affected_nodes = descendants.union({source_node})
    return G.subgraph(affected_nodes).copy()

def get_root_causes(G, target_node):
    """Returns a subgraph of all nodes upstream from the target node."""
    if target_node not in G:
        return nx.DiGraph()
    
    ancestors = nx.ancestors(G, target_node)
    cause_nodes = ancestors.union({target_node})
    return G.subgraph(cause_nodes).copy()

def get_path_between(G, source, target):
    """Finds paths between a source and a target."""
    try:
        return list(nx.all_simple_paths(G, source, target))
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return []
