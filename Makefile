init:
	pip install -r requirements.txt

test:
	nosetests -v --nologcapture tests 

testdebug:
	nosetests -v --pdb --nologcapture tests 
