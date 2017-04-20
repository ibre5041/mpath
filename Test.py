from antlr3 import *;
from antlr3.tree import *;
import MultipathLexer
import MultipathParser
import sys

import unittest

def evaluate(value):
    input = ANTLRFileStream(value)
    lexer = MultipathLexer.MultipathLexer(input);
    tokens = CommonTokenStream(lexer);
    parser = MultipathParser.MultipathParser(tokens);
    r = parser.multipath();
    t = r.tree; # // get tree from parser
    nodes = CommonTreeNodeStream(t);
    #walker = Eval.Eval(nodes);  # // create a tree parser
    #return walker.prog()
    return r.tree.toStringTree();

if __name__ == "__main__" and len(sys.argv) >= 2:
    print evaluate(str(sys.argv[1]))
