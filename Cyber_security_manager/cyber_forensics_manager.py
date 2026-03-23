"""
Cyber Forensic Case File Management System
A comprehensive GUI application for digital forensic investigators
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox, simpledialog
import sqlite3
import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
import threading

# Configure CustomTkinter appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Color constants
COLORS = {
    "primary_bg": "#0d1117",
    "secondary_bg": "#161b22",
    "accent": "#00ff9d",
    "accent_secondary": "#00b8ff",
    "text_primary": "#e6edf3",
    "text_secondary": "#8b949e",
    "warning": "#f0883e",
    "error": "#f85149",
    "success": "#3fb950",
    "border": "#30363d",
}

# Database setup
class Database:
    def __init__(self, db_path="forensics_db.sqlite"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Cases table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'Open',
                priority TEXT DEFAULT 'Medium',
                investigator TEXT,
                created_date TEXT,
                updated_date TEXT
            )
        ''')
        
        # Evidence table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                evidence_id TEXT UNIQUE NOT NULL,
                case_id TEXT NOT NULL,
                file_path TEXT,
                file_name TEXT,
                file_size INTEGER,
                evidence_type TEXT,
                description TEXT,
                md5_hash TEXT,
                sha256_hash TEXT,
                added_date TEXT,
                FOREIGN KEY (case_id) REFERENCES cases(case_id)
            )
        ''')
        
        # Notes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id TEXT UNIQUE NOT NULL,
                case_id TEXT NOT NULL,
                content TEXT NOT NULL,
                created_date TEXT,
                FOREIGN KEY (case_id) REFERENCES cases(case_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)


class CyberForensicsApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("CyberForensics Manager")
        self.geometry("1200x700")
        self.minsize(1000, 600)
        
        # Initialize database
        self.db = Database()
        
        # Set window background
        self.configure(fg_color=COLORS["primary_bg"])
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create UI components
        self.create_sidebar()
        self.create_main_content()
        
        # Show dashboard by default
        self.show_dashboard()
    
    def create_sidebar(self):
        """Create the sidebar navigation"""
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color=COLORS["secondary_bg"])
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # Logo/Title
        title_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        title_frame.pack(pady=20, padx=20, fill="x")
        
        logo_label = ctk.CTkLabel(
            title_frame,
            text="🔬",
            font=ctk.CTkFont(size=40)
        )
        logo_label.pack()
        
        app_title = ctk.CTkLabel(
            title_frame,
            text="CyberForensics",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=COLORS["accent"]
        )
        app_title.pack()
        
        subtitle = ctk.CTkLabel(
            title_frame,
            text="Case Manager",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        )
        subtitle.pack()
        
        # Navigation buttons
        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.pack(pady=20, padx=10, fill="x")
        
        self.nav_buttons = {}
        
        nav_items = [
            ("Dashboard", "📊", self.show_dashboard),
            ("Cases", "📁", self.show_cases),
            ("Evidence", "🔍", self.show_evidence),
            ("Reports", "📋", self.show_reports),
            ("Settings", "⚙️", self.show_settings)
        ]
        
        for i, (text, icon, command) in enumerate(nav_items):
            btn = ctk.CTkButton(
                nav_frame,
                text=f"  {icon}  {text}",
                command=command,
                fg_color="transparent",
                text_color=COLORS["text_primary"],
                hover_color=COLORS["accent"],
                anchor="w",
                font=ctk.CTkFont(size=14),
                height=45
            )
            btn.pack(pady=4, fill="x")
            self.nav_buttons[text] = btn
        
        # Version info
        version_label = ctk.CTkLabel(
            self.sidebar,
            text="v1.0.0 | Digital Forensics",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_secondary"]
        )
        version_label.pack(side="bottom", pady=15)
    
    def create_main_content(self):
        """Create the main content area"""
        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=COLORS["primary_bg"])
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        
        # Header
        self.header_frame = ctk.CTkFrame(self.content_frame, height=60, corner_radius=0, fg_color=COLORS["secondary_bg"])
        self.header_frame.pack(fill="x", padx=0, pady=0)
        self.header_frame.pack_propagate(False)
        
        self.header_title = ctk.CTkLabel(
            self.header_frame,
            text="Dashboard",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        self.header_title.pack(side="left", padx=20)
        
        # Search bar
        self.search_entry = ctk.CTkEntry(
            self.header_frame,
            placeholder_text="🔍 Search cases...",
            width=250,
            fg_color=COLORS["primary_bg"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"]
        )
        self.search_entry.pack(side="right", padx=20, pady=10)
        self.search_entry.bind("<Return>", lambda e: self.perform_search())
        
        # Main scrollable content
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color="transparent",
            scrollbar_button_color=COLORS["accent"],
            scrollbar_button_hover_color=COLORS["accent_secondary"]
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    def clear_content(self):
        """Clear the scroll frame content"""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):
        """Show the dashboard view"""
        self.header_title.configure(text="Dashboard")
        self.clear_content()
        
        # Statistics cards
        stats_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 20))
        
        # Get stats from database
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM cases")
        total_cases = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM cases WHERE status = 'Open'")
        open_cases = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM evidence")
        total_evidence = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM cases WHERE status = 'Closed'")
        closed_cases = cursor.fetchone()[0]
        
        conn.close()
        
        stats = [
            ("Total Cases", total_cases, "📁", COLORS["accent_secondary"]),
            ("Open Cases", open_cases, "🔓", COLORS["warning"]),
            ("Evidence Items", total_evidence, "🔍", COLORS["accent"]),
            ("Closed Cases", closed_cases, "✅", COLORS["success"])
        ]
        
        for i, (title, value, icon, color) in enumerate(stats):
            card = ctk.CTkFrame(stats_frame, fg_color=COLORS["secondary_bg"])
            card.pack(side="left", padx=10, fill="both", expand=True)
            
            ctk.CTkLabel(
                card,
                text=icon,
                font=ctk.CTkFont(size=30)
            ).pack(pady=(15, 5))
            
            ctk.CTkLabel(
                card,
                text=str(value),
                font=ctk.CTkFont(size=28, weight="bold"),
                text_color=color
            ).pack()
            
            ctk.CTkLabel(
                card,
                text=title,
                font=ctk.CTkFont(size=12),
                text_color=COLORS["text_secondary"]
            ).pack(pady=(0, 15))
        
        # Quick actions
        actions_frame = ctk.CTkFrame(self.scroll_frame, fg_color=COLORS["secondary_bg"])
        actions_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            actions_frame,
            text="Quick Actions",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w", padx=20, pady=(15, 10))
        
        action_buttons = [
            ("➕ New Case", lambda: self.show_cases(new_case=True)),
            ("📂 Import Evidence", self.import_evidence),
("📊 Generate Report", self.generate_case_summary_report)
        ]
        
        btn_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        btn_frame.pack(padx=20, pady=(0, 15), fill="x")
        
        for text, command in action_buttons:
            btn = ctk.CTkButton(
                btn_frame,
                text=text,
                command=command,
                fg_color=COLORS["accent"],
                hover_color="#00cc7d",
                text_color=COLORS["primary_bg"],
                font=ctk.CTkFont(weight="bold")
            )
            btn.pack(side="left", padx=5)
        
        # Recent cases
        recent_frame = ctk.CTkFrame(self.scroll_frame, fg_color=COLORS["secondary_bg"])
        recent_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(
            recent_frame,
            text="Recent Cases",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w", padx=20, pady=(15, 10))
        
        # Get recent cases
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT case_id, title, status, priority, created_date FROM cases ORDER BY created_date DESC LIMIT 5")
        recent_cases = cursor.fetchall()
        conn.close()
        
        if recent_cases:
            for case in recent_cases:
                case_card = ctk.CTkFrame(recent_frame, fg_color=COLORS["primary_bg"])
                case_card.pack(fill="x", padx=20, pady=5)
                
                status_colors = {
                    "Open": COLORS["warning"],
                    "In Progress": COLORS["accent_secondary"],
                    "Closed": COLORS["success"],
                    "Archived": COLORS["text_secondary"]
                }
                
                priority_colors = {
                    "Low": COLORS["text_secondary"],
                    "Medium": COLORS["warning"],
                    "High": COLORS["error"],
                    "Critical": "#ff00ff"
                }
                
                ctk.CTkLabel(
                    case_card,
                    text=f"📁 {case[1]}",
                    font=ctk.CTkFont(size=14),
                    text_color=COLORS["text_primary"]
                ).pack(side="left", padx=15, pady=12)
                
                status_label = ctk.CTkLabel(
                    case_card,
                    text=case[2],
                    font=ctk.CTkFont(size=11),
                    text_color=status_colors.get(case[2], COLORS["text_secondary"])
                )
                status_label.pack(side="right", padx=15, pady=12)
                
                priority_label = ctk.CTkLabel(
                    case_card,
                    text=f"Priority: {case[3]}",
                    font=ctk.CTkFont(size=11),
                    text_color=priority_colors.get(case[3], COLORS["text_secondary"])
                )
                priority_label.pack(side="right", padx=10, pady=12)
                
                case_card.bind("<Button-1>", lambda e, c=case[0]: self.view_case(c))
        else:
            ctk.CTkLabel(
                recent_frame,
                text="No cases yet. Create your first case!",
                font=ctk.CTkFont(size=13),
                text_color=COLORS["text_secondary"]
            ).pack(pady=30)
    
    def show_cases(self, new_case=False):
        """Show cases list or create case form"""
        self.header_title.configure(text="Cases")
        self.clear_content()
        
        # Toolbar
        toolbar = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 15))
        
        ctk.CTkButton(
            toolbar,
            text="➕ New Case",
            command=self.create_case_form,
            fg_color=COLORS["accent"],
            hover_color="#00cc7d",
            text_color=COLORS["primary_bg"],
            font=ctk.CTkFont(weight="bold")
        ).pack(side="left")
        
        # Filter dropdown
        self.status_filter = ctk.CTkOptionMenu(
            toolbar,
            values=["All", "Open", "In Progress", "Closed", "Archived"],
            fg_color=COLORS["secondary_bg"],
            button_color=COLORS["border"],
            button_hover_color=COLORS["accent"],
            text_color=COLORS["text_primary"]
        )
        self.status_filter.pack(side="right", padx=5)
        self.status_filter.set("All")
        self.status_filter.bind("<<ComboboxSelected>>", lambda e: self.load_cases())
        
        # Cases list
        self.load_cases()
    
    def load_cases(self):
        """Load and display cases"""
        # Clear existing case items
        for widget in self.scroll_frame.winfo_children():
            if widget.winfo_class() == "CTkFrame":
                widget.destroy()
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        status_filter = self.status_filter.get() if hasattr(self, 'status_filter') else "All"
        
        if status_filter == "All":
            cursor.execute("SELECT case_id, title, description, status, priority, investigator, created_date FROM cases ORDER BY created_date DESC")
        else:
            cursor.execute("SELECT case_id, title, description, status, priority, investigator, created_date FROM cases WHERE status = ? ORDER BY created_date DESC", (status_filter,))
        
        cases = cursor.fetchall()
        conn.close()
        
        if not cases:
            ctk.CTkLabel(
                self.scroll_frame,
                text="No cases found",
                font=ctk.CTkFont(size=14),
                text_color=COLORS["text_secondary"]
            ).pack(pady=30)
            return
        
        for case in cases:
            case_card = ctk.CTkFrame(self.scroll_frame, fg_color=COLORS["secondary_bg"])
            case_card.pack(fill="x", pady=8)
            
            # Left side - case info
            info_frame = ctk.CTkFrame(case_card, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True, padx=20, pady=15)
            
            ctk.CTkLabel(
                info_frame,
                text=case[1],
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=COLORS["text_primary"]
            ).pack(anchor="w")
            
            ctk.CTkLabel(
                info_frame,
                text=f"ID: {case[0]} | Investigator: {case[5] or 'N/A'}",
                font=ctk.CTkFont(size=11),
                text_color=COLORS["text_secondary"]
            ).pack(anchor="w", pady=(2, 0))
            
            ctk.CTkLabel(
                info_frame,
                text=case[2] or "No description",
                font=ctk.CTkFont(size=12),
                text_color=COLORS["text_secondary"],
                wraplength=400
            ).pack(anchor="w", pady=(5, 0))
            
            # Right side - status and actions
            right_frame = ctk.CTkFrame(case_card, fg_color="transparent")
            right_frame.pack(side="right", padx=20, pady=15)
            
            status_colors = {
                "Open": COLORS["warning"],
                "In Progress": COLORS["accent_secondary"],
                "Closed": COLORS["success"],
                "Archived": COLORS["text_secondary"]
            }
            
            priority_colors = {
                "Low": COLORS["text_secondary"],
                "Medium": COLORS["warning"],
                "High": COLORS["error"],
                "Critical": "#ff00ff"
            }
            
            # Status badge
            status_frame = ctk.CTkFrame(right_frame, fg_color=COLORS["secondary_bg"], corner_radius=15)
            status_frame.pack(pady=2)
            ctk.CTkLabel(
                status_frame,
                text=case[3],
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=status_colors.get(case[3], COLORS["text_secondary"]),
                padx=15, pady=4
            ).pack()
            
            # Priority badge
            priority_frame = ctk.CTkFrame(right_frame, fg_color=COLORS["secondary_bg"], corner_radius=15)
            priority_frame.pack(pady=2)
            ctk.CTkLabel(
                priority_frame,
                text=f"{case[4]} Priority",
                font=ctk.CTkFont(size=10),
                text_color=priority_colors.get(case[4], COLORS["text_secondary"]),
                padx=10, pady=2
            ).pack()
            
            # Action buttons
            btn_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
            btn_frame.pack(pady=8)
            
            ctk.CTkButton(
                btn_frame,
                text="👁️ View",
                command=lambda c=case[0]: self.view_case(c),
                width=70,
                fg_color=COLORS["accent_secondary"],
                hover_color="#0099cc",
                text_color=COLORS["primary_bg"],
                font=ctk.CTkFont(size=11)
            ).pack(side="left", padx=2)
            
            ctk.CTkButton(
                btn_frame,
                text="🗑️",
                command=lambda c=case[0]: self.delete_case(c),
                width=40,
                fg_color=COLORS["error"],
                hover_color="#cc3333",
                text_color="white",
                font=ctk.CTkFont(size=11)
            ).pack(side="left", padx=2)
            
            # Bind click to view case
            info_frame.bind("<Button-1>", lambda e, cid=case[0]: self.view_case(cid))
            for child in info_frame.winfo_children():
                child.bind("<Button-1>", lambda e, cid=case[0]: self.view_case(cid))
    
    def create_case_form(self):
        """Show form to create a new case"""
        self.header_title.configure(text="New Case")
        self.clear_content()
        
        form_frame = ctk.CTkFrame(self.scroll_frame, fg_color=COLORS["secondary_bg"])
        form_frame.pack(fill="x", padx=50, pady=20)
        
        ctk.CTkLabel(
            form_frame,
            text="Create New Case",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["accent"]
        ).pack(pady=(20, 30))
        
        # Case ID
        ctk.CTkLabel(
            form_frame,
            text="Case ID *",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w", padx=30)
        
        case_id_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="e.g., CF-2024-001",
            fg_color=COLORS["primary_bg"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            width=400
        )
        case_id_entry.pack(padx=30, pady=(5, 15), fill="x")
        
        # Title
        ctk.CTkLabel(
            form_frame,
            text="Case Title *",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w", padx=30)
        
        title_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter case title",
            fg_color=COLORS["primary_bg"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            width=400
        )
        title_entry.pack(padx=30, pady=(5, 15), fill="x")
        
        # Description
        ctk.CTkLabel(
            form_frame,
            text="Description",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w", padx=30)
        
        desc_text = ctk.CTkTextbox(
            form_frame,
            fg_color=COLORS["primary_bg"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            width=400,
            height=100
        )
        desc_text.pack(padx=30, pady=(5, 15), fill="x")
        
        # Priority
        ctk.CTkLabel(
            form_frame,
            text="Priority",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w", padx=30)
        
        priority_var = ctk.CTkOptionMenu(
            form_frame,
            values=["Low", "Medium", "High", "Critical"],
            fg_color=COLORS["primary_bg"],
            button_color=COLORS["border"],
            button_hover_color=COLORS["accent"],
            text_color=COLORS["text_primary"],
            width=200
        )
        priority_var.pack(padx=30, pady=(5, 15), anchor="w")
        priority_var.set("Medium")
        
        # Investigator
        ctk.CTkLabel(
            form_frame,
            text="Investigator Name",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w", padx=30)
        
        investigator_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter investigator name",
            fg_color=COLORS["primary_bg"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            width=400
        )
        investigator_entry.pack(padx=30, pady=(5, 25), fill="x")
        
        # Buttons
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(pady=(0, 20))
        
        def save_case():
            case_id = case_id_entry.get().strip()
            title = title_entry.get().strip()
            description = desc_text.get("1.0", "end-1c").strip()
            priority = priority_var.get()
            investigator = investigator_entry.get().strip()
            
            if not case_id or not title:
                messagebox.showerror("Error", "Case ID and Title are required!")
                return
            
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                cursor.execute(
                    "INSERT INTO cases (case_id, title, description, priority, investigator, created_date, updated_date) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (case_id, title, description, priority, investigator, now, now)
                )
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "Case created successfully!")
                self.show_cases()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Case ID already exists!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create case: {str(e)}")
        
        ctk.CTkButton(
            btn_frame,
            text="💾 Save Case",
            command=save_case,
            fg_color=COLORS["accent"],
            hover_color="#00cc7d",
            text_color=COLORS["primary_bg"],
            font=ctk.CTkFont(weight="bold"),
            width=150
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self.show_cases,
            fg_color=COLORS["border"],
            hover_color=COLORS["text_secondary"],
            text_color=COLORS["text_primary"],
            width=150
        ).pack(side="left", padx=10)
    
    def view_case(self, case_id):
        """View case details"""
        self.header_title.configure(text=f"Case: {case_id}")
        self.clear_content()
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM cases WHERE case_id = ?", (case_id,))
        case = cursor.fetchone()
        
        if not case:
            conn.close()
            messagebox.showerror("Error", "Case not found!")
            return
        
        # Get evidence count
        cursor.execute("SELECT COUNT(*) FROM evidence WHERE case_id = ?", (case_id,))
        evidence_count = cursor.fetchone()[0]
        
        # Get notes
        cursor.execute("SELECT * FROM notes WHERE case_id = ? ORDER BY created_date DESC", (case_id,))
        notes = cursor.fetchall()
        
        conn.close()
        
        # Case info card
        info_card = ctk.CTkFrame(self.scroll_frame, fg_color=COLORS["secondary_bg"])
        info_card.pack(fill="x", pady=(0, 15))
        
        # Header with title and back button
        header_frame = ctk.CTkFrame(info_card, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkButton(
            header_frame,
            text="← Back",
            command=self.show_cases,
            fg_color="transparent",
            text_color=COLORS["accent_secondary"],
            hover_color=COLORS["border"],
            font=ctk.CTkFont(size=12)
        ).pack(side="left")
        
        ctk.CTkLabel(
            header_frame,
            text=case[2],
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=15)
        
        # Status dropdown
        status_var = ctk.StringVar(value=case[3])
        status_menu = ctk.CTkOptionMenu(
            header_frame,
            values=["Open", "In Progress", "Closed", "Archived"],
            variable=status_var,
            fg_color=COLORS["primary_bg"],
            button_color=COLORS["border"],
            button_hover_color=COLORS["accent"],
            text_color=COLORS["text_primary"],
            command=lambda s, cid=case_id: self.update_case_status(cid, s)
        )
        status_menu.pack(side="right")
        
        # Details grid
        details_frame = ctk.CTkFrame(info_card, fg_color="transparent")
        details_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        details = [
            ("Case ID", case[1]),
            ("Title", case[2]),
            ("Description", case[3] or "N/A"),
            ("Priority", case[4]),
            ("Investigator", case[5] or "N/A"),
            ("Created", case[6]),
            ("Last Updated", case[7]),
            ("Evidence Items", str(evidence_count))
        ]
        
        for i, (label, value) in enumerate(details):
            row = i // 2
            col = (i % 2) * 2
            
            ctk.CTkLabel(
                details_frame,
                text=f"{label}:",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS["accent_secondary"]
            ).grid(row=row, column=col, sticky="w", padx=(0, 10), pady=5)
            
            ctk.CTkLabel(
                details_frame,
                text=str(value),
                font=ctk.CTkFont(size=12),
                text_color=COLORS["text_primary"]
            ).grid(row=row, column=col+1, sticky="w", pady=5)
        
        # Evidence section
        evidence_section = ctk.CTkFrame(self.scroll_frame, fg_color=COLORS["secondary_bg"])
        evidence_section.pack(fill="x", pady=(0, 15))
        
        evidence_header = ctk.CTkFrame(evidence_section, fg_color="transparent")
        evidence_header.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(
            evidence_header,
            text="📍 Evidence",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left")
        
        ctk.CTkButton(
            evidence_header,
            text="➕ Add Evidence",
            command=lambda: self.add_evidence_form(case_id),
            fg_color=COLORS["accent"],
            hover_color="#00cc7d",
            text_color=COLORS["primary_bg"],
            font=ctk.CTkFont(size=11, weight="bold")
        ).pack(side="right")
        
        # Evidence list
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM evidence WHERE case_id = ?", (case_id,))
        evidence_items = cursor.fetchall()
        conn.close()
        
        if evidence_items:
            for evidence in evidence_items:
                ev_card = ctk.CTkFrame(evidence_section, fg_color=COLORS["primary_bg"])
                ev_card.pack(fill="x", padx=20, pady=5)
                
                ctk.CTkLabel(
                    ev_card,
                    text=f"📄 {evidence[4]}",
                    font=ctk.CTkFont(size=13),
                    text_color=COLORS["text_primary"]
                ).pack(side="left", padx=15, pady=10)
                
                ctk.CTkLabel(
                    ev_card,
                    text=f"Type: {evidence[6]}",
                    font=ctk.CTkFont(size=11),
                    text_color=COLORS["text_secondary"]
                ).pack(side="left", padx=10)
                
                # Hash display
                if evidence[8]:
                    hash_label = ctk.CTkLabel(
                        ev_card,
                        text=f"MD5: {evidence[8][:16]}...",
                        font=ctk.CTkFont(size=10, family="Consolas"),
                        text_color=COLORS["accent_secondary"]
                    )
                    hash_label.pack(side="right", padx=15)
                
                ctk.CTkButton(
                    ev_card,
                    text="🗑️",
                    command=lambda eid=evidence[1]: self.delete_evidence(eid),
                    width=40,
                    fg_color=COLORS["error"],
                    hover_color="#cc3333",
                    text_color="white"
                ).pack(side="right", padx=5)
        else:
            ctk.CTkLabel(
                evidence_section,
                text="No evidence added yet",
                font=ctk.CTkFont(size=12),
                text_color=COLORS["text_secondary"]
            ).pack(pady=15)
        
        # Notes section
        notes_section = ctk.CTkFrame(self.scroll_frame, fg_color=COLORS["secondary_bg"])
        notes_section.pack(fill="both", expand=True)
        
        notes_header = ctk.CTkFrame(notes_section, fg_color="transparent")
        notes_header.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(
            notes_header,
            text="📝 Notes",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left")
        
        ctk.CTkButton(
            notes_header,
            text="➕ Add Note",
            command=lambda: self.add_note_form(case_id),
            fg_color=COLORS["accent_secondary"],
            hover_color="#0099cc",
            text_color=COLORS["primary_bg"],
            font=ctk.CTkFont(size=11, weight="bold")
        ).pack(side="right")
        
        # Notes list
        if notes:
            for note in notes:
                note_card = ctk.CTkFrame(notes_section, fg_color=COLORS["primary_bg"])
                note_card.pack(fill="x", padx=20, pady=5)
                
                ctk.CTkLabel(
                    note_card,
                    text=note[3],
                    font=ctk.CTkFont(size=12),
                    text_color=COLORS["text_primary"],
                    wraplength=600,
                    justify="left"
                ).pack(anchor="w", padx=15, pady=10)
                
                ctk.CTkLabel(
                    note_card,
                    text=note[4],
                    font=ctk.CTkFont(size=10),
                    text_color=COLORS["text_secondary"]
                ).pack(anchor="e", padx=15, pady=(0, 5))
                
                ctk.CTkButton(
                    note_card,
                    text="🗑️",
                    command=lambda nid=note[1]: self.delete_note(nid),
                    width=40,
                    fg_color=COLORS["error"],
                    hover_color="#cc3333",
                    text_color="white"
                ).pack(side="right", padx=(0, 15), pady=10)
        else:
            ctk.CTkLabel(
                notes_section,
                text="No notes added yet",
                font=ctk.CTkFont(size=12),
                text_color=COLORS["text_secondary"]
            ).pack(pady=15)
    
    def update_case_status(self, case_id, status):
        """Update case status"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("UPDATE cases SET status = ?, updated_date = ? WHERE case_id = ?", (status, now, case_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", f"Case status updated to {status}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update status: {str(e)}")
    
    def delete_case(self, case_id):
        """Delete a case"""
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete case {case_id}? This will also delete all associated evidence and notes."):
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM notes WHERE case_id = ?", (case_id,))
                cursor.execute("DELETE FROM evidence WHERE case_id = ?", (case_id,))
                cursor.execute("DELETE FROM cases WHERE case_id = ?", (case_id,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Case deleted successfully!")
                self.show_cases()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete case: {str(e)}")
    
    def add_evidence_form(self, case_id):
        """Show form to add evidence to a case"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Evidence")
        dialog.geometry("500x500")
        dialog.configure(fg_color=COLORS["primary_bg"])
        dialog.transient(self)
        dialog.grab_set()
        
        ctk.CTkLabel(
            dialog,
            text="Add Evidence",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["accent"]
        ).pack(pady=20)
        
        # File selection
        ctk.CTkLabel(
            dialog,
            text="Select File",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        ).pack(pady=(10, 5))
        
        file_path_var = ctk.StringVar()
        
        def select_file():
            filename = filedialog.askopenfilename()
            if filename:
                file_path_var.set(filename)
        
        ctk.CTkButton(
            dialog,
            text="📂 Browse",
            command=select_file,
            fg_color=COLORS["border"],
            text_color=COLORS["text_primary"]
        ).pack()
        
        file_label = ctk.CTkLabel(
            dialog,
            text="No file selected",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"]
        )
        file_label.pack()
        
        # Evidence type
        ctk.CTkLabel(
            dialog,
            text="Evidence Type",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        ).pack(pady=(15, 5))
        
        evidence_type = ctk.CTkOptionMenu(
            dialog,
            values=["Digital Media", "Hard Drive", "Memory Dump", "Network Capture", "Log File", "Document", "Other"],
            fg_color=COLORS["secondary_bg"],
            button_color=COLORS["border"],
            button_hover_color=COLORS["accent"],
            text_color=COLORS["text_primary"]
        )
        evidence_type.pack()
        
        # Description
        ctk.CTkLabel(
            dialog,
            text="Description",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        ).pack(pady=(15, 5))
        
        desc_text = ctk.CTkTextbox(
            dialog,
            fg_color=COLORS["secondary_bg"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            width=400,
            height=80
        )
        desc_text.pack(pady=5)
        
        # Calculate hashes checkbox
        calc_hashes = ctk.CTkCheckBox(
            dialog,
            text="Calculate file hashes (MD5, SHA256)",
            text_color=COLORS["text_primary"],
            fg_color=COLORS["accent"]
        )
        calc_hashes.pack(pady=10)
        calc_hashes.select()
        
        def save_evidence():
            filepath = file_path_var.get()
            if not filepath:
                messagebox.showerror("Error", "Please select a file!")
                return
            
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                
                # Generate evidence ID
                evidence_id = f"EV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                # Get file info
                file_name = os.path.basename(filepath)
                file_size = os.path.getsize(filepath)
                
                # Calculate hashes if requested
                md5_hash = ""
                sha256_hash = ""
                
                if calc_hashes.get():
                    md5_hash = hashlib.md5()
                    sha256_hash = hashlib.sha256()
                    
                    with open(filepath, 'rb') as f:
                        while chunk := f.read(8192):
                            md5_hash.update(chunk)
                            sha256_hash.update(chunk)
                    
                    md5_hash = md5_hash.hexdigest()
                    sha256_hash = sha256_hash.hexdigest()
                
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                cursor.execute(
                    "INSERT INTO evidence (evidence_id, case_id, file_path, file_name, file_size, evidence_type, description, md5_hash, sha256_hash, added_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (evidence_id, case_id, filepath, file_name, file_size, evidence_type.get(), desc_text.get("1.0", "end-1c"), md5_hash, sha256_hash, now)
                )
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "Evidence added successfully!")
                dialog.destroy()
                self.view_case(case_id)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add evidence: {str(e)}")
        
        ctk.CTkButton(
            dialog,
            text="💾 Save Evidence",
            command=save_evidence,
            fg_color=COLORS["accent"],
            hover_color="#00cc7d",
            text_color=COLORS["primary_bg"],
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=20)
    
    def delete_evidence(self, evidence_id):
        """Delete evidence"""
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete evidence {evidence_id}?"):
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM evidence WHERE evidence_id = ?", (evidence_id,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Evidence deleted successfully!")
                # Refresh current view
                self.show_cases()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete evidence: {str(e)}")
    
    def add_note_form(self, case_id):
        """Show form to add a note to a case"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Note")
        dialog.geometry("500x350")
        dialog.configure(fg_color=COLORS["primary_bg"])
        dialog.transient(self)
        dialog.grab_set()
        
        ctk.CTkLabel(
            dialog,
            text="Add Note",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["accent"]
        ).pack(pady=20)
        
        ctk.CTkLabel(
            dialog,
            text="Note Content",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        ).pack(pady=(10, 5))
        
        note_text = ctk.CTkTextbox(
            dialog,
            fg_color=COLORS["secondary_bg"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            width=400,
            height=150
        )
        note_text.pack(pady=10)
        
        def save_note():
            content = note_text.get("1.0", "end-1c").strip()
            if not content:
                messagebox.showerror("Error", "Please enter note content!")
                return
            
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                
                note_id = f"NOTE-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                cursor.execute(
                    "INSERT INTO notes (note_id, case_id, content, created_date) VALUES (?, ?, ?, ?)",
                    (note_id, case_id, content, now)
                )
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "Note added successfully!")
                dialog.destroy()
                self.view_case(case_id)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add note: {str(e)}")
        
        ctk.CTkButton(
            dialog,
            text="💾 Save Note",
            command=save_note,
            fg_color=COLORS["accent"],
            hover_color="#00cc7d",
            text_color=COLORS["primary_bg"],
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=20)
    
    def delete_note(self, note_id):
        """Delete a note"""
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete this note?"):
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM notes WHERE note_id = ?", (note_id,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Note deleted successfully!")
                self.show_cases()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete note: {str(e)}")
    
    def import_evidence(self):
        """Import evidence - shows case selector first"""
        self.show_cases()
    
    def show_evidence(self):
        """Show all evidence across all cases"""
        self.header_title.configure(text="Evidence Inventory")
        self.clear_content()
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM evidence ORDER BY added_date DESC")
        all_evidence = cursor.fetchall()
        conn.close()
        
        if not all_evidence:
            ctk.CTkLabel(
                self.scroll_frame,
                text="No evidence in the system",
                font=ctk.CTkFont(size=14),
                text_color=COLORS["text_secondary"]
            ).pack(pady=30)
            return
        
        # Table header
        header = ctk.CTkFrame(self.scroll_frame, fg_color=COLORS["secondary_bg"])
        header.pack(fill="x", pady=(0, 5))
        
        headers = ["Evidence ID", "Case", "File Name", "Type", "Hash (MD5)", "Date"]
        for i, h in enumerate(headers):
            ctk.CTkLabel(
                header,
                text=h,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=COLORS["accent_secondary"]
            ).pack(side="left", padx=10, pady=10)
        
        for evidence in all_evidence:
            row = ctk.CTkFrame(self.scroll_frame, fg_color=COLORS["secondary_bg"])
            row.pack(fill="x", pady=2)
            
            data = [
                evidence[1],
                evidence[2],
                evidence[4][:20] + "..." if len(evidence[4]) > 20 else evidence[4],
                evidence[6],
                (evidence[8] or "N/A")[:16] + "..." if evidence[8] and len(evidence[8]) > 16 else (evidence[8] or "N/A"),
                evidence[10][:10] if evidence[10] else "N/A"
            ]
            
            for d in data:
                ctk.CTkLabel(
                    row,
                    text=d,
                    font=ctk.CTkFont(size=10),
                    text_color=COLORS["text_primary"]
                ).pack(side="left", padx=10, pady=8)
    
    def show_reports(self):
        """Show reports view"""
        self.header_title.configure(text="Reports")
        self.clear_content()
        
        report_frame = ctk.CTkFrame(self.scroll_frame, fg_color=COLORS["secondary_bg"])
        report_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            report_frame,
            text="Generate Reports",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["accent"]
        ).pack(pady=20)
        
        # Case summary report
        ctk.CTkButton(
            report_frame,
            text="📊 Case Summary Report",
            command=self.generate_case_summary_report,
            fg_color=COLORS["accent_secondary"],
            hover_color="#0099cc",
            text_color=COLORS["primary_bg"],
            font=ctk.CTkFont(weight="bold"),
            width=250
        ).pack(pady=10)
        
        # Export all cases
        ctk.CTkButton(
            report_frame,
            text="📁 Export All Cases (JSON)",
            command=self.export_all_cases_json,
            fg_color=COLORS["accent"],
            hover_color="#00cc7d",
            text_color=COLORS["primary_bg"],
            font=ctk.CTkFont(weight="bold"),
            width=250
        ).pack(pady=10)
        
        # Evidence inventory
        ctk.CTkButton(
            report_frame,
            text="🔍 Evidence Inventory",
            command=self.generate_evidence_report,
            fg_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            width=250
        ).pack(pady=10)
    
    def generate_case_summary_report(self):
        """Generate a summary report of all cases"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM cases")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT status, COUNT(*) FROM cases GROUP BY status")
        status_counts = cursor.fetchall()
        
        cursor.execute("SELECT priority, COUNT(*) FROM cases GROUP BY priority")
        priority_counts = cursor.fetchall()
        
        conn.close()
        
        report = f"""
