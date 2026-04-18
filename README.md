# Medical Diagnostic Support System

A graph-based medical diagnostic tool using **Semantic Networks**, **Frame-Based Knowledge Representation**, and **Neo4j Graph Database**.

## Features

- **46 diseases** across 12 body-system categories (Respiratory, Cardiovascular, Neurological, etc.)
- **Confidence-scored diagnosis** — enter symptoms, get ranked disease matches with % confidence
- **Modern GUI** — dark-themed Tkinter desktop application with embedded graph visualization
- **CLI interface** — full-featured command-line interface with category browsing, search, and more
- **Semantic network visualization** — clean clustered radial layout diagrams
- **Neo4j integration** — graph database storage with Cypher queries

## Tech Stack

- **Python 3** — core application logic
- **Neo4j** — graph database for storing and querying the semantic network
- **NetworkX** — graph creation and visualization
- **Matplotlib** — network diagram rendering
- **Tkinter** — desktop GUI framework

## Setup

### Prerequisites

1. **Python 3.10+** installed
2. **Neo4j Desktop** installed and a local database created

### Installation

```bash
# Install dependencies
pip install neo4j networkx matplotlib python-docx

# Update Neo4j credentials in main.py and gui.py (line 11-12):
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "your_password_here"
```

### Running

```bash
# Start Neo4j Desktop and ensure your database is RUNNING, then:

# Option 1: GUI Application (recommended)
python gui.py

# Option 2: Command-Line Interface
python main.py
```

## Project Structure

```
medical_project/
├── main.py                 # CLI application + Neo4j integration
├── gui.py                  # Tkinter GUI application
├── medical_dataset.py      # Knowledge base (46 diseases)
├── generate_report.py      # DOCX report generator with diagrams
├── Project_Report.docx     # Generated project report
└── README.md               # This file
```

## How It Works

1. **Knowledge Base** — diseases stored as frames (Python dicts) with slots (properties) and fillers (symptoms, treatments, risk factors)
2. **Database Seeding** — frames are mapped to Neo4j nodes and relationships (Disease, Symptom, Treatment, Category, RiskFactor)
3. **Diagnosis** — Cypher query matches patient symptoms against the graph, computing confidence = matched/total symptoms × 100%
4. **Visualization** — custom clustered radial layout places each disease as a cluster with symptoms orbiting around it

## CLI Commands

| Command | Description |
|---|---|
| `fever, cough, headache` | Diagnose with comma-separated symptoms |
| `list diseases` | Show all 46 diseases |
| `list symptoms` | Show all symptoms |
| `list categories` | Show body-system categories |
| `browse Respiratory` | Browse diseases by category |
| `info Influenza` | Full disease details |
| `treatments Pneumonia` | Treatment lookup |
| `search fever` | Search diseases and symptoms |
| `visualize all` | Full semantic network graph |
| `help` | Command reference |

## Report Generation

```bash
# Generate the DOCX project report with diagrams
python generate_report.py
# Output: Project_Report.docx
```
