import pandas as pd
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

def get_contaminated_batches(data_dir=None):
    """Return failed batches, or an empty list when the source file is unavailable."""
    data_dir = Path(data_dir) if data_dir is not None else PROJECT_ROOT / "data"
    try:
        lab_results = pd.read_csv(data_dir / "lab_results.csv")
    except (OSError, pd.errors.EmptyDataError, pd.errors.ParserError):
        return []

    if not {"batch_id", "result"}.issubset(lab_results.columns):
        return []
    # Filter for Failed results
    failed = lab_results[lab_results["result"] == "Fail"]
    return failed["batch_id"].tolist()

def get_affected_source_nodes(G, data_dir=None):
    contaminated_batches = get_contaminated_batches(data_dir)
    affected_nodes = set()
    
    # Check edges to find where these batches originated or passed through
    for u, v, data in G.edges(data=True):
        if data.get('batch_id') in contaminated_batches:
            affected_nodes.add(u)
            affected_nodes.add(v)
            
    return list(affected_nodes)
