all: tests install

install:
	python setup.py install
tests:
	nosetests -v
