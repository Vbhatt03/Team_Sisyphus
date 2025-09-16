PRD: NYAYA AI – AI-Powered Sexual Offence Investigation Guide
1. Product Overview

NYAYA AI is an AI-driven assistant designed to support Investigating Officers (IOs) in handling sexual offence cases. The tool ensures legal compliance, integrates judicial guidance, and generates standardized documentation, thereby reducing procedural lapses and improving conviction rates.

2. Goals & Objectives

Primary Goal: Provide an investigation assistant that ensures SOP-compliant sexual offence investigations.

Objectives:

Generate case-specific investigation roadmaps based on FIRs, SOPs, and laws (BNS 2023, POCSO, IT Act).

Provide judgment-based insights by analyzing court rulings to highlight admissibility of evidence, pitfalls, and judicial expectations.

Auto-generate case diaries, charge sheets, and reports in standardized formats.

Monitor investigation progress, flagging missing steps and suggesting corrective actions.

3. Target Users

Primary: Investigating Officers (IOs) handling sexual offence cases.

Secondary: Supervisory officers overseeing compliance with SOPs.

4. Key Deliverables (Hackathon Priority)
MVP Features (must-have)

Legal Intelligence Engine

Input: FIR (structured/unstructured).

Output: Applicable legal sections (BNS, POCSO, IT Act).

Generate checklist with mandatory steps, evidence requirements, and deadlines.

Court Judgment Analyzer

Upload feature for judgments (PDF/text).

Extract admissibility issues, pitfalls, and expectations from higher courts.

Provide search & precedent-matching with relevant cases.

Compliance Monitoring System

Track whether critical steps (medical exam, Sec. 183 BNSS victim statement, digital evidence collection) are done.

Flag missing or delayed steps.

Provide corrective action guidance.

Automated Documentation Generator

Standardized Case Diary and Charge Sheet templates.

Auto-fill from case facts + compliance tracker.

Export to tamper-proof PDF.

5. Stretch Goals (time permitting)

Predictive conviction probability (ML classifier on compliance dataset).

Blockchain-secured evidence log.

Officer training module with interactive case studies.

Multi-modal evidence (image/audio metadata extraction).

6. Functional Requirements
Module	Requirements
Case Intake	Accept structured form or FIR text; parse key facts (victim age, type of offence, reported evidence).
Legal Roadmap Generator	Map facts to applicable legal sections; create JSON checklist of tasks & deadlines.
Compliance Tracker	Track task completion; compare with statutory deadlines; highlight violations.
Judgment Analyzer	Convert uploaded judgments to text; embed using Legal-BERT/SBERT; retrieve similar cases; summarize pitfalls.
Auto-doc Generator	Populate standardized templates (case diary, charge sheet) with case details & compliance data; export as PDF.
Dashboard	Tabs for Case Intake, Compliance, Judgments, Reports; Red/Green indicators for compliance.
7. Non-Functional Requirements

Usability: Simple, intuitive UI for officers (Streamlit dashboard).

Performance: End-to-end case processing under 5 seconds.

Security: Local-only data processing for hackathon demo; no external API leaks.

Scalability: Can later expand to other IPC/BNS offences beyond sexual offences.

8. Tech Stack

Frontend/UI: Streamlit (rapid prototyping).

Backend: Python + FastAPI.

NLP: Hugging Face (Legal-BERT, SBERT), spaCy.

Vector Search: FAISS / ChromaDB.

Database: SQLite (hackathon) → Postgres (scalable).

Docs: Jinja2 templates + pdfkit.

9. Success Metrics (Hackathon Evaluation)

Working demo: Case input → checklist + compliance → judgment insights → auto-doc PDF.

Clear compliance visualization (traffic-light style).

Judges see direct impact: “Every IO using NYAYA AI will never miss SOP steps → improved conviction rates.”

10. Timeline (48 hours hackathon)

Day 1: Dataset exploration, Legal SOP engine, UI scaffold.

Day 2: Judgment analyzer + auto-doc generator.

Day 3: Compliance monitor polish + integration + presentation.
