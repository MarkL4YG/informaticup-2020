all: run

setup:
	pip install --user -r ./docker/python/requirements.txt

run:
	./docker/python/main.py