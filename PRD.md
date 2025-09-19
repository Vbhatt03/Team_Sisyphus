# **Product Requirements Document: NYAYA AI**


## **1\. Vision & Problem Statement**

### **1.1. Problem Statement**

The investigation of sexual offenses is a procedurally intensive process governed by strict legal timelines and protocols (BNS, BNSS, POCSO Act, SOPs). Investigating Officers (IOs) are overburdened with manual documentation, complex compliance tracking, and the pressure to build legally watertight cases. Critical procedural errors—such as missing the 24-hour deadline for a victim's judicial statement, improper evidence seizure, or incomplete documentation—are common. These lapses create legal loopholes that often lead to the acquittal of the guilty, failing both the victim and the justice system. The current workflow is fragmented, paper-based, and lacks intelligent oversight, leading to inefficiencies and reduced conviction rates.

### **1.2. Product Vision**

To empower every Investigating Officer with an intelligent, end-to-end digital investigation platform that guarantees 100% procedural compliance. NYAYA AI will transform sexual offence investigations by automating documentation, providing proactive legal guidance, and ensuring every case file is meticulously prepared for trial, thereby increasing conviction rates and delivering swifter justice.

## **2\. User Personas & Scenarios**

### **2.1. Primary Persona: Investigating Officer (IO)**

* **Role:** Manages the entire lifecycle of a sexual offence investigation, from FIR to chargesheet.  
* **Goals:** To conduct a thorough and fair investigation, collect admissible evidence, and ensure the guilty are convicted.  
* **Frustrations:**  
  * "I spend more time on paperwork than on actual investigation."  
  * "It's impossible to remember every single deadline and procedural nuance for a POCSO case versus a standard BNS case."  
  * "I live in constant fear that a small mistake in a seizure memo or a missed deadline will get my entire case thrown out of court."

### **2.2. Secondary Persona: Supervisory Officer (ACP/DCP)**

* **Role:** Oversees multiple IOs and ensures the quality and compliance of investigations within their jurisdiction.  
* **Goals:** To improve the overall conviction rate, reduce procedural errors, and ensure adherence to SOPs.  
* **Frustrations:**  
  * "I have no real-time visibility into the status of critical cases. I only find out about problems when it's too late."  
  * "Reviewing a case file for compliance is a manual, time-consuming process of sifting through hundreds of pages."

## **3\. Core Principles & UX Philosophy**

* **Guidance, Not Obstruction:** The tool should feel like an expert partner, not a rigid taskmaster. It guides the IO through the correct process without hindering their ability to apply their own investigative judgment.  
* **Single Source of Truth:** All case-related documents, evidence logs, and notes live in one centralized, secure digital case file, eliminating redundancy and confusion.  
* **Automate the Mundane, Empower the Human:** Automate repetitive tasks like documentation and deadline tracking to free up the IO's cognitive bandwidth for critical thinking and on-the-ground investigation.  
* **Data-Driven, Not Data-Entry-Driven:** The UI should be intelligent. Every piece of data entered (e.g., a case diary entry) should actively contribute to building the final report, not just sit in a database.

## **4\. Detailed Feature Breakdown**

The application is structured around a central "Investigation Workspace" for each case.

### **Module 1: Case Initiation & Strategic Planning**

This module ensures every case starts on a solid, legally compliant foundation.

**1.1. AI-Powered Case Intake Wizard:**

* **Description:** Upon receiving a new case, the IO initiates a "New Case File" wizard. The IO can upload the FIR (PDF/Image/Text).  
* **AI Functionality:** The system uses OCR and NLP to parse the FIR and pre-fill a structured form with key details: victim's name (to be pseudonymized), age, alleged sections of law, known accused, and a summary of the incident.  
* **IO Verification:** The IO verifies the AI-extracted data and adds any missing context. The victim's age is a critical field that determines if POCSO Act protocols apply.  
* **Output:** A digital case file is created.

**1.2. Dynamic Investigation Roadmap Generator:**

