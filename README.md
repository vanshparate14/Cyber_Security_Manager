# Cyber Forensics File Manager

[![License: VP](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)

A comprehensive **GUI application** for digital forensic investigators to manage cases, track evidence with cryptographic hashes (MD5/SHA256), maintain notes, generate reports, and export data.

## 🛡️ **Understand using STAR Anamoly**

### **Strategy** (High-Level Approach)
Built with a **SQLite-backed MVC architecture** using **CustomTkinter** for modern dark-mode UI. Emphasizes:
- **Chain-of-Custody**: Automatic file hashing and timestamping
- **Data Integrity**: ACID-compliant database transactions
- **User Experience**: Intuitive dashboard with real-time stats and quick actions
- **Exportability**: JSON/TXT reports for court admissibility

### **Task** (Core Functionality)
Digital forensics workflow automation:
1. **Case Management**: Create/track/update cases with priority/status/investigator assignment
2. **Evidence Tracking**: Secure file cataloging with metadata, hashes, file size/type
3. **Investigation Notes**: Timestamped, searchable case notes
4. **Reporting**: Automated summaries and full exports
5. **Analytics**: Dashboard with case/evidence stats

### **Analysis** (Technical Implementation)
```
Database Schema:
├── cases (case_id, title, description, status, priority, investigator, timestamps)
├── evidence (evidence_id, case_id, file_path, hashes, type, description, timestamps)
└── notes (note_id, case_id, content, timestamps)

UI Components:
├── Dark-mode CustomTkinter (responsive 1200x700+)
├── Sidebar navigation (Dashboard/Cases/Evidence/Reports/Settings)
├── Real-time stats cards
├── Search/filter capabilities
└── CRUD modals with validation
```

**Key Features:**
- ✅ File hash computation (MD5 + SHA256)
- ✅ Export to JSON (full data) + TXT summaries
- ✅ Evidence chain-of-custody tracking
- ✅ Priority/status filtering
- ✅ Responsive grid layouts

### **Report** (Outcomes & Usage)
**Sample Usage Data** (generated files):
```
Case Summary (Date):
- TOTAL CASES: 2 Cases
- Priorities: 1 Critical, 1 High
```
**JSON Export Structure**: Hierarchical cases → evidence/notes

## 🚀 **Quick Start**

### Prerequisites
```bash
Python 3.8+
pip install customtkinter
```

### Run
```bash
cd c:/Users/Acer/Desktop/Cyber_security_manager
python cyber_forensics_manager.py
```

### Database
- Auto-creates `forensics_db.sqlite`
- Migrates automatically

## 📁 **Project Structure**
```
Cyber_security_manager/
├── cyber_forensics_manager.py    # Main GUI app
├── forensics_db.sqlite           # SQLite database
├── forensics_export_*.json       # Case exports
├── case_summary_*.txt           # Reports
├── 1.png - 5.png                # UI screenshots
└── README.md                    # This file
```

## 🛠️ **Features Demo**

**Dashboard:**
- Stats cards (Total/Open/Closed cases, Evidence count)
- Recent cases list
- Quick actions (New Case, Import Evidence, Generate Report)

**Case View:**
```
Case CF-2024-001: "Malware Investigation"
├── Priority: Critical    Status: Open
├── Investigator: John Doe
├── Evidence: malware.exe (MD5: a1b2c3...)
├── Notes: "Suspicious API calls detected"
└── Actions: Add Evidence | Update Status | Delete
```

## 🔧 **Advanced Usage**

1. **Bulk Export**: Reports → "Export All Cases (JSON)"
2. **Evidence Hashing**: Auto-calculates on import (opt-in)
3. **Search**: Real-time across case title/description/ID
4. **Filters**: Status/priority dropdowns

## 📊 **Sample Reports Generated**
```
case_summary_20260322_200339.txt:
TOTAL CASES: 2 | Open: 1 | Critical: 1 | High: 0
```

## 🤝 **Contributing**
1. Fork the repo
2. Create feature branch (`git checkout -b feature/evidence-timeline`)
3. Commit changes (`git commit -m 'Add evidence timeline'`)
4. Push (`git push origin feature/evidence-timeline`)
5. Open Pull Request

## 📄 **License**
MIT License - see [LICENSE](LICENSE) for details.

## 👨‍💻 **Author**
**Vansh Parate** - Cyber Forensics Manager v1.0.0

---

⭐ **Star this project if it helps your investigations!** 🚀

