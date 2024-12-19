.PHONY: all lint test install dev clean distclean

all: ;

lint:
	q2lint
	flake8

test: all
	py.test

install: all
	python -m pip install -v .

dev: all
	pip install -e .

clean: distclean

distclean: ;
