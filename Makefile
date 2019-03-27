init:
	pip install -r requirements.txt

test:
	nosetests --exe tests
