"""
Medical Diagnostic Support System — GUI Application
A Tkinter-based graphical interface for symptom-based disease diagnosis.
Uses Neo4j graph database and semantic networks.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import networkx as nx
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as mpatches
import math

from neo4j import GraphDatabase
from medical_dataset import MEDICAL_KNOWLEDGE_BASE

# ==========================================
# NEO4J CONFIGURATION
# ==========================================
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "sava4090"


# ==========================================
# COLOR THEME
# ==========================================
class Theme:
    BG = "#0f0f1a"
    BG_SECONDARY = "#1a1a2e"
    BG_CARD = "#16213e"
    BG_INPUT = "#1a1a2e"
    ACCENT = "#00d2ff"
    ACCENT2 = "#7b2ff7"
    ACCENT_GRADIENT = "#0099ff"
    TEXT = "#e8e8e8"
    TEXT_DIM = "#8892b0"
    TEXT_BRIGHT = "#ffffff"
    SUCCESS = "#00d9a6"
    WARNING = "#ffd166"
    DANGER = "#ff6b6b"
    BORDER = "#2a2a4a"
    HIGHLIGHT = "#feca57"

    # Severity colors
    SEV_HIGH = "#ff6b6b"
    SEV_MOD = "#ffd166"
    SEV_MILD = "#00d9a6"


def severity_color(severity):
    sev = severity.lower()
    if "critical" in sev or "high" in sev:
        return Theme.SEV_HIGH
    elif "moderate" in sev:
        return Theme.SEV_MOD
    return Theme.SEV_MILD


# ==========================================
# DATABASE CLASS (reused from main.py)
# ==========================================
class MedicalDB:
    def __init__(self, uri, user, password):
        self.driver = None
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            self.driver.verify_connectivity()
        except Exception as e:
            raise ConnectionError(f"Neo4j connection failed: {e}")

    def close(self):
        if self.driver:
            self.driver.close()

    def seed_database(self):
        if not self.driver:
            return
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            for disease_name, frame in MEDICAL_KNOWLEDGE_BASE.items():
                session.run('''
                    CREATE (d:Disease {
                        name: $name, description: $description,
                        prevalence: $prevalence, severity: $severity,
                        category: $category
                    })
                ''', name=disease_name,
                     description=frame.get("description", ""),
                     prevalence=frame.get("prevalence", ""),
                     severity=frame.get("severity", ""),
                     category=frame.get("category", "General"))

                category = frame.get("category", "General")
                session.run('''
                    MATCH (d:Disease {name: $d_name})
                    MERGE (c:Category {name: $c_name})
                    MERGE (d)-[:BELONGS_TO]->(c)
                ''', d_name=disease_name, c_name=category)

                for symptom in frame.get("symptoms", []):
                    session.run('''
                        MATCH (d:Disease {name: $d_name})
                        MERGE (s:Symptom {name: $s_name})
                        MERGE (d)-[:HAS_SYMPTOM]->(s)
                    ''', d_name=disease_name, s_name=symptom)

                for treatment in frame.get("treatments", []):
                    session.run('''
                        MATCH (d:Disease {name: $d_name})
                        MERGE (t:Treatment {name: $t_name})
                        MERGE (t)-[:TREATS]->(d)
                    ''', d_name=disease_name, t_name=treatment)

                for rf in frame.get("risk_factors", []):
                    session.run('''
                        MATCH (d:Disease {name: $d_name})
                        MERGE (r:RiskFactor {name: $r_name})
                        MERGE (d)-[:HAS_RISK_FACTOR]->(r)
                    ''', d_name=disease_name, r_name=rf)

    def diagnose(self, symptoms):
        if not self.driver:
            return []
        with self.driver.session() as session:
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
            return [dict(record) for record in result]

    def get_treatments(self, disease_name):
        if not self.driver:
            return []
        with self.driver.session() as session:
            result = session.run('''
                MATCH (t:Treatment)-[:TREATS]->(d:Disease {name: $name})
                RETURN t.name AS Treatment
            ''', name=disease_name)
            return [r['Treatment'] for r in result]

    def get_risk_factors(self, disease_name):
        if not self.driver:
            return []
        with self.driver.session() as session:
            result = session.run('''
                MATCH (d:Disease {name: $name})-[:HAS_RISK_FACTOR]->(r:RiskFactor)
                RETURN r.name AS RiskFactor
            ''', name=disease_name)
            return [r['RiskFactor'] for r in result]

    def get_disease_symptoms(self, diseases):
        """Get symptoms for given diseases, returned as {disease: [symptoms]}"""
        if not self.driver:
            return {}
        with self.driver.session() as session:
            result = session.run('''
                MATCH (d:Disease)-[:HAS_SYMPTOM]->(s:Symptom)
                WHERE d.name IN $diseases
                RETURN d.name AS Disease, s.name AS Symptom
            ''', diseases=diseases)
            data = {}
            for r in result:
                data.setdefault(r['Disease'], []).append(r['Symptom'])
            return data


# ==========================================
# GUI APPLICATION
# ==========================================
class MedicalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Medical Diagnostic Support System")
        self.root.configure(bg=Theme.BG)
        self.root.geometry("1280x820")
        self.root.minsize(1100, 700)

        self.db = None
        self.last_matches = []

        # --- Styles ---
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self._configure_styles()

        # --- Build UI ---
        self._build_header()
        self._build_main_content()
        self._build_status_bar()

        # --- Connect to DB on startup ---
        self.root.after(300, self._connect_db)

    # ------------------------------------------------------------------
    # STYLES
    # ------------------------------------------------------------------
    def _configure_styles(self):
        s = self.style
        s.configure("Header.TFrame", background=Theme.BG)
        s.configure("Card.TFrame", background=Theme.BG_CARD)
        s.configure("Main.TFrame", background=Theme.BG)
        s.configure("Status.TFrame", background=Theme.BG_SECONDARY)

        s.configure("Title.TLabel", background=Theme.BG, foreground=Theme.ACCENT,
                     font=("Segoe UI", 20, "bold"))
        s.configure("Subtitle.TLabel", background=Theme.BG, foreground=Theme.TEXT_DIM,
                     font=("Segoe UI", 10))
        s.configure("CardTitle.TLabel", background=Theme.BG_CARD, foreground=Theme.TEXT_BRIGHT,
                     font=("Segoe UI", 12, "bold"))
        s.configure("CardText.TLabel", background=Theme.BG_CARD, foreground=Theme.TEXT,
                     font=("Segoe UI", 10))
        s.configure("Status.TLabel", background=Theme.BG_SECONDARY, foreground=Theme.TEXT_DIM,
                     font=("Segoe UI", 9))

        # Accent button
        s.configure("Accent.TButton",
                     background=Theme.ACCENT, foreground=Theme.BG,
                     font=("Segoe UI", 11, "bold"), padding=(20, 10))
        s.map("Accent.TButton",
              background=[("active", Theme.ACCENT_GRADIENT), ("pressed", Theme.ACCENT2)])

        # Secondary button
        s.configure("Secondary.TButton",
                     background=Theme.BG_CARD, foreground=Theme.TEXT,
                     font=("Segoe UI", 10), padding=(12, 8),
                     bordercolor=Theme.BORDER, borderwidth=1)
        s.map("Secondary.TButton",
              background=[("active", Theme.BORDER)])

        # Combobox
        s.configure("TCombobox", fieldbackground=Theme.BG_INPUT, foreground=Theme.TEXT,
                     background=Theme.BG_CARD, arrowcolor=Theme.ACCENT)

    # ------------------------------------------------------------------
    # HEADER
    # ------------------------------------------------------------------
    def _build_header(self):
        header = ttk.Frame(self.root, style="Header.TFrame")
        header.pack(fill=tk.X, padx=30, pady=(20, 5))

        ttk.Label(header, text="♥  Medical Diagnostic System",
                  style="Title.TLabel").pack(side=tk.LEFT)

        self.conn_label = ttk.Label(header, text="● Connecting...",
                                    style="Subtitle.TLabel")
        self.conn_label.pack(side=tk.RIGHT)

        # Separator
        sep = tk.Frame(self.root, bg=Theme.BORDER, height=1)
        sep.pack(fill=tk.X, padx=30, pady=(5, 10))

    # ------------------------------------------------------------------
    # MAIN CONTENT (left panel + right panel)
    # ------------------------------------------------------------------
    def _build_main_content(self):
        main = ttk.Frame(self.root, style="Main.TFrame")
        main.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 10))
        main.columnconfigure(0, weight=2)
        main.columnconfigure(1, weight=3)
        main.rowconfigure(0, weight=1)

        self._build_left_panel(main)
        self._build_right_panel(main)

    def _build_left_panel(self, parent):
        """Input & results panel"""
        left = tk.Frame(parent, bg=Theme.BG)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left.rowconfigure(2, weight=1)

        # --- Symptom Input Card ---
        input_card = tk.Frame(left, bg=Theme.BG_CARD, highlightbackground=Theme.BORDER,
                              highlightthickness=1, padx=20, pady=18)
        input_card.pack(fill=tk.X, pady=(0, 12))

        tk.Label(input_card, text="ENTER SYMPTOMS", bg=Theme.BG_CARD,
                 fg=Theme.ACCENT, font=("Segoe UI", 11, "bold")).pack(anchor=tk.W)
        tk.Label(input_card, text="Separate multiple symptoms with commas",
                 bg=Theme.BG_CARD, fg=Theme.TEXT_DIM, font=("Segoe UI", 9)).pack(anchor=tk.W, pady=(2, 8))

        # Input field
        input_frame = tk.Frame(input_card, bg=Theme.BG_CARD)
        input_frame.pack(fill=tk.X)

        self.symptom_entry = tk.Entry(input_frame, bg=Theme.BG_INPUT, fg=Theme.TEXT_BRIGHT,
                                      insertbackground=Theme.ACCENT,
                                      font=("Segoe UI", 13), relief=tk.FLAT,
                                      highlightbackground=Theme.BORDER,
                                      highlightcolor=Theme.ACCENT,
                                      highlightthickness=1)
        self.symptom_entry.pack(fill=tk.X, ipady=10)
        self.symptom_entry.bind('<Return>', lambda e: self._run_diagnosis())

        # Diagnose button
        diag_btn = tk.Button(input_card, text="🔍  DIAGNOSE", bg=Theme.ACCENT,
                             fg=Theme.BG, font=("Segoe UI", 12, "bold"),
                             relief=tk.FLAT, cursor="hand2", activebackground=Theme.ACCENT_GRADIENT,
                             command=self._run_diagnosis)
        diag_btn.pack(fill=tk.X, pady=(12, 5), ipady=8)

        # Quick symptom buttons
        quick_frame = tk.Frame(input_card, bg=Theme.BG_CARD)
        quick_frame.pack(fill=tk.X, pady=(5, 0))
        tk.Label(quick_frame, text="Quick add:", bg=Theme.BG_CARD,
                 fg=Theme.TEXT_DIM, font=("Segoe UI", 9)).pack(side=tk.LEFT)
        for sym in ["Fever", "Cough", "Headache", "Fatigue", "Nausea"]:
            btn = tk.Button(quick_frame, text=sym, bg=Theme.BG_SECONDARY,
                           fg=Theme.TEXT, font=("Segoe UI", 8), relief=tk.FLAT,
                           cursor="hand2", padx=8, pady=2,
                           activebackground=Theme.BORDER,
                           command=lambda s=sym: self._quick_add(s))
            btn.pack(side=tk.LEFT, padx=3)

        # --- Category Browse Card ---
        browse_card = tk.Frame(left, bg=Theme.BG_CARD, highlightbackground=Theme.BORDER,
                               highlightthickness=1, padx=20, pady=15)
        browse_card.pack(fill=tk.X, pady=(0, 12))

        tk.Label(browse_card, text="BROWSE BY CATEGORY", bg=Theme.BG_CARD,
                 fg=Theme.ACCENT, font=("Segoe UI", 11, "bold")).pack(anchor=tk.W)

        cat_frame = tk.Frame(browse_card, bg=Theme.BG_CARD)
        cat_frame.pack(fill=tk.X, pady=(8, 0))

        categories = sorted(set(d.get("category", "General") for d in MEDICAL_KNOWLEDGE_BASE.values()))
        self.cat_var = tk.StringVar(value=categories[0] if categories else "")
        cat_combo = ttk.Combobox(cat_frame, textvariable=self.cat_var,
                                  values=categories, state="readonly",
                                  font=("Segoe UI", 10))
        cat_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        browse_btn = tk.Button(cat_frame, text="Browse", bg=Theme.BG_SECONDARY,
                               fg=Theme.TEXT, font=("Segoe UI", 10), relief=tk.FLAT,
                               cursor="hand2", padx=15, activebackground=Theme.BORDER,
                               command=self._browse_category)
        browse_btn.pack(side=tk.LEFT)

        # --- Action Buttons ---
        actions_card = tk.Frame(left, bg=Theme.BG_CARD, highlightbackground=Theme.BORDER,
                                highlightthickness=1, padx=20, pady=15)
        actions_card.pack(fill=tk.X, pady=(0, 12))

        tk.Label(actions_card, text="ACTIONS", bg=Theme.BG_CARD,
                 fg=Theme.ACCENT, font=("Segoe UI", 11, "bold")).pack(anchor=tk.W, pady=(0, 8))

        btn_frame = tk.Frame(actions_card, bg=Theme.BG_CARD)
        btn_frame.pack(fill=tk.X)
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)

        actions = [
            ("📋 All Diseases", self._list_diseases, 0, 0),
            ("🔬 All Symptoms", self._list_symptoms, 0, 1),
            ("🗺️ Full Network", self._show_full_network, 1, 0),
            ("🔄 Reseed DB", self._reseed_db, 1, 1),
        ]
        for text, cmd, r, c in actions:
            b = tk.Button(btn_frame, text=text, bg=Theme.BG_SECONDARY,
                         fg=Theme.TEXT, font=("Segoe UI", 9), relief=tk.FLAT,
                         cursor="hand2", activebackground=Theme.BORDER,
                         command=cmd)
            b.grid(row=r, column=c, sticky="ew", padx=3, pady=3, ipady=5)

        # --- Results Area ---
        results_frame = tk.Frame(left, bg=Theme.BG_CARD, highlightbackground=Theme.BORDER,
                                 highlightthickness=1)
        results_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(results_frame, text="  RESULTS", bg=Theme.BG_CARD,
                 fg=Theme.ACCENT, font=("Segoe UI", 11, "bold")).pack(anchor=tk.W, padx=15, pady=(12, 5))

        self.results_text = scrolledtext.ScrolledText(
            results_frame, bg=Theme.BG, fg=Theme.TEXT,
            font=("Consolas", 10), relief=tk.FLAT, wrap=tk.WORD,
            insertbackground=Theme.ACCENT, selectbackground=Theme.ACCENT2,
            highlightthickness=0, padx=10, pady=8)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        self.results_text.config(state=tk.DISABLED)

        # Tag configurations for colored text
        self.results_text.tag_configure("title", foreground=Theme.ACCENT, font=("Consolas", 11, "bold"))
        self.results_text.tag_configure("disease", foreground=Theme.TEXT_BRIGHT, font=("Consolas", 11, "bold"))
        self.results_text.tag_configure("matched", foreground=Theme.HIGHLIGHT, font=("Consolas", 10))
        self.results_text.tag_configure("treatment", foreground=Theme.SUCCESS, font=("Consolas", 10))
        self.results_text.tag_configure("risk", foreground=Theme.WARNING, font=("Consolas", 10))
        self.results_text.tag_configure("severity_high", foreground=Theme.SEV_HIGH, font=("Consolas", 10, "bold"))
        self.results_text.tag_configure("severity_mod", foreground=Theme.SEV_MOD, font=("Consolas", 10))
        self.results_text.tag_configure("severity_mild", foreground=Theme.SEV_MILD, font=("Consolas", 10))
        self.results_text.tag_configure("dim", foreground=Theme.TEXT_DIM, font=("Consolas", 9))
        self.results_text.tag_configure("info", foreground=Theme.TEXT, font=("Consolas", 10))
        self.results_text.tag_configure("header", foreground=Theme.ACCENT2, font=("Consolas", 10, "bold"))

    def _build_right_panel(self, parent):
        """Graph visualization panel"""
        right = tk.Frame(parent, bg=Theme.BG_CARD, highlightbackground=Theme.BORDER,
                         highlightthickness=1)
        right.grid(row=0, column=1, sticky="nsew")

        # Title bar
        title_bar = tk.Frame(right, bg=Theme.BG_CARD)
        title_bar.pack(fill=tk.X, padx=15, pady=(12, 5))
        tk.Label(title_bar, text="SEMANTIC NETWORK VISUALIZATION",
                 bg=Theme.BG_CARD, fg=Theme.ACCENT,
                 font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT)

        # Canvas area for matplotlib
        self.graph_frame = tk.Frame(right, bg=Theme.BG)
        self.graph_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        # Placeholder label
        self.placeholder_label = tk.Label(
            self.graph_frame,
            text="Enter symptoms and click DIAGNOSE\nto see the semantic network here",
            bg=Theme.BG, fg=Theme.TEXT_DIM, font=("Segoe UI", 13),
            justify=tk.CENTER)
        self.placeholder_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.canvas_widget = None

    # ------------------------------------------------------------------
    # STATUS BAR
    # ------------------------------------------------------------------
    def _build_status_bar(self):
        status = ttk.Frame(self.root, style="Status.TFrame")
        status.pack(fill=tk.X, padx=0, pady=0)

        self.status_label = ttk.Label(status,
            text=f"  {len(MEDICAL_KNOWLEDGE_BASE)} diseases loaded  |  Ready",
            style="Status.TLabel")
        self.status_label.pack(side=tk.LEFT, padx=10, pady=4)

    # ------------------------------------------------------------------
    # DB CONNECTION
    # ------------------------------------------------------------------
    def _connect_db(self):
        try:
            self.db = MedicalDB(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
            self.conn_label.config(text="● Connected to Neo4j", foreground=Theme.SUCCESS)
            self.status_label.config(text=f"  {len(MEDICAL_KNOWLEDGE_BASE)} diseases  |  Connected to Neo4j")
            self._write_result("✓ Connected to Neo4j successfully.\n", "treatment")
            self._write_result("  Type symptoms and click DIAGNOSE, or browse by category.\n\n", "dim")
        except Exception as e:
            self.conn_label.config(text="● Disconnected", foreground=Theme.DANGER)
            self.status_label.config(text="  ⚠ Neo4j not connected — start your database first")
            self._write_result("✗ Could not connect to Neo4j.\n\n", "severity_high")
            self._write_result("Make sure Neo4j Desktop is running and your database is STARTED.\n", "info")
            self._write_result(f"  URI: {NEO4J_URI}\n  User: {NEO4J_USER}\n\n", "dim")
            self._write_result(f"Error: {e}\n", "dim")

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------
    def _clear_results(self):
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        self.results_text.config(state=tk.DISABLED)

    def _write_result(self, text, tag=None):
        self.results_text.config(state=tk.NORMAL)
        self.results_text.insert(tk.END, text, tag)
        self.results_text.see(tk.END)
        self.results_text.config(state=tk.DISABLED)

    def _quick_add(self, symptom):
        current = self.symptom_entry.get().strip()
        if current:
            # Don't add duplicates
            existing = [s.strip().title() for s in current.split(',')]
            if symptom not in existing:
                self.symptom_entry.insert(tk.END, f", {symptom}")
        else:
            self.symptom_entry.insert(0, symptom)

    # ------------------------------------------------------------------
    # DIAGNOSIS
    # ------------------------------------------------------------------
    def _run_diagnosis(self):
        if not self.db:
            messagebox.showwarning("Not Connected", "Neo4j database is not connected.\nStart Neo4j and restart the app.")
            return

        raw = self.symptom_entry.get().strip()
        if not raw:
            messagebox.showinfo("Input Required", "Please enter at least one symptom.")
            return

        patient_symptoms = [s.strip().title() for s in raw.split(',') if s.strip()]
        self._clear_results()
        self._write_result("DIAGNOSTIC RESULTS\n", "title")
        self._write_result(f"{'─'*45}\n", "dim")
        self._write_result(f"Symptoms: {', '.join(patient_symptoms)}\n\n", "matched")

        self.status_label.config(text="  Analyzing symptoms...")
        self.root.update()

        matches = self.db.diagnose(patient_symptoms)
        self.last_matches = matches

        if not matches:
            self._write_result("⚠ No matching diseases found.\n", "severity_high")
            self._write_result("Try common symptom names like Fever, Cough, etc.\n", "dim")
            self.status_label.config(text=f"  {len(MEDICAL_KNOWLEDGE_BASE)} diseases  |  No matches found")
            return

        for i, m in enumerate(matches, 1):
            conf = m['Confidence']
            sev = m['Severity']
            sev_tag = "severity_high" if "high" in sev.lower() or "critical" in sev.lower() \
                      else "severity_mod" if "moderate" in sev.lower() else "severity_mild"

            # Confidence bar
            bar_len = 20
            filled = int(conf / 100 * bar_len)
            bar = '█' * filled + '░' * (bar_len - filled)

            self._write_result(f" {i}. ", "info")
            self._write_result(f"{m['Disease']}\n", "disease")
            self._write_result(f"    Category:   {m['Category']}\n", "info")
            self._write_result(f"    Severity:   ", "info")
            self._write_result(f"{sev}\n", sev_tag)
            self._write_result(f"    Confidence: [{bar}] {conf:.1f}%\n", "info")
            self._write_result(f"    Matched:    ", "info")
            self._write_result(f"{', '.join(m['MatchedSymptomList'])}\n", "matched")
            self._write_result(f"                ({m['MatchingSymptoms']}/{m['TotalSymptoms']} symptoms)\n\n", "dim")

        # Show treatments for top result
        top = matches[0]['Disease']
        treatments = self.db.get_treatments(top)
        if treatments:
            self._write_result(f"TREATMENTS for \"{top}\":\n", "title")
            for t in treatments:
                self._write_result(f"  💊 {t}\n", "treatment")
            self._write_result("\n", "info")

        risk_factors = self.db.get_risk_factors(top)
        if risk_factors:
            self._write_result(f"RISK FACTORS:\n", "title")
            for r in risk_factors:
                self._write_result(f"  ⚡ {r}\n", "risk")

        self.status_label.config(text=f"  {len(matches)} diseases matched  |  Top: {top}")

        # Draw the graph
        top_diseases = [m['Disease'] for m in matches[:3]]
        self._draw_diagnosis_graph(top_diseases, patient_symptoms)

    # ------------------------------------------------------------------
    # BROWSE CATEGORY
    # ------------------------------------------------------------------
    def _browse_category(self):
        cat = self.cat_var.get()
        if not cat:
            return
        self._clear_results()
        self._write_result(f"{cat.upper()} DISEASES\n", "title")
        self._write_result(f"{'─'*45}\n\n", "dim")

        diseases_in_cat = {k: v for k, v in MEDICAL_KNOWLEDGE_BASE.items()
                           if v.get("category", "") == cat}

        for i, (name, data) in enumerate(sorted(diseases_in_cat.items()), 1):
            sev = data.get("severity", "")
            sev_tag = "severity_high" if "high" in sev.lower() or "critical" in sev.lower() \
                      else "severity_mod" if "moderate" in sev.lower() else "severity_mild"
            self._write_result(f" {i}. ", "info")
            self._write_result(f"{name}\n", "disease")
            self._write_result(f"    {data.get('description', '')}\n", "dim")
            self._write_result(f"    Severity: ", "info")
            self._write_result(f"{sev}", sev_tag)
            self._write_result(f"  |  Prevalence: {data.get('prevalence', '')}\n", "info")
            self._write_result(f"    Symptoms: {', '.join(data.get('symptoms', []))}\n\n", "matched")

        self.status_label.config(text=f"  Browsing: {cat}  |  {len(diseases_in_cat)} diseases")

    # ------------------------------------------------------------------
    # LIST DISEASES / SYMPTOMS
    # ------------------------------------------------------------------
    def _list_diseases(self):
        self._clear_results()
        diseases = sorted(MEDICAL_KNOWLEDGE_BASE.keys())
        self._write_result(f"ALL DISEASES ({len(diseases)})\n", "title")
        self._write_result(f"{'─'*45}\n\n", "dim")
        for i, d in enumerate(diseases, 1):
            cat = MEDICAL_KNOWLEDGE_BASE[d].get("category", "")
            sev = MEDICAL_KNOWLEDGE_BASE[d].get("severity", "")
            self._write_result(f" {i:3}. {d}\n", "disease")
            self._write_result(f"      [{cat}]  {sev}\n", "dim")

    def _list_symptoms(self):
        self._clear_results()
        all_symptoms = set()
        for data in MEDICAL_KNOWLEDGE_BASE.values():
            all_symptoms.update(data.get("symptoms", []))
        symptoms = sorted(all_symptoms)
        self._write_result(f"ALL SYMPTOMS ({len(symptoms)})\n", "title")
        self._write_result(f"{'─'*45}\n\n", "dim")
        for i, s in enumerate(symptoms, 1):
            self._write_result(f" {i:3}. {s}\n", "info")

    # ------------------------------------------------------------------
    # RESEED DATABASE
    # ------------------------------------------------------------------
    def _reseed_db(self):
        if not self.db:
            messagebox.showwarning("Not Connected", "Neo4j not connected.")
            return
        if not messagebox.askyesno("Reseed Database",
                                    "This will clear and reload ALL data.\nContinue?"):
            return
        self._clear_results()
        self._write_result("Reseeding database...\n", "title")
        self.root.update()
        try:
            self.db.seed_database()
            self._write_result(f"✓ Database reseeded with {len(MEDICAL_KNOWLEDGE_BASE)} diseases.\n", "treatment")
        except Exception as e:
            self._write_result(f"✗ Error: {e}\n", "severity_high")

    # ------------------------------------------------------------------
    # GRAPH VISUALIZATION
    # ------------------------------------------------------------------
    def _draw_diagnosis_graph(self, top_diseases, patient_symptoms):
        """Draw a clean clustered graph inside the GUI panel."""
        if not self.db:
            return

        # Clear previous graph
        if self.canvas_widget:
            self.canvas_widget.destroy()
            self.canvas_widget = None
        self.placeholder_label.place_forget()

        disease_symptoms = self.db.get_disease_symptoms(top_diseases)
        if not disease_symptoms:
            return

        # Build graph
        G = nx.Graph()
        for disease, symptoms in disease_symptoms.items():
            for symptom in symptoms:
                G.add_edge(disease, symptom)

        # Custom clustered layout
        pos = {}
        diseases_list = list(disease_symptoms.keys())
        n_d = len(diseases_list)
        cluster_radius = 4.5
        symptom_radius = 2.2

        for i, disease in enumerate(diseases_list):
            angle = 2 * math.pi * i / n_d - math.pi / 2
            cx = cluster_radius * math.cos(angle)
            cy = cluster_radius * math.sin(angle)
            pos[disease] = (cx, cy)

            syms = disease_symptoms[disease]
            for j, sym in enumerate(syms):
                s_angle = 2 * math.pi * j / len(syms) - math.pi / 2
                sx = cx + symptom_radius * math.cos(s_angle)
                sy = cy + symptom_radius * math.sin(s_angle)
                if sym in pos:
                    ox, oy = pos[sym]
                    pos[sym] = ((ox + sx) / 2, (oy + sy) / 2)
                else:
                    pos[sym] = (sx, sy)

        # Colors and sizes
        node_colors = []
        node_sizes = []
        for node in G.nodes():
            if node in disease_symptoms:
                node_colors.append('#ff6b6b')
                node_sizes.append(3500)
            elif node in patient_symptoms:
                node_colors.append('#feca57')
                node_sizes.append(1800)
            else:
                node_colors.append('#3d5a80')
                node_sizes.append(500)

        # Edge types
        matched_edges = [(u, v) for u, v in G.edges()
                         if u in patient_symptoms or v in patient_symptoms]
        other_edges = [(u, v) for u, v in G.edges()
                       if u not in patient_symptoms and v not in patient_symptoms]

        # Labels
        disease_labels = {n: n for n in G.nodes() if n in disease_symptoms}
        matched_labels = {n: n for n in G.nodes()
                          if n not in disease_symptoms and n in patient_symptoms}
        other_labels = {n: n for n in G.nodes()
                        if n not in disease_symptoms and n not in patient_symptoms}

        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
        fig.patch.set_facecolor('#0f0f1a')
        ax.set_facecolor('#0f0f1a')

        # Draw
        if other_edges:
            nx.draw_networkx_edges(G, pos, edgelist=other_edges,
                                   width=0.6, alpha=0.15, edge_color='#4a5568', ax=ax)
        if matched_edges:
            nx.draw_networkx_edges(G, pos, edgelist=matched_edges,
                                   width=1.8, alpha=0.5, edge_color='#feca57', ax=ax)

        nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors,
                               alpha=0.9, edgecolors='#1a1a2e', linewidths=1.5, ax=ax)

        nx.draw_networkx_labels(G, pos, labels=disease_labels,
                                font_size=8, font_weight='bold', font_color='white',
                                font_family='sans-serif',
                                bbox=dict(facecolor='#ff6b6b', edgecolor='none',
                                          alpha=0.85, boxstyle='round,pad=0.3'), ax=ax)

        nx.draw_networkx_labels(G, pos, labels=matched_labels,
                                font_size=7, font_weight='bold', font_color='#2d3436',
                                font_family='sans-serif',
                                bbox=dict(facecolor='#feca57', edgecolor='none',
                                          alpha=0.85, boxstyle='round,pad=0.2'), ax=ax)

        nx.draw_networkx_labels(G, pos, labels=other_labels,
                                font_size=6, font_color='#8892b0',
                                font_family='sans-serif', alpha=0.7, ax=ax)

        # Legend
        legend_elements = [
            mpatches.Patch(color='#ff6b6b', label='Diagnosed Diseases'),
            mpatches.Patch(color='#feca57', label='Your Symptoms'),
            mpatches.Patch(color='#3d5a80', label='Other Symptoms'),
        ]
        ax.legend(handles=legend_elements, loc='upper left', fontsize=7,
                  facecolor='#1a1a2e', edgecolor='#2a2a4a', labelcolor='#e8e8e8',
                  framealpha=0.9)

        ax.set_title("Diagnosis — Semantic Network", fontsize=11,
                     fontweight='bold', color='#e8e8e8', pad=10)
        ax.axis('off')
        fig.tight_layout()

        # Embed in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        self.canvas_widget = canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
        plt.close(fig)

    def _show_full_network(self):
        """Show the full network in a separate matplotlib window."""
        if not self.db:
            messagebox.showwarning("Not Connected", "Neo4j not connected.")
            return

        self._clear_results()
        self._write_result("Opening full network in a new window...\n", "title")
        self._write_result("Close the window to return.\n", "dim")

        # Gather all data from dataset
        disease_symptoms = {}
        for name, data in MEDICAL_KNOWLEDGE_BASE.items():
            disease_symptoms[name] = data.get("symptoms", [])

        G = nx.Graph()
        for disease, symptoms in disease_symptoms.items():
            for sym in symptoms:
                G.add_edge(disease, sym)

        # Clustered layout
        pos = {}
        diseases_list = list(disease_symptoms.keys())
        n_d = len(diseases_list)
        cluster_radius = max(14.0, n_d * 1.3)
        symptom_radius = max(2.0, min(3.5, cluster_radius / n_d * 2.5))

        for i, disease in enumerate(diseases_list):
            a = 2 * math.pi * i / n_d - math.pi / 2
            cx, cy = cluster_radius * math.cos(a), cluster_radius * math.sin(a)
            pos[disease] = (cx, cy)
            syms = disease_symptoms[disease]
            for j, sym in enumerate(syms):
                sa = 2 * math.pi * j / len(syms) - math.pi / 2
                sx = cx + symptom_radius * math.cos(sa)
                sy = cy + symptom_radius * math.sin(sa)
                if sym in pos:
                    ox, oy = pos[sym]
                    pos[sym] = ((ox + sx) / 2, (oy + sy) / 2)
                else:
                    pos[sym] = (sx, sy)

        category_colors = {
            "Respiratory": "#54a0ff", "Immunological": "#a29bfe",
            "Neurological": "#fd79a8", "Cardiovascular": "#e17055",
            "Gastrointestinal": "#00b894", "Endocrine": "#fdcb6e",
            "Dermatological": "#e84393", "Psychiatric": "#6c5ce7",
            "Infectious": "#ff7675", "Musculoskeletal": "#00cec9",
            "Renal": "#0984e3", "Hematological": "#d63031",
        }

        node_colors = []
        node_sizes = []
        for node in G.nodes():
            if node in disease_symptoms:
                cat = MEDICAL_KNOWLEDGE_BASE.get(node, {}).get("category", "General")
                node_colors.append(category_colors.get(cat, '#54a0ff'))
                node_sizes.append(3000)
            else:
                node_colors.append('#dfe6e9')
                node_sizes.append(300)

        disease_labels = {n: n for n in G.nodes() if n in disease_symptoms}

        fig, ax = plt.subplots(figsize=(24, 18))
        fig.patch.set_facecolor('#f8f9fa')
        ax.set_facecolor('#f8f9fa')

        nx.draw_networkx_edges(G, pos, width=0.5, alpha=0.12, edge_color='#b2bec3', ax=ax)
        nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors,
                               alpha=0.9, edgecolors='white', linewidths=1.5, ax=ax)
        nx.draw_networkx_labels(G, pos, labels=disease_labels,
                                font_size=8, font_weight='bold',
                                bbox=dict(facecolor='white', edgecolor='#ddd',
                                          alpha=0.9, boxstyle='round,pad=0.3'), ax=ax)

        legend_elements = [mpatches.Patch(color=c, label=cat) for cat, c in category_colors.items()]
        legend_elements.append(mpatches.Patch(color='#dfe6e9', label='Symptoms'))
        ax.legend(handles=legend_elements, loc='upper left', fontsize=9, ncol=2,
                  framealpha=0.9, fancybox=True, shadow=True)

        ax.set_title("Full Medical Knowledge Base — Semantic Network",
                     fontsize=18, fontweight='bold', pad=20)
        ax.axis('off')
        fig.tight_layout()
        plt.show()


# ==========================================
# MAIN
# ==========================================
if __name__ == "__main__":
    root = tk.Tk()

    # Set icon if available
    try:
        root.iconbitmap(default='')
    except Exception:
        pass

    app = MedicalApp(root)
    root.mainloop()
