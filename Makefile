all: build test

build: Multipath.g
	java -jar antlr-3.1.3.jar Multipath.g

test:
	python Test.py multipath.conf.1

clean:
	rm -f Multipath.tokens MultipathParser.py MultipathLexer.py MultipathLexer.pyc MultipathParser.pyc


