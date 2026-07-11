import pandas as pd
import numpy as np
import random
import os
from datetime import datetime, timedelta

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

np.random.seed(42)
random.seed(42)

# --- 1. Nodes ---
def generate_nodes(prefix, count, name_prefix):
    return pd.DataFrame({
        "id": [f"{prefix}-{str(i).zfill(3)}" for i in range(1, count + 1)],
        "name": [f"{name_prefix} {i}" for i in range(1, count + 1)],
        "location": [np.random.choice(["New York", "Chicago", "Los Angeles", "Houston", "Miami", "Seattle"]) for _ in range(count)]
    })

suppliers = generate_nodes("SUP", 5, "Supplier")
dcs = generate_nodes("DC", 4, "Dist Center")
kitchens = generate_nodes("KIT", 8, "Kitchen")
stores = generate_nodes("ST", 15, "Store")
products = pd.DataFrame({
    "id": [f"PRD-{str(i).zfill(3)}" for i in range(1, 21)],
    "name": [f"Product {i}" for i in range(1, 21)],
    "category": [np.random.choice(["Produce", "Meat", "Dairy", "Bakery", "Packaged"]) for _ in range(20)]
})

suppliers.to_csv("data/suppliers.csv", index=False)
dcs.to_csv("data/distribution_centers.csv", index=False)
kitchens.to_csv("data/kitchens.csv", index=False)
stores.to_csv("data/stores.csv", index=False)
products.to_csv("data/products.csv", index=False)

# --- 2. Relationships & Batches ---
# We will generate batches that flow from Supplier -> DC -> Kitchen -> Store -> Product
# Wait, product is typically tied to the batch or it represents the end item.
# For the graph layout: Supplier -> DC -> Kitchen -> Store -> Product
relationships = []
batches = []

for b in range(1, 101):
    batch_id = f"BATCH-{str(b).zfill(4)}"
    sup = suppliers.sample(1).iloc[0]["id"]
    dc = dcs.sample(1).iloc[0]["id"]
    kit = kitchens.sample(1).iloc[0]["id"]
    st = stores.sample(1).iloc[0]["id"]
    prd = products.sample(1).iloc[0]["id"]
    
    date = datetime.now() - timedelta(days=np.random.randint(1, 30))
    status = "Active"
    
    batches.append({
        "batch_id": batch_id,
        "product_id": prd,
        "supplier_id": sup,
        "date": date.strftime("%Y-%m-%d"),
        "status": status
    })
    
    # Supplier to DC
    relationships.append({"source": sup, "target": dc, "relationship_type": "SUPPLIES", "batch_id": batch_id})
    # DC to Kitchen
    relationships.append({"source": dc, "target": kit, "relationship_type": "DISTRIBUTES", "batch_id": batch_id})
    # Kitchen to Store
    relationships.append({"source": kit, "target": st, "relationship_type": "DELIVERS", "batch_id": batch_id})
    # Store to Product (Graph representation)
    relationships.append({"source": st, "target": prd, "relationship_type": "STOCKS", "batch_id": batch_id})

pd.DataFrame(batches).to_csv("data/batches.csv", index=False)
pd.DataFrame(relationships).to_csv("data/relationships.csv", index=False)

# --- 3. Logs & Results ---
lab_results = []
for b in batches:
    if np.random.rand() > 0.95:  # 5% failure rate
        result = "Fail"
    else:
        result = "Pass"
    lab_results.append({
        "batch_id": b["batch_id"],
        "test_date": (datetime.strptime(b["date"], "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d"),
        "test_type": "Pathogen Screen",
        "result": result
    })
pd.DataFrame(lab_results).to_csv("data/lab_results.csv", index=False)

transport_logs = []
for idx, r in enumerate(relationships):
    if r["relationship_type"] in ["SUPPLIES", "DISTRIBUTES", "DELIVERS"]:
        transport_logs.append({
            "log_id": f"TR-{str(idx).zfill(5)}",
            "batch_id": r["batch_id"],
            "from_id": r["source"],
            "to_id": r["target"],
            "temperature": round(np.random.normal(38.0, 5.0), 1) # ~38F average
        })
pd.DataFrame(transport_logs).to_csv("data/transport_logs.csv", index=False)

complaints = []
for _ in range(20):
    st = stores.sample(1).iloc[0]["id"]
    prd = products.sample(1).iloc[0]["id"]
    date = datetime.now() - timedelta(days=np.random.randint(1, 10))
    complaints.append({
        "complaint_id": f"CMP-{str(_).zfill(3)}",
        "store_id": st,
        "product_id": prd,
        "date": date.strftime("%Y-%m-%d"),
        "severity": np.random.choice(["Low", "Medium", "High"]),
        "description": "Customer reported issue."
    })
pd.DataFrame(complaints).to_csv("data/customer_complaints.csv", index=False)

print("Data generation complete.")
