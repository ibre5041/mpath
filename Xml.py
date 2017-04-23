from xml.dom import minidom
import sys

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
        if self.lunId < other.lunId:
            return True
        if self.lunId == other.lunId:
            return self.getWWID() < other.getWWID()
        return False
        
if __name__ == "__main__" and len(sys.argv) >= 2:
    xmldoc = minidom.parse(str(sys.argv[1]))
    itemlist = xmldoc.getElementsByTagName('device_file')
    #print('Total devices: '+len(itemlist))
    L = []
    for s in itemlist:
        xmlDevice = XmlDevice(s)
        L.append(xmlDevice)        
    L.sort()   
    for device in L:   
        print(device)

    