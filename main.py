import networkx as nx
import matplotlib.pyplot as plt
from neo4j import GraphDatabase
from medical_dataset import MEDICAL_KNOWLEDGE_BASE

# ==========================================
# NEO4J CONFIGURATION - UPDATE THESE IF NEEDED
# ==========================================
# Look for your neo4j URI and password in your Neo4j Desktop app.
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "sava4090"  # <-- UPDATE THIS to your Neo4j password

# ==========================================
# TERMINAL COLOR CODES FOR SEVERITY OUTPUT
# ==========================================
class Colors:
    RED = '\033[91m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    CYAN = '\033[96m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'

def severity_color(severity):
    """Return color code based on severity string."""
    sev = severity.lower()
    if "critical" in sev or "high" in sev:
        return Colors.RED
    elif "moderate" in sev:
        return Colors.YELLOW
    elif "mild" in sev or "variable" in sev:
        return Colors.GREEN
    return Colors.RESET


class MedicalKnowledgeBase:
    def __init__(self, uri, user, password):
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            self.driver.verify_connectivity()
            print(f"{Colors.GREEN}✓ Successfully connected to Neo4j Database.{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}✗ Failed to connect to Neo4j. Check your DB, URI, and credentials.{Colors.RESET}")
            print(f"  Error details: {e}")
            self.driver = None

    def close(self):
        if self.driver:
            self.driver.close()

    def seed_database(self):
        """Loads semantic network nodes and frame properties into Neo4j."""
        if not self.driver:
            return
            
        print(f"\n{Colors.CYAN}Seeding database (this will CLEAR existing data)...{Colors.RESET}")
        with self.driver.session() as session:
            # Clear old network data so we don't duplicate nodes
            session.run("MATCH (n) DETACH DELETE n")

            # Insert new semantic network based on `medical_dataset.py`
            for disease_name, frame in MEDICAL_KNOWLEDGE_BASE.items():
                
                # 1. Create Disease Node (Slots mapped to Properties)
                session.run('''
                    CREATE (d:Disease {
                        name: $name, 
                        description: $description, 
                        prevalence: $prevalence, 
                        severity: $severity,
                        category: $category
                    })
                ''', name=disease_name, 
                     description=frame.get("description", ""),
                     prevalence=frame.get("prevalence", ""),
                     severity=frame.get("severity", ""),
                     category=frame.get("category", "General"))

                # 2. Create Category node and link
                category = frame.get("category", "General")
                session.run('''
                    MATCH (d:Disease {name: $d_name})
                    MERGE (c:Category {name: $c_name})
                    MERGE (d)-[:BELONGS_TO]->(c)
                ''', d_name=disease_name, c_name=category)

                # 3. Create Symptoms and relate them to the disease
                for symptom in frame.get("symptoms", []):
                    session.run('''
                        MATCH (d:Disease {name: $d_name})
                        MERGE (s:Symptom {name: $s_name})
                        MERGE (d)-[:HAS_SYMPTOM]->(s)
                    ''', d_name=disease_name, s_name=symptom)

                # 4. Create Treatments and relate them to the disease
                for treatment in frame.get("treatments", []):
                    session.run('''
                        MATCH (d:Disease {name: $d_name})
                        MERGE (t:Treatment {name: $t_name})
                        MERGE (t)-[:TREATS]->(d)
                    ''', d_name=disease_name, t_name=treatment)

                # 5. Create Risk Factors and relate them to the disease
                for risk_factor in frame.get("risk_factors", []):
                    session.run('''
                        MATCH (d:Disease {name: $d_name})
                        MERGE (r:RiskFactor {name: $r_name})
                        MERGE (d)-[:HAS_RISK_FACTOR]->(r)
                    ''', d_name=disease_name, r_name=risk_factor)

        print(f"{Colors.GREEN}✓ Database seeded with {len(MEDICAL_KNOWLEDGE_BASE)} diseases!{Colors.RESET}")

    def diagnose(self, symptoms):
        """Diagnose based on provided symptoms using Cypher queries with confidence scoring."""
        if not self.driver:
            return []
            
        print(f"\n{Colors.BOLD}{'='*50}")
        print(f"  DIAGNOSTIC ENGINE")
        print(f"{'='*50}{Colors.RESET}")
        print(f"  Patient Symptoms: {Colors.CYAN}{', '.join(symptoms)}{Colors.RESET}")
        
        with self.driver.session() as session:
            # Enhanced Cypher query with confidence scoring
            query = '''
                MATCH (d:Disease)-[:HAS_SYMPTOM]->(s:Symptom)
                WITH d, collect(s.name) AS allSymptoms
                WITH d, allSymptoms, size(allSymptoms) AS totalSymptoms
                WITH d, allSymptoms, totalSymptoms,
                     [sym IN allSymptoms WHERE sym IN $patient_symptoms] AS matchedSymptoms
                WITH d, allSymptoms, totalSymptoms, matchedSymptoms,
                     size(matchedSymptoms) AS matchCount
                WHERE matchCount > 0
                RETURN d.name AS Disease,
                       matchCount AS MatchingSymptoms,
                       totalSymptoms AS TotalSymptoms,
                       matchedSymptoms AS MatchedSymptomList,
                       d.severity AS Severity,
                       d.category AS Category,
                       d.description AS Description,
                       toFloat(matchCount) / toFloat(totalSymptoms) * 100 AS Confidence
                ORDER BY Confidence DESC, MatchingSymptoms DESC
                LIMIT 5
            '''
            result = session.run(query, patient_symptoms=symptoms)
            matches = [record for record in result]
            
            if not matches:
                print(f"\n  {Colors.YELLOW}⚠ No clear diagnosis found for these symptoms.{Colors.RESET}")
            else:
                print(f"\n  {Colors.BOLD}Top {len(matches)} Possible Diagnoses:{Colors.RESET}\n")
                for i, record in enumerate(matches, 1):
                    sev_col = severity_color(record['Severity'])
                    confidence = record['Confidence']
                    
                    # Confidence bar
                    bar_length = 20
                    filled = int(confidence / 100 * bar_length)
                    bar = '█' * filled + '░' * (bar_length - filled)
                    
                    print(f"  {Colors.BOLD}{i}. {record['Disease']}{Colors.RESET}")
                    print(f"     Category:   {Colors.BLUE}{record['Category']}{Colors.RESET}")
                    print(f"     Severity:   {sev_col}{record['Severity']}{Colors.RESET}")
                    print(f"     Confidence: [{bar}] {confidence:.1f}%")
                    print(f"     Matched:    {Colors.CYAN}{', '.join(record['MatchedSymptomList'])}{Colors.RESET}")
                    print(f"                 ({record['MatchingSymptoms']}/{record['TotalSymptoms']} symptoms)")
                    print()

                # Show treatments for top diagnosis
                top_disease = matches[0]['Disease']
                treatments = self._get_treatments(top_disease)
                if treatments:
                    print(f"  {Colors.BOLD}Recommended Treatments for \"{top_disease}\":{Colors.RESET}")
                    for t in treatments:
                        print(f"     • {Colors.GREEN}{t}{Colors.RESET}")
                    print()

                # Show risk factors for top diagnosis
                risk_factors = self._get_risk_factors(top_disease)
                if risk_factors:
                    print(f"  {Colors.BOLD}Risk Factors:{Colors.RESET}")
                    for rf in risk_factors:
                        print(f"     ⚡ {Colors.YELLOW}{rf}{Colors.RESET}")
                    print()

            return matches

    def _get_treatments(self, disease_name):
        """Get treatments for a specific disease from Neo4j."""
        if not self.driver:
            return []
        with self.driver.session() as session:
            result = session.run('''
                MATCH (t:Treatment)-[:TREATS]->(d:Disease {name: $name})
                RETURN t.name AS Treatment
            ''', name=disease_name)
            return [record['Treatment'] for record in result]

    def _get_risk_factors(self, disease_name):
        """Get risk factors for a specific disease from Neo4j."""
        if not self.driver:
            return []
        with self.driver.session() as session:
            result = session.run('''
                MATCH (d:Disease {name: $name})-[:HAS_RISK_FACTOR]->(r:RiskFactor)
                RETURN r.name AS RiskFactor
            ''', name=disease_name)
            return [record['RiskFactor'] for record in result]

    def get_disease_info(self, disease_name):
        """Get full details of a disease from Neo4j."""
        if not self.driver:
            return None
        with self.driver.session() as session:
            result = session.run('''
                MATCH (d:Disease {name: $name})
                OPTIONAL MATCH (d)-[:HAS_SYMPTOM]->(s:Symptom)
                OPTIONAL MATCH (t:Treatment)-[:TREATS]->(d)
                OPTIONAL MATCH (d)-[:HAS_RISK_FACTOR]->(r:RiskFactor)
                RETURN d.name AS Name, d.description AS Description,
                       d.severity AS Severity, d.prevalence AS Prevalence,
                       d.category AS Category,
                       collect(DISTINCT s.name) AS Symptoms,
                       collect(DISTINCT t.name) AS Treatments,
                       collect(DISTINCT r.name) AS RiskFactors
            ''', name=disease_name)
            record = result.single()
            return record

    def get_categories(self):
        """Get all disease categories and their counts from Neo4j."""
        if not self.driver:
            return []
        with self.driver.session() as session:
            result = session.run('''
                MATCH (d:Disease)-[:BELONGS_TO]->(c:Category)
                RETURN c.name AS Category, count(d) AS DiseaseCount
                ORDER BY DiseaseCount DESC
            ''')
            return [record for record in result]

    def get_diseases_by_category(self, category):
        """Get all diseases in a specific category."""
        if not self.driver:
            return []
        with self.driver.session() as session:
            result = session.run('''
                MATCH (d:Disease)-[:BELONGS_TO]->(c:Category {name: $category})
                RETURN d.name AS Disease, d.severity AS Severity, d.prevalence AS Prevalence
                ORDER BY d.name
            ''', category=category)
            return [record for record in result]

    def search_keyword(self, keyword):
        """Search for diseases and symptoms containing a keyword."""
        if not self.driver:
            return [], []
        with self.driver.session() as session:
            # Search diseases
            disease_result = session.run('''
                MATCH (d:Disease)
                WHERE toLower(d.name) CONTAINS toLower($keyword)
                   OR toLower(d.description) CONTAINS toLower($keyword)
                RETURN d.name AS Name, d.category AS Category, d.severity AS Severity
                ORDER BY d.name
            ''', keyword=keyword)
            diseases = [record for record in disease_result]

            # Search symptoms
            symptom_result = session.run('''
                MATCH (s:Symptom)<-[:HAS_SYMPTOM]-(d:Disease)
                WHERE toLower(s.name) CONTAINS toLower($keyword)
                RETURN DISTINCT s.name AS Symptom, collect(DISTINCT d.name) AS RelatedDiseases
                ORDER BY s.name
            ''', keyword=keyword)
            symptoms = [record for record in symptom_result]

            return diseases, symptoms

    def visualize_network(self, top_diseases=None, patient_symptoms=None):
        """Fetch relationships from Neo4j and plot them using NetworkX.
        Uses a clean clustered layout so each disease gets its own area."""
        if not self.driver:
            return

        import matplotlib.patches as mpatches
        import math

        print(f"\n{Colors.CYAN}Fetching network from Neo4j for visualization...{Colors.RESET}")

        with self.driver.session() as session:
            if top_diseases and patient_symptoms:
                # --- DIAGNOSIS VIEW: Only show top 3 diseases ---
                show_diseases = top_diseases[:3]
                query = '''
                    MATCH (d:Disease)-[:HAS_SYMPTOM]->(s:Symptom)
                    WHERE d.name IN $diseases
                    RETURN d.name AS Disease, s.name AS Symptom
                '''
                result = session.run(query, diseases=show_diseases)
                # Build per-disease clusters
                disease_symptoms = {}
                for record in result:
                    d_name = record["Disease"]
                    s_name = record["Symptom"]
                    disease_symptoms.setdefault(d_name, []).append(s_name)
            else:
                # --- FULL VIEW: Show all diseases grouped by category ---
                result = session.run('''
                    MATCH (d:Disease)-[:HAS_SYMPTOM]->(s:Symptom)
                    RETURN d.name AS Disease, s.name AS Symptom
                ''')
                disease_symptoms = {}
                for record in result:
                    d_name = record["Disease"]
                    s_name = record["Symptom"]
                    disease_symptoms.setdefault(d_name, []).append(s_name)

        if not disease_symptoms:
            print(f"  {Colors.YELLOW}No data to visualize.{Colors.RESET}")
            return

        n_diseases = len(disease_symptoms)
        print(f"{Colors.CYAN}Drawing clean clustered diagram ({n_diseases} diseases)...{Colors.RESET}")

        # --- Build graph ---
        G = nx.Graph()
        for disease, symptoms in disease_symptoms.items():
            for symptom in symptoms:
                G.add_edge(disease, symptom)

        # --- CUSTOM CLUSTERED LAYOUT ---
        # Place each disease at a point on a large circle,
        # then arrange its symptoms in a smaller circle around it.
        pos = {}
        diseases_list = list(disease_symptoms.keys())

        if top_diseases and patient_symptoms:
            # Diagnosis mode: spread 3 diseases across the canvas
            cluster_radius = 5.0      # distance between disease centers
            symptom_radius = 2.5      # how far symptoms sit from their disease
        else:
            # Full mode: arrange on a larger ring
            cluster_radius = max(12.0, n_diseases * 1.2)
            symptom_radius = max(2.0, min(3.5, cluster_radius / n_diseases * 2.5))

        for i, disease in enumerate(diseases_list):
            # Place disease center on a circle
            angle = 2 * math.pi * i / n_diseases - math.pi / 2
            cx = cluster_radius * math.cos(angle)
            cy = cluster_radius * math.sin(angle)
            pos[disease] = (cx, cy)

            # Place symptoms in a ring around the disease
            syms = disease_symptoms[disease]
            for j, symptom in enumerate(syms):
                s_angle = 2 * math.pi * j / len(syms) - math.pi / 2
                sx = cx + symptom_radius * math.cos(s_angle)
                sy = cy + symptom_radius * math.sin(s_angle)
                # If symptom already placed (shared), average the positions
                if symptom in pos:
                    old_x, old_y = pos[symptom]
                    pos[symptom] = ((old_x + sx) / 2, (old_y + sy) / 2)
                else:
                    pos[symptom] = (sx, sy)

        # --- Classify nodes ---
        disease_color_map = {
            "#ff6b6b": [],  # diagnosed diseases
            "#54a0ff": [],  # other diseases
        }
        matched_symptom_nodes = []
        other_symptom_nodes = []

        # Category colors for full view
        category_colors = {
            "Respiratory": "#54a0ff", "Immunological": "#a29bfe",
            "Neurological": "#fd79a8", "Cardiovascular": "#e17055",
            "Gastrointestinal": "#00b894", "Endocrine": "#fdcb6e",
            "Dermatological": "#e84393", "Psychiatric": "#6c5ce7",
            "Infectious": "#ff7675", "Musculoskeletal": "#00cec9",
            "Renal": "#0984e3", "Hematological": "#d63031",
        }

        node_colors = {}
        node_sizes = {}
        labels_show = {}

        for node in G.nodes():
            if node in disease_symptoms:
                # It's a disease node
                if top_diseases and node in top_diseases:
                    node_colors[node] = '#ff6b6b'
                    node_sizes[node] = 4500
                else:
                    cat = MEDICAL_KNOWLEDGE_BASE.get(node, {}).get("category", "General")
                    node_colors[node] = category_colors.get(cat, '#54a0ff')
                    node_sizes[node] = 3000
                labels_show[node] = node
            elif patient_symptoms and node in patient_symptoms:
                # Matched patient symptom
                node_colors[node] = '#feca57'
                node_sizes[node] = 2200
                labels_show[node] = node
            else:
                # Other symptom
                node_colors[node] = '#dfe6e9'
                node_sizes[node] = 600
                # Only label other symptoms in diagnosis mode (fewer nodes)
                if top_diseases:
                    labels_show[node] = node

        # --- DRAW ---
        fig_w = 24 if not top_diseases else 18
        fig_h = 18 if not top_diseases else 13
        fig, ax = plt.subplots(figsize=(fig_w, fig_h))
        ax.set_facecolor('#f8f9fa')
        fig.patch.set_facecolor('#f8f9fa')

        # Separate edges into matched vs other for styling
        matched_edges = []
        other_edges = []
        for u, v in G.edges():
            if patient_symptoms and (u in patient_symptoms or v in patient_symptoms):
                matched_edges.append((u, v))
            else:
                other_edges.append((u, v))

        # Draw other edges first (faded)
        if other_edges:
            nx.draw_networkx_edges(G, pos, edgelist=other_edges,
                                   width=0.8, alpha=0.15, edge_color='#b2bec3', style='solid', ax=ax)

        # Draw matched edges (highlighted)
        if matched_edges:
            nx.draw_networkx_edges(G, pos, edgelist=matched_edges,
                                   width=2.0, alpha=0.6, edge_color='#fdcb6e', style='solid', ax=ax)

        # Draw nodes
        ordered_nodes = list(G.nodes())
        c_list = [node_colors.get(n, '#dfe6e9') for n in ordered_nodes]
        s_list = [node_sizes.get(n, 600) for n in ordered_nodes]

        nx.draw_networkx_nodes(G, pos, nodelist=ordered_nodes,
                               node_size=s_list, node_color=c_list,
                               alpha=0.92, edgecolors='white', linewidths=2.0, ax=ax)

        # Draw disease labels (bold, boxed)
        disease_labels = {n: l for n, l in labels_show.items() if n in disease_symptoms}
        symptom_labels = {n: l for n, l in labels_show.items() if n not in disease_symptoms}

        nx.draw_networkx_labels(G, pos, labels=disease_labels,
                                font_size=10, font_weight='bold', font_family='sans-serif',
                                bbox=dict(facecolor='white', edgecolor='#ddd', alpha=0.9,
                                          boxstyle='round,pad=0.4'), ax=ax)

        # Draw symptom labels (smaller, clean)
        if top_diseases:
            # In diagnosis view: label matched symptoms bold, others lighter
            matched_labels = {n: l for n, l in symptom_labels.items()
                              if patient_symptoms and n in patient_symptoms}
            other_labels = {n: l for n, l in symptom_labels.items()
                            if not patient_symptoms or n not in patient_symptoms}

            nx.draw_networkx_labels(G, pos, labels=matched_labels,
                                    font_size=9, font_weight='bold', font_family='sans-serif',
                                    font_color='#2d3436',
                                    bbox=dict(facecolor='#ffeaa7', edgecolor='none', alpha=0.8,
                                              boxstyle='round,pad=0.2'), ax=ax)
            nx.draw_networkx_labels(G, pos, labels=other_labels,
                                    font_size=7, font_family='sans-serif',
                                    font_color='#636e72', alpha=0.7, ax=ax)
        else:
            # Full view: skip symptom labels to avoid clutter
            pass

        # --- Title ---
        if top_diseases:
            plt_title = "Patient Diagnosis — Semantic Network"
            subtitle = f"Showing top {len(disease_symptoms)} matched diseases and their symptom clusters"
        else:
            plt_title = "Full Medical Knowledge Base — Semantic Network"
            subtitle = f"{n_diseases} diseases · {G.number_of_edges()} relationships"

        ax.set_title(plt_title, fontsize=18, fontweight='bold', pad=25, color='#2d3436')
        ax.text(0.5, 1.01, subtitle, transform=ax.transAxes, ha='center',
                fontsize=11, color='#636e72', style='italic')

        # --- Legend ---
        if top_diseases:
            legend_elements = [
                mpatches.Patch(color='#ff6b6b', label='Diagnosed Diseases'),
                mpatches.Patch(color='#feca57', label='Your Symptoms (Matched)'),
                mpatches.Patch(color='#dfe6e9', label='Other Disease Symptoms'),
            ]
        else:
            legend_elements = [mpatches.Patch(color=c, label=cat) for cat, c in category_colors.items()]
            legend_elements.append(mpatches.Patch(color='#dfe6e9', label='Symptoms'))

        ax.legend(handles=legend_elements, loc='upper left', prop={'size': 10},
                  framealpha=0.9, fancybox=True, shadow=True,
                  ncol=2 if not top_diseases else 1)

        ax.axis('off')
        plt.tight_layout()
        plt.show()


def print_help():
    """Display all available commands."""
    print(f"\n{Colors.BOLD}{'='*60}")
    print(f"  MEDICAL DIAGNOSTIC SYSTEM — COMMAND REFERENCE")
    print(f"{'='*60}{Colors.RESET}")
    print(f"""
  {Colors.CYAN}DIAGNOSIS:{Colors.RESET}
    {Colors.BOLD}fever, cough, headache{Colors.RESET}     Enter symptoms separated by commas

  {Colors.CYAN}BROWSING:{Colors.RESET}
    {Colors.BOLD}list diseases{Colors.RESET}              List all diseases in the database
    {Colors.BOLD}list symptoms{Colors.RESET}              List all symptoms in the database
    {Colors.BOLD}list categories{Colors.RESET}            Show all body-system categories
    {Colors.BOLD}browse <category>{Colors.RESET}          List diseases in a category
                                 e.g., browse Respiratory

  {Colors.CYAN}DETAILS:{Colors.RESET}
    {Colors.BOLD}info <disease>{Colors.RESET}             Show full disease details
                                 e.g., info Influenza (Flu)
    {Colors.BOLD}treatments <disease>{Colors.RESET}       Show treatments for a disease
                                 e.g., treatments Pneumonia

  {Colors.CYAN}SEARCH:{Colors.RESET}
    {Colors.BOLD}search <keyword>{Colors.RESET}           Search diseases & symptoms by keyword
                                 e.g., search fever

  {Colors.CYAN}VISUALIZATION:{Colors.RESET}
    {Colors.BOLD}visualize all{Colors.RESET}              Show the full semantic network graph

  {Colors.CYAN}SYSTEM:{Colors.RESET}
    {Colors.BOLD}help{Colors.RESET}                       Show this help message
    {Colors.BOLD}exit / quit{Colors.RESET}                Close the application
""")


if __name__ == "__main__":
    db = MedicalKnowledgeBase(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
    if db.driver:
        # NOTE: Uncomment the line below the very first time you run this to populate your database!
        db.seed_database()
        
        print(f"\n{Colors.BOLD}{'='*60}")
        print(f"   ♥  MEDICAL DIAGNOSTIC SUPPORT SYSTEM  ♥")
        print(f"{'='*60}{Colors.RESET}")
        print(f"   {Colors.DIM}Powered by Neo4j Graph Database & Semantic Networks{Colors.RESET}")
        print(f"   {Colors.DIM}{len(MEDICAL_KNOWLEDGE_BASE)} diseases | ", end="")
        total_symptoms = set()
        for d in MEDICAL_KNOWLEDGE_BASE.values():
            total_symptoms.update(d.get("symptoms", []))
        print(f"{len(total_symptoms)} symptoms{Colors.RESET}")
        print(f"\n   Type {Colors.CYAN}help{Colors.RESET} for all commands, or enter symptoms to diagnose.")
        print(f"   Example: {Colors.CYAN}fever, cough, headache{Colors.RESET}\n")
        
        while True:
            try:
                user_input = input(f"{Colors.BOLD}▸ {Colors.RESET}").strip()
            except (KeyboardInterrupt, EOFError):
                print(f"\n{Colors.DIM}Exiting diagnostic system. Goodbye!{Colors.RESET}")
                break
                
            if not user_input:
                continue

            command = user_input.lower()

            # ---- EXIT ----
            if command in ['exit', 'quit']:
                print(f"{Colors.DIM}Exiting diagnostic system. Goodbye!{Colors.RESET}")
                break

            # ---- HELP ----
            elif command == 'help':
                print_help()

            # ---- LIST DISEASES ----
            elif command == 'list diseases':
                diseases = list(MEDICAL_KNOWLEDGE_BASE.keys())
                print(f"\n{Colors.BOLD}  All Diseases ({len(diseases)} total):{Colors.RESET}")
                print(f"  {'─'*50}")
                for i, d in enumerate(sorted(diseases), 1):
                    sev = MEDICAL_KNOWLEDGE_BASE[d].get("severity", "")
                    cat = MEDICAL_KNOWLEDGE_BASE[d].get("category", "")
                    col = severity_color(sev)
                    print(f"  {i:3}. {d:<45} {Colors.BLUE}[{cat}]{Colors.RESET} {col}{sev}{Colors.RESET}")
                print()

            # ---- LIST SYMPTOMS ----
            elif command == 'list symptoms':
                all_symptoms = set()
                for data in MEDICAL_KNOWLEDGE_BASE.values():
                    all_symptoms.update(data.get("symptoms", []))
                sorted_symptoms = sorted(list(all_symptoms))
                
                print(f"\n{Colors.BOLD}  All Symptoms ({len(sorted_symptoms)} total):{Colors.RESET}")
                print(f"  {'─'*50}")
                # Print in 2 columns
                half = (len(sorted_symptoms) + 1) // 2
                for i in range(half):
                    left = f"{i+1:3}. {sorted_symptoms[i]}"
                    right = f"{i+half+1:3}. {sorted_symptoms[i+half]}" if i + half < len(sorted_symptoms) else ""
                    print(f"  {left:<40} {right}")
                print()

            # ---- LIST CATEGORIES ----
            elif command == 'list categories':
                categories = db.get_categories()
                if categories:
                    print(f"\n{Colors.BOLD}  Disease Categories:{Colors.RESET}")
                    print(f"  {'─'*50}")
                    for record in categories:
                        print(f"    {Colors.BLUE}■{Colors.RESET} {record['Category']:<25} ({record['DiseaseCount']} diseases)")
                    print(f"\n  Use {Colors.CYAN}browse <category>{Colors.RESET} to see diseases in a category.\n")
                else:
                    print(f"  {Colors.YELLOW}No categories found. Run seed_database first.{Colors.RESET}")

            # ---- BROWSE CATEGORY ----
            elif command.startswith('browse '):
                category = user_input[7:].strip()
                # Try to match case-insensitively
                matched_cat = None
                for d in MEDICAL_KNOWLEDGE_BASE.values():
                    c = d.get("category", "")
                    if c.lower() == category.lower():
                        matched_cat = c
                        break
                
                if matched_cat:
                    diseases = db.get_diseases_by_category(matched_cat)
                    if diseases:
                        print(f"\n{Colors.BOLD}  {matched_cat} Diseases ({len(diseases)}):{Colors.RESET}")
                        print(f"  {'─'*50}")
                        for i, record in enumerate(diseases, 1):
                            col = severity_color(record['Severity'])
                            print(f"  {i:3}. {record['Disease']:<45} {col}{record['Severity']}{Colors.RESET}")
                        print(f"\n  Use {Colors.CYAN}info <disease name>{Colors.RESET} for full details.\n")
                    else:
                        print(f"  {Colors.YELLOW}No diseases found in '{category}'.{Colors.RESET}")
                else:
                    print(f"  {Colors.YELLOW}Category '{category}' not found.{Colors.RESET}")
                    print(f"  Use {Colors.CYAN}list categories{Colors.RESET} to see all available categories.")

            # ---- INFO DISEASE ----
            elif command.startswith('info '):
                disease_query = user_input[5:].strip()
                # Fuzzy match: check if query is a substring of any disease name
                matched_name = None
                for d_name in MEDICAL_KNOWLEDGE_BASE:
                    if disease_query.lower() in d_name.lower():
                        matched_name = d_name
                        break
                
                if matched_name:
                    record = db.get_disease_info(matched_name)
                    if record:
                        sev_col = severity_color(record['Severity'])
                        print(f"\n{Colors.BOLD}  ╔{'═'*56}╗")
                        print(f"  ║  {record['Name']:<54}║")
                        print(f"  ╚{'═'*56}╝{Colors.RESET}")
                        print(f"  {Colors.DIM}{record['Description']}{Colors.RESET}")
                        print(f"\n  Category:    {Colors.BLUE}{record['Category']}{Colors.RESET}")
                        print(f"  Severity:    {sev_col}{record['Severity']}{Colors.RESET}")
                        print(f"  Prevalence:  {record['Prevalence']}")
                        
                        print(f"\n  {Colors.BOLD}Symptoms ({len(record['Symptoms'])}):{Colors.RESET}")
                        for s in sorted(record['Symptoms']):
                            print(f"    • {s}")
                        
                        print(f"\n  {Colors.BOLD}Treatments ({len(record['Treatments'])}):{Colors.RESET}")
                        for t in sorted(record['Treatments']):
                            print(f"    💊 {Colors.GREEN}{t}{Colors.RESET}")
                        
                        print(f"\n  {Colors.BOLD}Risk Factors ({len(record['RiskFactors'])}):{Colors.RESET}")
                        for r in sorted(record['RiskFactors']):
                            print(f"    ⚡ {Colors.YELLOW}{r}{Colors.RESET}")
                        print()
                    else:
                        print(f"  {Colors.YELLOW}Disease not found in database.{Colors.RESET}")
                else:
                    print(f"  {Colors.YELLOW}Disease '{disease_query}' not found.{Colors.RESET}")
                    print(f"  Use {Colors.CYAN}list diseases{Colors.RESET} or {Colors.CYAN}search <keyword>{Colors.RESET} to find it.")

            # ---- TREATMENTS ----
            elif command.startswith('treatments '):
                disease_query = user_input[11:].strip()
                matched_name = None
                for d_name in MEDICAL_KNOWLEDGE_BASE:
                    if disease_query.lower() in d_name.lower():
                        matched_name = d_name
                        break
                
                if matched_name:
                    treatments = db._get_treatments(matched_name)
                    if treatments:
                        print(f"\n{Colors.BOLD}  Treatments for \"{matched_name}\":{Colors.RESET}")
                        print(f"  {'─'*50}")
                        for t in sorted(treatments):
                            print(f"    💊 {Colors.GREEN}{t}{Colors.RESET}")
                        print()
                    else:
                        print(f"  {Colors.YELLOW}No treatments found.{Colors.RESET}")
                else:
                    print(f"  {Colors.YELLOW}Disease '{disease_query}' not found.{Colors.RESET}")

            # ---- SEARCH ----
            elif command.startswith('search '):
                keyword = user_input[7:].strip()
                if not keyword:
                    print(f"  {Colors.YELLOW}Please provide a search keyword.{Colors.RESET}")
                    continue
                
                diseases, symptoms = db.search_keyword(keyword)
                
                print(f"\n{Colors.BOLD}  Search Results for \"{keyword}\":{Colors.RESET}")
                print(f"  {'─'*50}")
                
                if diseases:
                    print(f"\n  {Colors.BOLD}Diseases ({len(diseases)}):{Colors.RESET}")
                    for record in diseases:
                        col = severity_color(record['Severity'])
                        print(f"    • {record['Name']:<40} {Colors.BLUE}[{record['Category']}]{Colors.RESET} {col}{record['Severity']}{Colors.RESET}")
                
                if symptoms:
                    print(f"\n  {Colors.BOLD}Symptoms ({len(symptoms)}):{Colors.RESET}")
                    for record in symptoms:
                        related = ', '.join(record['RelatedDiseases'][:3])
                        extra = f" +{len(record['RelatedDiseases'])-3} more" if len(record['RelatedDiseases']) > 3 else ""
                        print(f"    • {record['Symptom']:<30} → {Colors.DIM}{related}{extra}{Colors.RESET}")

                if not diseases and not symptoms:
                    print(f"  {Colors.YELLOW}No results found for '{keyword}'.{Colors.RESET}")
                print()

            # ---- VISUALIZE ALL ----
            elif command == 'visualize all':
                print(f"  {Colors.CYAN}Loading full network visualization...{Colors.RESET}")
                print(f"  {Colors.DIM}(Close the graph window to return to the CLI){Colors.RESET}")
                db.visualize_network()

            # ---- SYMPTOM INPUT (DIAGNOSIS) ----
            else:
                # Clean up user input (capitalize to match DB standard)
                patient_symptoms = [sym.strip().title() for sym in user_input.split(',')]
                
                matches = db.diagnose(patient_symptoms)
                
                if matches:
                    top_diseases = [record["Disease"] for record in matches]
                    print(f"  {Colors.CYAN}Opening visualization for top diagnoses...{Colors.RESET}")
                    print(f"  {Colors.DIM}(Close the graph window to enter more symptoms){Colors.RESET}")
                    db.visualize_network(top_diseases=top_diseases, patient_symptoms=patient_symptoms)
                else:
                    print(f"  {Colors.YELLOW}No diseases matched. Try standard terms like 'Fever', 'Cough', etc.{Colors.RESET}")
                    print(f"  Use {Colors.CYAN}list symptoms{Colors.RESET} to see all available symptom terms.\n")
        
        db.close()