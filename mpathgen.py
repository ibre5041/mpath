from xml.dom import minidom
from antlr3 import *;
from antlr3.tree import *;
import MultipathLexer
import MultipathParser
import sys
import re
import unittest
import math

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
        
    def getAlias(self):
        return self.alias

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

class XmlDevice:
    def __init__(self, elem):
        #
        self.path = elem.getElementsByTagName('name')[0].getAttribute('path').strip()
        #
        self.fcLunId = elem.getElementsByTagName('fc_lun_id')[0].firstChild.nodeValue
        #
        # 50060e8007293a35 ( 5 - NNA format 5, 0060e8 - 24 bit vendor OUI, 007293a35 - 36 bit vendor sequence or serial number      
        array_port_wwn = elem.getElementsByTagName('array_storage')[0].getElementsByTagName('array_port_wwn')[0].firstChild.nodeValue
        self.serialNrHex = array_port_wwn[-9:]
        # replace last byte with zero
        self.serialNrHex = self.serialNrHex[:-2] + '00'
        #
        self.serialNrDec = elem.port  = elem.getElementsByTagName('array_storage')[0].getElementsByTagName('serial_nr')[0].firstChild.nodeValue
        # 
        self.vendorOui = array_port_wwn[1:7]
        #
        self.alpa  = elem.port  = elem.getElementsByTagName('array_storage')[0].getElementsByTagName('alpa')[0].firstChild.nodeValue
        #
        self.lunId = elem.getElementsByTagName('lun_id')[0].firstChild.nodeValue # LUN id decimal format
        self.lunId = int(self.lunId)
        #
        self.port  = elem.getElementsByTagName('array_storage')[0].getElementsByTagName('array_port_name')[0].firstChild.nodeValue
        #
        self.cu    = elem.getElementsByTagName('array_storage')[0].getElementsByTagName('ldev')[0].getElementsByTagName('cu')[0].firstChild.nodeValue # decimal format
        self.cu    = elem.getElementsByTagName('array_storage')[0].getElementsByTagName('ldev')[0].getElementsByTagName('cu')[0].firstChild.nodeValue # decimal format
        #
        self.size  = elem.getElementsByTagName('array_storage')[0].getElementsByTagName('ldev')[0].getElementsByTagName('size')[0].firstChild.nodeValue
        self.size  = int(self.size)    

    def getWWID(self):
    # generate WWID in Linux multipath.conf format        
        return '3' + '6' + self.vendorOui + self.serialNrHex + self.fcLunId;
        
    def getComment(self):
        return "# Path: {} \t FcLunId: {}\t OUI: {}\t LUN: {:02d}\t Port: {}\t SN: {}/{}\t Size: {: 8d}\t {}"\
            .format(self.path, self.fcLunId ,self.vendorOui, self.lunId, self.port, self.serialNrHex, self.serialNrDec, self.size, self.getWWID())
                               
    def __str__(self):
        return self.getComment()           

    def __lt__(self, other):
        if self.serialNrHex < other.serialNrHex:
            return True
        if self.lunId < other.lunId:
            return True
        if self.lunId == other.lunId:
            return self.getWWID() < other.getWWID()
        return False
    
def parseXPinfo(filename):
    xmldoc = minidom.parse(filename)
    itemlist = xmldoc.getElementsByTagName('device_file')
    #print('Total devices: '+len(itemlist))
    L = []
    for s in itemlist:
        xmlDevice = XmlDevice(s)
        L.append(xmlDevice)        
    L.sort()   
    for device in L:   
        print(device)
    return L

def nextAliasNumber(AliasList, n):
    Aliases = filter(lambda a: not re.match("^local", a) , AliasList)
    LastAlias = max(Aliases)
    aliasRe = re.compile(r'^([a-zA-Z]+)([0-9]+)')
    reSult =aliasRe.search(LastAlias);
    aliasPrefix, aliasSuffix = reSult.groups();
    # aliasNumner = 32, resp. 91, resp 450
    aliasNumber = int(aliasSuffix)
    # scale = 1, resp 1, resp 2
    scale = int(math.floor(math.log10(aliasNumber)))
    # scalePow = 10, resp 10, resp 100
    scalePow = int(math.pow(10, scale))
    # leadingDigit 3, resp 9, resp 4
    leadingDigit = int(math.floor(aliasNumber / scalePow))
    if leadingDigit == 9:
        leadingDigit = 1
        scale += 1
        scalePow = int(math.pow(10, scale))
        leadingDigit = 1
    else:
        leadingDigit += 1

    R = []
    zfilllen = max([scale+2, len(aliasSuffix)])    
    for i in range(1,n):
        alias = aliasPrefix + str(scalePow * leadingDigit + i).zfill(zfilllen)
        R.append(alias)        
    return R
    
if __name__ == "__main__" and len(sys.argv) >= 3:
    MPathList = parseMultipathConf(str(sys.argv[1]))
    XPinfList = parseXPinfo(str(sys.argv[2]))
    # Get WWIDs from /etc/multipath.conf
    MPathWWIDs = set(map(lambda m: m.getWWID(), MPathList))
    # Get WWIDs from xpinfo output but not in /etc/multipath.conf
    XPinfWWIDs = set(map(lambda m: m.getWWID(), XPinfList))
    #    
    MissingWWIDs = set(filter(lambda m: m not in MPathWWIDs, XPinfWWIDs))
    #
    print "mpath: " + str(len(MPathWWIDs))
    for W in MPathWWIDs:
        print W

    print "xpinfo: "  + str(len(XPinfWWIDs))
    for W in XPinfWWIDs:
        print W 

    print "missing: " + str(len(MissingWWIDs))
    for W in MissingWWIDs:
        print W
    
    
    NewAliases = nextAliasNumber(map(lambda m: m.getAlias(), MPathList), len(MissingWWIDs))
    print NewAliases
    
    

    
