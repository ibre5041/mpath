from antlr3 import *;
from antlr3.tree import *;
import MultipathLexer
import MultipathParser
import sys

import unittest

class MultipathDevice:
    def __init__(self, elem):
        #
        self.additional = ''
        for e in elem.children:
            if e.toString() == '{':
                continue
            elif e.toString() == 'wwid':
                self.wwid = e.children[0].text
            elif e.toString() == 'alias':
                self.alias = e.children[0].text
            elif e.toString() == '}':
                continue
            else:
                self.additional += "\n"                
                self.additional += e.toString()
                self.additional += " " + e.children[0].text if e.children else None
    def getWWID(self):
    # generate WWID in Linux multipath.conf format        
        return self.wwid
        
    def getComment(self):
        return ''

    def __str__(self):
        return """multipath {
wwid %s
alias %s%s
}
""" % (self.wwid, self.alias, self.additional if self.additional else '')

    def __lt__(self, other):
        if self.alias.startswith('local') and other.alias.startswith('asm'):
            return True
        if other.alias.startswith('local') and self.alias.startswith('asm'):
            return False
        return self.getWWID() < other.getWWID()
        #return self.alias < other.alias

def parseMultipathConf(filename):
    lines = [line.rstrip('\n') for line in open(filename)]
    #
    input = ANTLRFileStream(filename)
    lexer = MultipathLexer.MultipathLexer(input);
    tokens = CommonTokenStream(lexer);
    parser = MultipathParser.MultipathParser(tokens);
    r = parser.multipath();
    t = r.tree; # get tree from parser
    #
    multipaths = [ a for a in t.children if a.token.text == 'multipaths' ] # filter tree children, find those named 'multipaths' (assuming there is only one)
    #
    startToken = tokens.get(multipaths[0].startIndex)
    stopToken  = tokens.get(multipaths[0].stopIndex)
    #
    for line in lines[0: startToken.line -1 ] : # antlr3 indexes lines from 1
        print line

    print 'multipaths {'
    M = []
    for multipath in multipaths[0].children:
        if multipath.toString() != 'multipath': # leading '{' and trailing '}' are also children of multipaths element 
            continue
        M.append(MultipathDevice(multipath))
    M.sort()
    for multipath in M:
        print(multipath)
    print '}'
                    
    for line in lines[stopToken.line:] :
        print line
        
    return M
    
if __name__ == "__main__" and len(sys.argv) >= 2:
    print parseMultipathConf(str(sys.argv[1]))
