import pandas as pd
import networkx as nx
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def build_supply_chain_graph(data_dir=None):
    """Build a graph without losing distinct batch movements between two nodes."""
    data_dir = Path(data_dir) if data_dir is not None else PROJECT_ROOT / "data"
    G = nx.MultiDiGraph()
    
    # Load nodes
    suppliers = pd.read_csv(data_dir / "suppliers.csv")
    dcs = pd.read_csv(data_dir / "distribution_centers.csv")
    kitchens = pd.read_csv(data_dir / "kitchens.csv")
    stores = pd.read_csv(data_dir / "stores.csv")
    products = pd.read_csv(data_dir / "products.csv")
    
    # Add nodes with types
    for _, row in suppliers.iterrows():
        G.add_node(row['id'], type='Supplier', label=row['name'], location=row['location'])
    for _, row in dcs.iterrows():
        G.add_node(row['id'], type='Distribution Center', label=row['name'], location=row['location'])
    for _, row in kitchens.iterrows():
        G.add_node(row['id'], type='Kitchen', label=row['name'], location=row['location'])
    for _, row in stores.iterrows():
        G.add_node(row['id'], type='Store', label=row['name'], location=row['location'])
    for _, row in products.iterrows():
        G.add_node(row['id'], type='Product', label=row['name'], category=row['category'])
        
    # Load relationships
    relationships = pd.read_csv(data_dir / "relationships.csv")
    
    for _, row in relationships.iterrows():
        G.add_edge(row['source'], row['target'], relationship_type=row['relationship_type'], batch_id=row['batch_id'])
        
    return G

def get_node_details(G, node_id):
    if node_id in G:
        return G.nodes[node_id]
    return None
