.PHONY: help install run test demo clean setup

help: ## Show this help message
	@echo "Agentic Community Assistant - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Initial setup - create venv and install dependencies
	@echo "Setting up development environment..."
	python3 -m venv .venv
	@echo "Virtual environment created. Activate it with: source .venv/bin/activate"
	@echo "Then run: make install"

install: ## Install Python dependencies
	@echo "Installing dependencies..."
	python3 -m pip install --upgrade pip
	pip install -r requirements.txt
	@echo "Installing Playwright browsers..."
	python3 -m playwright install
	@echo "Installation complete!"

run: ## Start the FastAPI server
	@echo "Starting FastAPI server..."
	python3 -m uvicorn app.main:app --reload

test: ## Run the demo script (requires server to be running)
	@echo "Running demo script..."
	python3 demo.py

demo: ## Run the complete demo workflow
	@echo "Starting demo workflow..."
	@echo "1. Starting server in background..."
	@python3 -m uvicorn app.main:app --reload &
	@echo "2. Waiting for server to start..."
	@sleep 3
	@echo "3. Running demo script..."
	@python3 demo.py
	@echo "4. Stopping server..."
	@pkill -f "uvicorn app.main:app"

clean: ## Clean up generated artifacts and cache
	@echo "Cleaning up..."
	rm -rf _artifacts/
	rm -rf __pycache__/
	rm -rf app/__pycache__/
	rm -rf app/*/__pycache__/
	@echo "Cleanup complete!"

cleanup-data: ## Clean up expired artifacts via API
	@echo "Cleaning up expired artifacts..."
	curl -X POST http://localhost:8000/cleanup

health: ## Check service health
	@echo "Checking service health..."
	curl http://localhost:8000/health

artifacts: ## List all artifacts
	@echo "Listing artifacts..."
	curl http://localhost:8000/artifacts

audit: ## View audit trail
	@echo "Viewing audit trail..."
	curl http://localhost:8000/audit

docs: ## Open API documentation in browser
	@echo "Opening API documentation..."
	open http://localhost:8000/docs

format: ## Format code with black
	@echo "Formatting code..."
	black app/ demo.py

lint: ## Lint code with flake8
	@echo "Linting code..."
	flake8 app/ demo.py

check: format lint ## Format and lint code

full-setup: setup install ## Complete setup including dependencies
	@echo "Full setup complete!"
	@echo "Next steps:"
	@echo "1. Activate virtual environment: source .venv/bin/activate"
	@echo "2. Start server: make run"
	@echo "3. Run demo: make demo"
	@echo "4. View docs: make docs"