* **Description:** Based on the verified case details, the system generates a dynamic, step-by-step roadmap for the investigation.  
* **AI Functionality:** The rules engine maps the case facts (e.g., victim age \< 18, gang rape allegation) to the specific requirements of the BNS, POCSO Act, and official SOPs.  
* **Output:** The roadmap is displayed as an interactive checklist within the Investigation Workspace, with each task assigned a priority and a legally mandated deadline (e.g., Victim's Statement u/s 183 BNSS \- Deadline: 20/09/2025 15:00).

### **Module 2: The Investigation Workspace**

This is the central hub for managing all aspects of an active investigation.

**2.1. Interactive Compliance Checklist:**

* **Description:** The core of the workspace. It displays all tasks from the roadmap.  
* **User Interaction:** The IO can click on any task to view:  
  * **SOP Guidance:** The exact text from the relevant SOP or law.  
  * **Document Templates:** Pre-filled templates for required documents (e.g., Seizure Memo, Arrest Memo).  
  * **Upload Link:** A prompt to upload the corresponding evidence/document.  
* **Status Tracking:** Uploading a document automatically marks the task as "Completed" and updates the compliance monitor. Deadlines are tracked in real-time.  
  * **GREEN:** Completed on time.  
  * **AMBER:** Deadline approaching (within 12 hours).  
  * **RED:** Deadline missed.

**2.2. Digital Evidence Locker:**

* **Description:** A centralized, secure repository for all case documents. Every file uploaded (FIR, medical reports, witness statements, crime scene photos, lab reports) is stored here.  
* **Features:**  
  * **Timestamping:** Every upload is automatically timestamped.  
  * **AI-Tagging:** The system automatically tags documents (e.g., "Medical Report \- Victim," "Forensic Report \- DNA").  
  * **Chain of Custody:** A digital log is maintained for each piece of evidence, tracking its movement and handling (stretch goal).  
  * **Secure & Searchable:** All documents are encrypted at rest and are fully searchable.

**2.3. Structured Case Diary Module:**

* **Description:** This feature replaces the traditional, free-text case diary. It's designed for **progressive report building**.  
* **User Interaction:** To make a daily entry, the IO uses a structured form:  
  1. **Select Activity Type:** Dropdown (e.g., *Witness Interrogation*, *Evidence Seizure*, *Accused Interrogation*, *Crime Scene Visit*).  
  2. **Date & Time:** Auto-filled but editable.  
  3. **Summary of Action:** A text box for the narrative.  
  4. **Link to Checklist Item:** The IO links the diary entry to a specific task on the compliance checklist.  
  5. **Link to Evidence:** The IO can directly upload a document (e.g., a witness statement) from this interface, which gets stored in the Evidence Locker.  
* **Benefit:** This structured data is machine-readable and directly feeds into the final chargesheet, ensuring the narrative is backed by logged actions and evidence.

### **Module 3: AI-Assisted Final Report Generation**

This module transforms the laborious task of writing the chargesheet into a simple review process.

**3.1. Chargesheet Builder:**

* **Description:** When the investigation is nearing completion, the IO initiates the "Generate Chargesheet" process.  
* **AI Functionality:** The system acts as an intelligent compiler:  
  * It chronologically assembles all **structured case diary entries** to form the core investigative narrative.  
  * It pulls in details of all witnesses, accused persons, and seized articles from the database.  
  * It attaches all relevant documents from the **Digital Evidence Locker** as annexures.  
  * It cross-references the narrative with the evidence, flagging potential inconsistencies (e.g., "Narrative mentions a weapon, but the Seizure Memo for the weapon is not uploaded").  
* **Output:** A complete, well-formatted draft of the chargesheet is presented to the IO for review, editing, and final approval before being exported as a court-ready PDF.

### **Module 4: Judicial Intelligence Engine**

This module provides proactive legal insights to build a stronger case.

**4.1. Precedent and Pitfall Analysis:**

* **Description:** This engine is integrated throughout the workspace.  
* **Proactive Guidance:** Based on the case facts, the system proactively provides alerts.  
  * *Example:* If the FIR was filed 2 days after the incident, an alert appears: "High courts often scrutinize delayed FIRs. Ensure the victim's statement clearly explains the reason for the delay. See *State of Punjab v. Gurmit Singh* for relevant precedent."  
* **On-Demand Search:** The IO can use a natural language search bar to query a curated database of landmark Supreme Court and High Court judgments on specific topics (e.g., "Evidentiary value of a retracted confession").

### **Module 5: Supervisory Dashboard**

**5.1. Command Center View:**

* **Description:** A secure, read-only dashboard for designated Supervisory Officers.  
* **Features:**  
  * A high-level view of all active sexual offence cases in their jurisdiction.  
  * Cases are color-coded by their overall compliance status (e.g., a case with any "RED" task is flagged as high-risk).  
  * Ability to drill down into any case to view its Investigation Workspace without being able to edit it.  
  * Analytics and reporting on compliance trends, common procedural errors, and IO performance.

## **5\. User Flow**

1. **IO Login** \-\> **Dashboard** \-\> **"Start New Case"**  
2. **Case Intake Wizard:** Upload FIR \-\> AI Parse \-\> IO Verify Data \-\> **Case File Created**.  
3. **Investigation Workspace:**  
   * Review **Dynamic Roadmap/Checklist**.  
   * **Perform Task** (e.g., get medical exam done).  
   * **Update Workspace:**  
     * Upload Medical Report to **Digital Evidence Locker**.  
     * Checklist item auto-updates to **GREEN**.  
     * Create a **Structured Case Diary Entry**, linking it to the medical exam task and report.  
4. *(Repeat Step 3 for all investigative actions)*.  
5. **Final Stage:** Click **"Generate Chargesheet"**.  
6. **Chargesheet Builder:** AI compiles all data \-\> IO reviews/edits the draft \-\> **Export Final PDF**.  
7. **Supervisor Login** \-\> **Supervisory Dashboard** \-\> View all cases \-\> Drill down to specific Case Workspace.

## **6\. Non-Functional Requirements (Production Grade)**

* **Security:**  
  * **Role-Based Access Control (RBAC):** Strict permissions for IOs (read/write on their cases) and Supervisors (read-only on cases in their jurisdiction).  
  * **Data Encryption:** End-to-end encryption for data at rest (AES-256) and in transit (TLS 1.3).  
  * **Audit Trails:** Immutable logs of every action taken within the system.  
  * **Deployment:** Must be deployable on a secure, government-approved cloud or on-premise infrastructure.  
* **Scalability:** The architecture must be able to handle thousands of concurrent cases and users across multiple districts or an entire state. This implies stateless application servers and a robust, scalable database.  
* **Availability:** The system must have a high uptime of \>99.9%, with robust backup and disaster recovery mechanisms.  
* **Interoperability:** The system should be designed with APIs to potentially integrate with existing Crime and Criminal Tracking Network & Systems (CCTNS).

## **7\. Technology Stack (Proposed for Production)**

* **Frontend:** React.js or Angular (for a robust, scalable single-page application).  
* **Backend:** Python (FastAPI/Django) or Node.js (Express.js) for building secure, scalable APIs.  
* **Database:** PostgreSQL or MySQL for structured data.  
* **NLP/AI:** Hugging Face Transformers (for Legal-BERT models), spaCy, and custom ML models for classification and entity recognition.  
* **Search:** Elasticsearch for powering the judicial intelligence search engine.  
* **Deployment:** Docker for containerization, Kubernetes for orchestration, deployed on a secure cloud (e.g., AWS GovCloud) or on-premise servers.

## **8\. Success Metrics**

* **Efficiency:** 50% reduction in the average time taken to prepare and file a chargesheet.  
* **Compliance:** 95%+ rate of on-time completion for all legally mandated, time-bound procedures (e.g., 24-hour rules).  
* **Effectiveness:** A 15% increase in the conviction rate for cases investigated using NYAYA AI over a 24-month period.  
* **Adoption:** 80% of IOs in the pilot district actively use the platform as their primary tool for managing sexual offence investigations.

## **9\. Future Roadmap (Post-MVP)**

* **Multi-language Support:** To accommodate the diverse languages across India.  
* **Mobile Application:** A lightweight mobile app for IOs to make case diary entries and upload evidence directly from the field.  
* **Predictive Analytics:** An ML model to predict cases at high risk of acquittal based on early procedural data, allowing for timely intervention.  
* **Expansion:** Adapting the platform to handle other types of complex criminal investigations (e.g., homicide, financial fraud).