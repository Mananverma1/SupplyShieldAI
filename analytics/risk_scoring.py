"""
Risk Scoring Engine
-------------------
Scores every node in the supply chain graph across four signals:
  1. Lab failures linked via batch edges
  2. Temperature breaches on inbound/outbound transport legs
  3. Customer complaint frequency at the node
  4. Downstream spread (blast-radius size)

Outputs a score 0–100 and one of four levels:
  Safe | Investigate | High Risk | Critical
"""

import pandas as pd
import os
from graph.traversal import get_blast_radius

TEMP_THRESHOLD = 45.0   # °F  – breach if temperature > this
BREACH_WEIGHT  = 15
LAB_FAIL_WEIGHT = 40
COMPLAINT_WEIGHT = 10
SPREAD_WEIGHT    = 35   # normalised by total node count

_LEVEL_THRESHOLDS = [
    (75, "Critical",    "#F15A29"),
    (45, "High Risk",   "#F4B860"),
    (20, "Investigate", "#8B6FD8"),
    (0,  "Safe",        "#7FD1C3"),
]


def _level(score: float):
    for threshold, label, color in _LEVEL_THRESHOLDS:
        if score >= threshold:
            return label, color
    return "Safe", "#7FD1C3"


def score_all_nodes(G, data_dir: str = "data") -> dict:
    """
    Returns  {node_id: {"score": float, "level": str, "color": str,
                         "lab_fail": bool, "breach": bool,
                         "complaints": int, "spread": int}}
    """
    total_nodes = max(G.number_of_nodes(), 1)

    # ── Lab failures ──────────────────────────────────────────────────
    try:
        lab = pd.read_csv(os.path.join(data_dir, "lab_results.csv"))
        failed_batches = set(lab.loc[lab["result"] == "Fail", "batch_id"])
    except Exception:
        failed_batches = set()

    nodes_with_lab_fail: set = set()
    for u, v, ed in G.edges(data=True):
        if ed.get("batch_id") in failed_batches:
            nodes_with_lab_fail.add(u)
            nodes_with_lab_fail.add(v)

    # ── Temperature breaches ─────────────────────────────────────────
    try:
        tlog = pd.read_csv(os.path.join(data_dir, "transport_logs.csv"))
        breached = tlog[tlog["temperature"] > TEMP_THRESHOLD]
        breach_from = set(breached["from_id"])
        breach_to   = set(breached["to_id"])
        breach_nodes = breach_from | breach_to
    except Exception:
        breach_nodes = set()

    # ── Customer complaints ──────────────────────────────────────────
    try:
        comp = pd.read_csv(os.path.join(data_dir, "customer_complaints.csv"))
        store_complaints = comp.groupby("store_id").size().to_dict()
        prod_complaints  = comp.groupby("product_id").size().to_dict()
    except Exception:
        store_complaints = {}
        prod_complaints  = {}

    # ── Score each node ───────────────────────────────────────────────
    results = {}
    for node in G.nodes():
        ntype = G.nodes[node].get("type", "")

        lab_fail = node in nodes_with_lab_fail
        breach   = node in breach_nodes

        complaints = store_complaints.get(node, 0) + prod_complaints.get(node, 0)

        # spread = number of downstream nodes
        try:
            spread = len(get_blast_radius(G, node).nodes()) - 1  # exclude self
        except Exception:
            spread = 0
        spread_pct = min(spread / total_nodes * 100, 100)

        score = 0.0
        if lab_fail:
            score += LAB_FAIL_WEIGHT
        if breach:
            score += BREACH_WEIGHT
        score += min(complaints * COMPLAINT_WEIGHT, 25)
        score += spread_pct * (SPREAD_WEIGHT / 100)

        score = min(round(score, 1), 100)
        level, color = _level(score)

        results[node] = {
            "score":      score,
            "level":      level,
            "color":      color,
            "lab_fail":   lab_fail,
            "breach":     breach,
            "complaints": int(complaints),
            "spread":     int(spread),
            "type":       ntype,
            "label":      G.nodes[node].get("label", node),
        }

    return results


def get_network_risk_summary(scores: dict) -> dict:
    """High-level counts per level for the dashboard."""
    counts = {"Critical": 0, "High Risk": 0, "Investigate": 0, "Safe": 0}
    for v in scores.values():
        counts[v["level"]] = counts.get(v["level"], 0) + 1
    return counts


def get_recall_efficiency(G, affected_nodes: set) -> dict:
    """
    Recall efficiency = targeted recall scope vs. full national scope.
    Returns percentage saved and absolute numbers.
    """
    total    = G.number_of_nodes()
    targeted = len(affected_nodes)
    saved    = total - targeted
    efficiency = round((saved / total) * 100, 1) if total else 0
    return {
        "total_nodes":   total,
        "targeted":      targeted,
        "saved":         saved,
        "efficiency_pct": efficiency,
    }
