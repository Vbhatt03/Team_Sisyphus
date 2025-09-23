# CaseFlow - Development Scripts

# Backend development server
.PHONY: dev-backend
dev-backend:
	cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend development server  
.PHONY: dev-frontend
dev-frontend:
	cd frontend && npm run dev

# Install backend dependencies
.PHONY: install-backend
install-backend:
	cd backend && pip install -r requirements.txt

# Install frontend dependencies
.PHONY: install-frontend
install-frontend:
	cd frontend && npm install

# Install all dependencies
.PHONY: install
install: install-backend install-frontend

# Seed database with demo data
.PHONY: seed
seed:
	cd backend && python seed.py

# Clean generated files and caches
.PHONY: clean
clean:
	rm -rf backend/__pycache__
	rm -rf backend/**/__pycache__
	rm -rf backend/caseflow.db
	rm -rf data/
	rm -rf frontend/dist
	rm -rf frontend/node_modules/.cache

# Run backend tests (if any)
.PHONY: test-backend
test-backend:
	cd backend && python -m pytest

# Run frontend tests
.PHONY: test-frontend  
test-frontend:
	cd frontend && npm test

# Build frontend for production
.PHONY: build-frontend
build-frontend:
	cd frontend && npm run build

# Start both servers simultaneously (requires concurrently package)
.PHONY: dev
dev:
	npm install -g concurrently
	concurrently "make dev-backend" "make dev-frontend"

# Setup everything from scratch
.PHONY: setup
setup: install seed
	@echo "✅ CaseFlow setup complete!"
	@echo "Run 'make dev' to start both servers"
	@echo "Login with username='demo', password='demo123'"

# Help target
.PHONY: help
help:
	@echo "CaseFlow Development Commands:"
	@echo ""
	@echo "  setup          - Install all dependencies and seed database"
	@echo "  dev            - Start both backend and frontend servers"
	@echo "  dev-backend    - Start only the FastAPI backend server"
	@echo "  dev-frontend   - Start only the React frontend server"
	@echo "  install        - Install all dependencies"
	@echo "  seed           - Seed database with demo data"
	@echo "  clean          - Clean generated files and caches"
	@echo "  build-frontend - Build frontend for production"
	@echo ""
	@echo "Default demo login: username='demo', password='demo123'"