PYTHON ?= python3

.PHONY: run test demo

run:
	$(PYTHON) src/main.py

test:
	$(PYTHON) -m unittest discover -s tests -t . -v

demo:
	bash scripts/os/all.sh
