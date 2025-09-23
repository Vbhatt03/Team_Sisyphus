# CaseFlow - Legal Case Management System

A localhost web application that implements a complete legal case processing workflow, integrating existing Python scripts for document parsing and report generation with a modern web interface.

## Architecture

- **Backend**: FastAPI (Python 3.11), SQLModel + SQLite, session-based authentication
- **Frontend**: React + Vite + TypeScript, React Router, Zustand for state management
- **Storage**: Local filesystem under `./data/{caseId}/` with SQLite database
- **Processing**: Existing Python scripts for PDF parsing and report generation

## Project Structure

```
caseflow/
├── backend/           # FastAPI application
├── frontend/          # React application  
├── data/              # Case data storage (gitignored)
├── scripts/           # Wrapper scripts
└── README.md
```

## Implementation Notes

### Existing Script Analysis

Based on inspection of the provided Python scripts, here are the key findings:

#### 1. JSON Generator (`json_generator/local_main.py`)

**Purpose**: Orchestrates PDF parsing using OCR.space API  
**CLI Invocation**: `python local_main.py` (no arguments, uses config.yaml)  
**Input**: 
- PDFs in directory specified by `config.yaml` → `paths.input_directory`  
- OCR.space API key from `config.yaml` → `ocr_space_api_key`  
**Output**: JSON files in `config.yaml` → `paths.output_directory`  
**File Routing**: Uses filename keywords to route to appropriate parsers:
- "fir" → `process_fir_pdf()`
- "statement" → `process_statement_pdf()`  
- "medical", "victim", "accuse" → `process_medical_pdf()`

**Key Functions**:
- `process_fir_pdf(pdf_path: str, api_key: str) -> dict`
- `process_statement_pdf(pdf_path: str, api_key: str) -> dict`  
- `process_medical_pdf(pdf_path: str, api_key: str) -> dict`

#### 2. Compliance Checklist Generator (`Report_generator/compliance_checklist_generator.py`)

**Purpose**: Generates SOP compliance checklist by comparing case data against rules  
**CLI Invocation**: `python compliance_checklist_generator.py` (no arguments, uses hardcoded paths)  
**Input**: 
- JSON files: `FIR.json`, `statement.json`, `victim_med_rep.json`, `accused_med_rep.json`
- Rules file: `rules_output.json`  
**Output**: `compliance_checklist.md` (Markdown format with checkboxes)  
**Dependencies**: All input JSON files must exist

#### 3. Case Diary Generator (`Report_generator/case_diary_generator.py`)

**Purpose**: Creates case diary from parsed JSON data  
**CLI Invocation**: `python case_diary_generator.py` (no arguments, uses hardcoded paths)  
**Input**: Same JSON files as compliance generator + `fir.json`  
**Output**: `case_diary.txt` (plain text format)  
**Dependencies**: FIR, statement, and both medical reports required

#### 4. Chargesheet Generator (`Report_generator/report_chargesheet_generator.py`) 

**Purpose**: Generates final report and chargesheet  
**CLI Invocation**: `python report_chargesheet_generator.py` (no arguments, uses hardcoded paths)  
**Input**: All JSON files + `case_diary.txt` from previous step  
**Output**: 
- `final_report.txt` (comprehensive summary)
- `chargesheet.md` (Markdown format)  
**Dependencies**: Requires case diary to be generated first

### Configuration Requirements

- **OCR.space API Key**: Required for PDF parsing (currently hardcoded: `"K88629238088957"`)
- **File Paths**: All scripts use absolute paths that need to be adapted for case-based storage
- **Processing Order**: Must follow: Parse → Compliance → Case Diary → Chargesheet

### Key Adaptations Needed

1. **Dynamic Path Configuration**: Replace hardcoded paths with case-based directory structure
2. **Function-based Invocation**: Import and call functions directly instead of CLI execution  
3. **Error Handling**: Add proper error handling for missing files (medical reports can be optional)
4. **Output Parsing**: Parse generated Markdown files into structured data for web interface

## Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- OCR.space API key

### Installation

```bash
# Clone and setup
cd caseflow

# Backend setup
cd backend
pip install -r requirements.txt

# Frontend setup  
cd ../frontend
npm install

# Run development servers
make dev-backend  # or: uvicorn backend.main:app --reload
make dev-frontend # or: npm run dev
```

### Environment Variables

Create `.env` files:

**backend/.env:**
```
OCR_SPACE_API_KEY=your_api_key_here
DATABASE_URL=sqlite:///./caseflow.db
SECRET_KEY=your_secret_key_for_sessions
```

**frontend/.env:**
```
VITE_API_URL=http://localhost:8000
```

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login with username/password
- `GET /api/auth/me` - Get current user info

### Case Management  
- `POST /api/cases` - Create new case
- `GET /api/cases` - List user's cases

### File Upload & Processing
- `POST /api/upload` - Upload PDF files  
- `POST /api/parse` - Parse uploaded PDFs to JSON
- `GET /api/files` - List case files
- `GET /api/files/download` - Download files

### Workflow Steps
- `POST /api/compliance/run` - Generate compliance checklist
- `GET /api/compliance` - Get checklist items  
- `PATCH /api/compliance/:id` - Update checklist item
- `POST /api/case-diary/generate` - Generate case diary
- `GET /api/case-diary` - Get case diary page
- `PUT /api/case-diary` - Save case diary page
- `POST /api/chargesheet/generate` - Generate final reports

## Frontend Pages

1. **Login** - Simple authentication form
2. **Upload Wizard** - 4-step PDF upload process
3. **Compliance** - Interactive checklist with edit capabilities  
4. **Case Diary** - Multi-page editor with save/navigation
5. **Final** - File downloads and preview

## File Storage Structure

```
data/
├── {caseId}/
│   ├── uploads/
│   │   ├── fir.pdf
│   │   ├── statement.pdf  
│   │   ├── victim_med.pdf (optional)
│   │   └── accused_med.pdf (optional)
│   └── outputs/
│       ├── json/
│       │   ├── fir.json
│       │   ├── statement.json
│       │   ├── victim_med_rep.json
│       │   └── accused_med_rep.json  
│       ├── compliance/
│       │   └── compliance_checklist.md
│       ├── case_diary/  
│       │   └── case_diary.txt
│       └── final/
│           ├── final_report.txt
│           └── chargesheet.md
```

## Testing

### End-to-End Test with Sample PDFs

1. Start both servers
2. Login with demo credentials
3. Upload sample PDFs from `New_reports/` folder:
   - `fir.pdf` → FIR step
   - `statement.pdf` → Statement step  
   - Skip medical reports or upload `victim_med_rep.pdf`, `accused_med_rep.pdf`
4. Parse documents → Verify JSON files generated
5. Generate compliance checklist → Verify checklist appears and is editable
6. Generate case diary → Verify pages are navigable and editable
7. Generate final reports → Verify files are downloadable

### Seed Data Command

```bash
python backend/seed.py
```

Creates demo user and sample case with provided PDFs.

---

## Known Issues & Limitations

- OCR.space API key is currently hardcoded and may have rate limits
- Medical reports are optional but scripts assume they exist - error handling added
- All processing is synchronous - may be slow for large PDFs
- Session storage is in-memory - cleared on server restart

## Future Enhancements

- Async processing with background tasks
- WebSocket support for real-time progress updates  
- PDF preview capabilities
- Advanced text editing with rich text editor
- Export capabilities (PDF, Word)
- Multi-user support with proper authentication