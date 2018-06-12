venv:
	python3 -m venv .venv
	@echo 'run `source .venv/bin/activate` to use virtualenv'

setup: venv
	source .venv/bin/activate && pip3 install -U black isort mypy pylint twine

dev: setup
	source .venv/bin/activate && python3 setup.py develop
	@echo 'run `source .venv/bin/activate` to develop bowler'

release: lint test clean
	python3 setup.py sdist
	python3 -m twine upload dist/*

format:
	black bowler setup.py
	isort

lint:
	black --check bowler setup.py
	mypy --ignore-missing-imports --python-version 3.6 .

test:
	python3 -m unittest -v bowler.tests

clean:
	rm -rf build dist README MANIFEST *.egg-info

distclean: clean
	rm -rf .venv
