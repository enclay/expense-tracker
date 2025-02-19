VENV_DIR ?= .venv
ACTIVATE := source $(VENV_DIR)/bin/activate &&

install:
	python3 -m venv $(VENV_DIR)
	@echo "Virtual environment created at $(VENV_DIR)."
	@$(ACTIVATE) pip install --upgrade pip && pip install -r requirements.txt
	@echo "All packages have been installed."

run:
	@$(ACTIVATE) python -m bot

clean:
	rm -rf $(VENV_DIR)
	@echo "Virtual environment removed."
