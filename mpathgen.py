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
    def __init__(self, comment, alias, wwid, additional = ''):
        self.comment = comment
        self.alias = alias
        self.wwid = wwid
        self.additional = additional
        
    @classmethod
    def fromASTToken(cls, elem):
        #
        additional = ''
        for e in elem.children:
            if e.toString() == '{':
                continue
            elif e.toString() == 'wwid':
                wwid = e.children[0].text
            elif e.toString() == 'alias':
                alias = e.children[0].text
            elif e.toString() == '}':
                continue
            else:
                additional += "\n"                
                additional += e.toString()
                additional += " " + e.children[0].text if e.children else None
        return cls('', alias, wwid, additional)

    def getWWID(self):
    # generate WWID in Linux multipath.conf format        
        return self.wwid
        
    def getAlias(self):
        return self.alias

    def getComment(self):
        return self.comment

    def __str__(self):
        return """multipath {
%s
wwid %s
alias %s%s
}
""" % (self.comment, self.wwid, self.alias, self.additional if self.additional else '')

    def __lt__(self, other):
        # local disks before shared ones
        if self.alias.startswith('local') and other.alias.startswith('asm'):
            return True
        if other.alias.startswith('local') and self.alias.startswith('asm'):
            return False
        return self.getAlias() < other.getAlias()
        #return self.alias < other.alias

class MultipathConf:
    def __init__(self, filename):
        self.lines = [line.rstrip('\n') for line in open(filename)]
        #
        inputStream = ANTLRFileStream(filename)
        lexer = MultipathLexer.MultipathLexer(inputStream);
        tokens = CommonTokenStream(lexer);
        parser = MultipathParser.MultipathParser(tokens);
        r = parser.multipath();
        self.tree = r.tree; # get tree from parser
        #
        self.mpathsSection = [ a for a in self.tree.children if a.token.text == 'multipaths' ] # filter tree children, find those named 'multipaths' (assuming there is only one)
        #
        self.mpathsSectionStart = tokens.get(self.mpathsSection[0].startIndex)
        self.mpathsSectionStop  = tokens.get(self.mpathsSection[0].stopIndex)
        #
        self.mpaths = []
        self.mpathsHashByWWID = {}
        self.mpathsHashByAlias = {}
        for mpath in self.mpathsSection[0].children:
            if mpath.toString() != 'multipath': # leading '{' and trailing '}' are also children of multipaths element 
                continue
            device = MultipathDevice.fromASTToken(mpath)
            self.mpaths.append(device)
            self.mpathsHashByWWID[device.getWWID()] = device
            self.mpathsHashByAlias[device.getAlias()] = device
        self.mpaths.sort()
        
    def multipaths(self):
        return self.mpaths
        
    def getMultipathByWWID(self, wwid):
        return self.mpathsHashByWWID[wwid]
        
    def getMultipathByAlias(self, alias): 
        return self.mpathsHashByAlias[alias]
        
    def getWWIDs(self):
        return set(map(lambda m: m.getWWID(), self.mpaths))
    
    def addMultipath(self, multipath):
        self.mpaths.append(multipath)
        self.mpathsHashByWWID[multipath.getWWID()] = multipath
        self.mpathsHashByAlias[multipath.getAlias()] = multipath
    
    def serialize(self):
        # Copy heading sections line by line, until multipaths section start
        for line in self.lines[0: self.mpathsSectionStart.line -1 ] : # antlr3 indexes lines from 1
            print line
        # Serialize current lultipaths list
        # self.mpaths.sort()
        print 'multipaths {'
        for multipath in self.mpaths:
            print(multipath)
        print '}'
        # Copy trailing line one by one - if any
        for line in self.lines[self.mpathsSectionStop.line:] :
            print line        

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
        #
        self.comment = "# Path: {0} \t FcLunId: {1}\t OUI: {2}\t LUN: {3:02d}\t Port: {4}\t SN: {5}/{6}\t Size: {7: 8d}"\
            .format(self.path, self.fcLunId ,self.vendorOui, self.lunId, self.port, self.serialNrHex, self.serialNrDec, self.size)

    def getWWID(self):
    # generate WWID in Linux multipath.conf format        
        return '3' + '6' + self.vendorOui + self.serialNrHex + self.fcLunId;
        
    def getComment(self):
        return self.comment
                               
    def __str__(self):
        return self.getComment()           

    def __lt__(self, other):
        # 1st compare serial numbers
        if self.serialNrHex != other.serialNrHex:
            return self.serialNrHex < other.serialNrHex
        # 2nd compare LUN IDs 
        if self.lunId != other.lunId:
            return self.lunId < other.lunId
        # 3rd should be reaches        
        if self.getWWID() != other.getWWID():
            return self.getWWID() < other.getWWID()
        # 4th sort lexically by comment (path)
        return self.getComment() < other.getComment()

