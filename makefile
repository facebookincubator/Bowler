venv:
	python -m venv .venv
	@echo 'run `source .venv/bin/activate` to use virtualenv'

setup:
	python -m pip install -Ur requirements.txt
	python -m pip install -Ur requirements-dev.txt

dev: venv
	source .venv/bin/activate && make setup
	source .venv/bin/activate && python setup.py develop
	@echo 'run `source .venv/bin/activate` to develop bowler'

release: lint test clean
	python setup.py sdist bdist_wheel
	python -m twine upload dist/*

format:
	isort --recursive -y bowler setup.py
	black bowler setup.py

lint:
	@/bin/bash -c 'die() { echo "$$1"; exit 1; }; \
	  while read filename; do \
	  grep -q "Copyright (c) Facebook" "$$filename" || \
	    die "Missing copyright in $$filename"; \
	  grep -q "#!/usr/bin/env python3" "$$filename" || \
	    die "Missing #! in $$filename"; \
	  done < <( git ls-tree -r --name-only HEAD | grep ".py$$" )'
	black --check bowler setup.py
	mypy -m bowler

test:
	python -m coverage run -m bowler.tests
	python -m coverage report

clean:
	rm -rf build dist README MANIFEST *.egg-info

distclean: clean
	rm -rf .venv
