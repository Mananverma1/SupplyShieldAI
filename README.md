# 🛡️ SupplyShield AI

> **An Intelligent Food Recall & Supply Chain Traceability Platform powered by Graph Analytics**

SupplyShield AI is an interactive analytics platform that simulates how modern food manufacturers and restaurant chains investigate food contamination incidents, trace affected supply chain components, and generate targeted recall strategies.

Instead of relying on traditional database joins, SupplyShield AI models the supply chain as a graph, allowing contamination to be traced across suppliers, distribution centers, kitchens, stores, and finished products in real time.

Designed as a portfolio project, SupplyShield AI demonstrates practical applications of **graph analytics, data visualization, supply chain intelligence, business analytics, and decision support systems** using Python.

---

# 📖 Table of Contents

- Project Overview
- Features
- System Workflow
- Architecture
- Technology Stack
- Project Structure
- Dataset
- Analytics Modules
- Graph Analytics
- Dashboard
- Installation
- Usage
- Future Improvements
- Learning Outcomes
- Screenshots
- License

---

# 🚀 Project Overview

Food contamination incidents can rapidly affect thousands of products across multiple locations. Identifying the complete impact quickly is critical to reducing health risks, minimizing waste, and lowering recall costs.

SupplyShield AI simulates this process by modeling a restaurant supply chain as a graph network.

The platform enables users to:

- Detect contaminated ingredient batches
- Trace contamination throughout the supply chain
- Visualize the contamination blast radius
- Perform root cause analysis
- Generate prioritized recall action plans
- Monitor operational risks
- Explore supply chain relationships interactively

---

# ✨ Features

## 🧪 Food Recall Simulation

- Simulate contamination events
- Select contaminated suppliers or ingredient batches
- Trace downstream impact instantly

---

## 🌐 Supply Chain Graph

Interactive graph visualization showing:

- Suppliers
- Distribution Centers
- Kitchens
- Stores
- Products

Graph traversal is powered using **NetworkX**.

---

## 📊 Executive Dashboard

Real-time business metrics including:

- Total Suppliers
- Distribution Centers
- Kitchens
- Stores
- Products
- Active Supply Routes
- Total Relationships
- Recall Reach
- Estimated Impact

---

## 🚨 Blast Radius Analysis

Automatically identifies:

- Affected distribution centers
- Affected kitchens
- Affected stores
- Affected products

using graph traversal algorithms.

---

## 🔍 Root Cause Analysis

Reverse traversal allows users to identify:

Product → Store → Kitchen → Distribution Center → Supplier

to determine the exact origin of contamination.

---

## ⚠️ Risk Assessment

Each affected node is assigned a recall priority based on:

- Node type
- Graph connectivity
- Downstream impact
- Distribution reach

Priority Levels

- 🔴 Critical
- 🟠 High
- 🟡 Medium
- 🟢 Safe

---

## 🌡 Temperature Monitoring

Monitor transportation and storage conditions including:

- Average temperature
- Cold-chain violations
- Threshold breaches
- Transportation legs

---

## 📄 Recall Action Plan

Automatically generates operational recommendations including:

- Quarantine facilities
- Stop shipments
- Remove products
- Notify stores
- Continue monitoring

---

## 📈 Interactive Visualizations

The dashboard includes:

- Interactive network graphs
- KPI cards
- Pie charts
- Bar charts
- Risk distribution
- Recall summaries

---

## 📥 Export Reports

Generate professional reports for:

- Recall summaries
- Risk analysis
- Impact assessment

---

# ⚙️ System Workflow

```
Lab Reports
Temperature Logs
Quality Checks
Customer Complaints
          │
          ▼
 Contamination Detection
          │
          ▼
Graph Construction
          │
          ▼
Network Traversal
          │
          ▼
Blast Radius Analysis
          │
          ▼
Recall Optimization
          │
          ▼
Action Plan Generation
          │
          ▼
Interactive Dashboard
```

---

# 🏗 Architecture

```
                 SupplyShield AI

                        │
                        ▼

                CSV Data Sources
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
   Suppliers      Distribution     Products
                     Centers

                        │
                        ▼

               NetworkX Graph Model

                        │
       ┌────────────────┼────────────────┐
       ▼                ▼                ▼

 Graph Explorer   Recall Engine   Risk Engine

       │                │                │
       └────────────────┼────────────────┘
                        ▼

             Streamlit Dashboard

                        │
        ┌───────────────┼──────────────┐
        ▼               ▼              ▼

     Charts         Reports      Analytics
```

---

# 🛠 Technology Stack

## Programming

- Python 3.x

---

## Framework

- Streamlit

---

## Data Processing

- Pandas
- NumPy

---

## Graph Analytics

- NetworkX
- PyVis

---

## Visualization

- Plotly

---

## Reporting

- ReportLab

---

## Dataset

- CSV

---

# 📊 Dataset

The project uses structured CSV datasets representing a complete food supply chain.

Entities include:

- Suppliers
- Distribution Centers
- Kitchens
- Stores
- Products
- Supply Relationships
- Temperature Logs
- Lab Test Records
- Quality Inspection Data

---

# 🧠 Graph Analytics

SupplyShield AI models the complete supply chain as a directed graph.

Each entity is represented as a node.

Relationships between facilities become graph edges.

This enables efficient:

- Breadth First Search (BFS)
- Depth First Search (DFS)
- Downstream traversal
- Upstream traversal
- Blast radius analysis
- Root cause tracing

---

# 📈 Dashboard Modules

## 🏠 Executive Dashboard

High-level KPIs and supply chain overview.

---

## 🌐 Graph Explorer

Interactive visualization of the complete network.

---

## 🚨 Recall Simulator

Trigger contamination events and observe downstream impact.

---

## 📊 Metrics Dashboard

Business intelligence metrics and operational summaries.

---

## ⚠️ Risk Analysis

Visualize contamination severity and affected entities.

---

## 🌡 Temperature Monitoring

Analyze transportation temperature logs and cold-chain performance.

---

# 💻 Usage

1. Launch the Streamlit application.
2. Navigate through dashboard modules.
3. Select a contaminated supplier or batch.
4. Run the recall simulation.
5. Visualize affected nodes.
6. Review the generated recall action plan.
7. Export reports if required.

---

# 🎯 Learning Outcomes

This project demonstrates knowledge of:

- Graph Analytics
- Supply Chain Intelligence
- Network Modeling
- Business Intelligence
- Data Visualization
- Graph Traversal Algorithms
- Decision Support Systems
- Operational Analytics
- Streamlit Application Development
- Python Data Engineering

---

# 🔮 Future Improvements

Planned enhancements include:

- Machine Learning based contamination prediction
- Real-time IoT sensor integration
- Batch-level traceability
- Interactive timeline playback
- Neo4j graph database integration
- API integration
- User authentication
- Cloud deployment
- Live dashboard updates
- AI-powered recall recommendations

---

# 📸 Screenshots

Add screenshots here after running the project.

Example:

```
assets/dashboard.png

assets/graph.png

assets/recall.png

assets/risk.png
```

---

# 🤝 Contributing

Contributions, suggestions, and feedback are welcome.

Feel free to fork the repository, open issues, or submit pull requests to improve the project.

---

# 📜 License

This project is intended for educational and portfolio purposes.

---

# 👨‍💻 Author

**Manan Verma**

B.Tech Computer Science (Artificial Intelligence)

Passionate about:

- Artificial Intelligence
- Data Analytics
- Supply Chain Intelligence
- Machine Learning
- Graph Analytics
- Business Intelligence

---

## ⭐ If you found this project interesting, consider giving it a Star!

It helps support the project and motivates future improvements.