class XPinfo:
    def __init__(self, filename):
        xmldoc = minidom.parse(filename)
        self.itemlist = xmldoc.getElementsByTagName('device_file')
        # This list contains duplicates, one per path
        self.L = []
        for s in self.itemlist: 
            self.L.append(XmlDevice(s))
        self.L.sort()
        # Put all wwids into hash map, if wwid is already present just concat comments
        self.M = {}
        for device in self.L:
            if device.getWWID() in self.M:
                d = self.M[device.getWWID()]
                d.comment += "\n" + device.comment
            else:        
                self.M[device.getWWID()] = device
        # Final sorted list
        self.N = []
        for wwid in list(self.M.keys()):
            self.N.append(self.M[wwid])
        self.N.sort()

    def devices(self):
        return self.N

    def getDeviceByWWID(self, wwid):
        return self.M[wwid]

    def getWWIDs(self):
        return map(lambda m: m.getWWID(), self.N)

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
    for i in range(0,n):
        # alias = 40, resp 100, resp 500
        alias = aliasPrefix + str(scalePow * leadingDigit + i).zfill(zfilllen)
        R.append(alias)        
    return R
    
if __name__ == "__main__" and len(sys.argv) >= 3:
    multipathConf = MultipathConf(str(sys.argv[1]))
    xpinfo = XPinfo(str(sys.argv[2]))
    # Get WWIDs from /etc/multipath.conf
    MPathWWIDs = multipathConf.getWWIDs()
    # Get WWIDs from xpinfo output but not in /etc/multipath.conf
    XPinfoWWIDs = xpinfo.getWWIDs() 
    # 
    MissingWWIDs = set(filter(lambda m: m not in MPathWWIDs, XPinfoWWIDs))
    #
    print >> sys.stderr, "mpath: " + str(len(MPathWWIDs))
    for W in MPathWWIDs:
        print >> sys.stderr, W

    print >> sys.stderr, "xpinfo: "  + str(len(XPinfoWWIDs))
    for W in XPinfoWWIDs:
        print >> sys.stderr, W 

    print >> sys.stderr, "missing: " + str(len(MissingWWIDs))
    # generate alias for each missing wwid
    newAliases = nextAliasNumber(map(lambda m: m.getAlias(), multipathConf.multipaths()), len(MissingWWIDs))
    # iterate over all xpinfo wwids
    for W in XPinfoWWIDs:
        # if it is present just modify its comment
        if W in MPathWWIDs:
            multipath = multipathConf.getMultipathByWWID(W)
            xmldevive = xpinfo.getDeviceByWWID(W)
            multipath.comment = xmldevive.getComment()
        # else add a new alias
        else:
            alias = newAliases.pop(0)
            comment = xpinfo.getDeviceByWWID(W).getComment()        
            print >> sys.stderr, "Adding: {0} \t {1}".format(alias, W)
            multipathConf.addMultipath(MultipathDevice(comment, alias, W))
    # serialiaze a new config file 
    multipathConf.serialize()