=== CYBER FORENSICS CASE SUMMARY REPORT ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

TOTAL CASES: {total}

STATUS BREAKDOWN:
"""
        for status, count in status_counts:
            report += f"  - {status}: {count}\n"
        
        report += "\nPRIORITY BREAKDOWN:\n"
        for priority, count in priority_counts:
            report += f"  - {priority}: {count}\n"
        
        # Save to file
        filename = f"case_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w') as f:
            f.write(report)
        
        messagebox.showinfo("Report Generated", f"Report saved to {filename}")
    
    def export_all_cases_json(self):
        """Export all cases to JSON"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM cases")
        cases = cursor.fetchall()
        
        data = {"cases": [], "export_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        for case in cases:
            case_dict = {
                "case_id": case[1],
                "title": case[2],
                "description": case[3],
                "status": case[4],
                "priority": case[5],
                "investigator": case[6],
                "created_date": case[7],
                "updated_date": case[8]
            }
            
            # Get evidence
            cursor.execute("SELECT * FROM evidence WHERE case_id = ?", (case[1],))
            evidence = cursor.fetchall()
            case_dict["evidence"] = [
                {
                    "evidence_id": e[1],
                    "file_name": e[4],
                    "file_size": e[5],
                    "evidence_type": e[6],
                    "description": e[7],
                    "md5_hash": e[8],
                    "sha256_hash": e[9],
                    "added_date": e[10]
                } for e in evidence
            ]
            
            # Get notes
            cursor.execute("SELECT * FROM notes WHERE case_id = ?", (case[1],))
            notes = cursor.fetchall()
            case_dict["notes"] = [
                {
                    "note_id": n[1],
                    "content": n[3],
                    "created_date": n[4]
                } for n in notes
            ]
            
            data["cases"].append(case_dict)
        
        conn.close()
        
        # Save to file
        filename = f"forensics_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        messagebox.showinfo("Export Complete", f"Data exported to {filename}")
    
    def generate_evidence_report(self):
        """Generate evidence inventory report"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM evidence ORDER BY added_date DESC")
        evidence = cursor.fetchall()
        
        conn.close()
        
        report = f"""
=== EVIDENCE INVENTORY REPORT ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Total Evidence Items: {len(evidence)}

"""
        
        for e in evidence:
            report += f"""
---
Evidence ID: {e[1]}
Case: {e[2]}
File: {e[4]}
Type: {e[6]}
Description: {e[7] or 'N/A'}
MD5: {e[8] or 'N/A'}
SHA256: {e[9] or 'N/A'}
Added: {e[10]}
"""
        
        filename = f"evidence_inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w') as f:
            f.write(report)
        
        messagebox.showinfo("Report Generated", f"Report saved to {filename}")
    
    def show_settings(self):
        """Show settings view"""
        self.header_title.configure(text="Settings")
        self.clear_content()
        
        settings_frame = ctk.CTkFrame(self.scroll_frame, fg_color=COLORS["secondary_bg"])
        settings_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            settings_frame,
            text="Application Settings",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["accent"]
        ).pack(pady=20)
        
        # Database info
        ctk.CTkLabel(
            settings_frame,
            text="Database",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w", padx=20, pady=(10, 5))
        
        ctk.CTkLabel(
            settings_frame,
            text=f"Database file: {self.db.db_path}",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w", padx=20)
        
        # Stats
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM cases")
        cases_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM evidence")
        evidence_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM notes")
        notes_count = cursor.fetchone()[0]
        
        conn.close()
        
        ctk.CTkLabel(
            settings_frame,
            text=f"Total Cases: {cases_count}",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w", padx=20, pady=2)
        
        ctk.CTkLabel(
            settings_frame,
            text=f"Total Evidence: {evidence_count}",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w", padx=20, pady=2)
        
        ctk.CTkLabel(
            settings_frame,
            text=f"Total Notes: {notes_count}",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w", padx=20, pady=2)
        
        # About
        about_frame = ctk.CTkFrame(self.scroll_frame, fg_color=COLORS["secondary_bg"])
        about_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(
            about_frame,
            text="About",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w", padx=20, pady=(15, 10))
        
        ctk.CTkLabel(
            about_frame,
            text="CyberForensics Manager v1.0.0",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w", padx=20)
        
        ctk.CTkLabel(
            about_frame,
            text="A comprehensive case management system for digital forensic investigators.",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"],
            wraplength=600,
            justify="left"
        ).pack(anchor="w", padx=20, pady=5)
    
    def perform_search(self):
        """Search cases"""
        search_term = self.search_entry.get().strip()
        if not search_term:
            self.show_cases()
            return
        
        self.header_title.configure(text=f"Search: {search_term}")
        self.clear_content()
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT case_id, title, description, status, priority, investigator, created_date FROM cases WHERE case_id LIKE ? OR title LIKE ? OR description LIKE ?",
            (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%")
        )
        results = cursor.fetchall()
        conn.close()
        
        ctk.CTkLabel(
            self.scroll_frame,
            text=f"Found {len(results)} results for '{search_term}'",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_secondary"]
        ).pack(pady=10)
        
        for case in results:
            case_card = ctk.CTkFrame(self.scroll_frame, fg_color=COLORS["secondary_bg"])
            case_card.pack(fill="x", pady=8)
            
            ctk.CTkLabel(
                case_card,
                text=f"📁 {case[1]}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=COLORS["text_primary"]
            ).pack(anchor="w", padx=15, pady=10)
            
            ctk.CTkLabel(
                case_card,
                text=f"ID: {case[0]} | Status: {case[3]}",
                font=ctk.CTkFont(size=11),
                text_color=COLORS["text_secondary"]
            ).pack(anchor="w", padx=15)
            
            ctk.CTkButton(
                case_card,
                text="👁️ View",
                command=lambda c=case[0]: self.view_case(c),
                width=70,
                fg_color=COLORS["accent_secondary"],
                hover_color="#0099cc",
                text_color=COLORS["primary_bg"],
                font=ctk.CTkFont(size=11)
            ).pack(anchor="e", padx=15, pady=10)


def main():
    app = CyberForensicsApp()
    app.mainloop()


if __name__ == "__main__":
    main()

