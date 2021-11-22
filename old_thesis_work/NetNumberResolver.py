# coding=utf-8
import re
import math


class NetNumberResolver:
    """
    This class aim is to find network number and autonomous system information about an IPv4. It stores the information in the field of an object of this class.
    This class has four fields:
    -Ipv4Range: a string representing a network number, which is the range of IP addresses managed by the autonomous system in ASName field (example of IPrange: "170.84.140.0/24")
    -ASName: a string which is the name of the autonomous system which manage the range of IP addresses in Ipv4Range.
    -code: a string representing the code of the autonomous system which manage the range of IP addresses in Ipv4Range. It has the form of "AS" followed by a number (example: "AS1234").
    -geocode: is a string which represents the country code of the country where the autonomous system is located.
    """

    Ipv4Range = None
    code = ""
    ASName = ""
    geocode = ""

    def __init__(self, IPrange, name, code, geocode):
        """
        This class constructor sets the fields of this class object. This constructor is called by resolveIPRange method to return a list of objects of this same class with the information about network number and autonomous system saved in the fields of the objects.
        :param IPrange: a string representing a network number, which is the range of IP addresses managed by the autonomous system in name attribute (example of IPrange: "170.84.140.0/24")
        :param name: a string which is the name of the autonomous system which manage the range of IP addresses in IPrange.
        :param code: a string representing the code of the autonomous system which manage the range of IP addresses in IPrange. It has the form of "AS" followed by a number (example: "AS1234").
        :param geocode: is a string which represents the country code of the country where the autonomous system is located.
        """
        self.Ipv4Range = IPrange
        self.code = code
        self.ASName = name
        self.geocode = geocode

    @staticmethod
    def resolve(Ip, netNumberDatabase='C:/Users/leona/Desktop/TesiMagistrale/IPv4ToASN/ip2asn-v4.tsv'):
        """
        This is a static method which, given an IPv4 in the form of a string, looks for network information about the IP on a database file opened with OpenDataBase class. It looks for: range of IP addresses the Ip belongs to, the autonomous system which manages that range of IP addresses, its autonomous system code and its location in the world as a country code.
        :param Ip: a string representing an IPv4 (example: "123.45.67.89").
        :return: If Ip is not in the form of an IPv4 address this method print on screen a message error and return None. Otherwise, this method returns a list of objects of this same class, the Ip is an IPv4 address which is found to be in the range of IP addresses of each of the elements in the list.
        """
        #check che ip sia scritto bene = solo numeri <255 e non più di 3 punti
        match = re.search("[^0-9.]", Ip)
        if match is not None:
            print("This Ip is not valid: ", Ip)
            return None
        subIPsupport = Ip.split(".")
        subIP = list()
        for i in subIPsupport:
            subIP.append(int(i))
        #print("printo", subIP, type(subIP[0]))
        if len(subIP) != 4:
            print("Ip has a value not valid, too much dots: ", Ip)
            return
        if subIP[0] > 255 or subIP[1] > 255 or subIP[2] > 255 or subIP[3] > 255:
            print("Ip has a value not valid, more than 255: ", Ip)
            return
        db = OpenDataBase(netNumberDatabase)
        fhand = db.fileHandler
        if fhand is None:
            print("NetworkNumber Database not found")
            return
        #da qui faccio un tentativo di ricerca binaria prima di trovare
        data = list()
        lines = fhand.readlines()
        start = 0
        end = len(lines) -1
        print("Looking for network number of address: ", Ip)
        while True:
            half = int((start + end)/2)
            divideLine = lines[half]
            subline = divideLine.split("\t")
            subIPsupport = subline[0].split(".")
            subIPfrom = list()
            subIPto = list()
            for a in subIPsupport:
                subIPfrom.append(int(a))
            subIPsupport = subline[1].split(".")
            for b in subIPsupport:
                subIPto.append(int(b))
            where = NetNumberResolver.isInRange(subIP, subIPfrom, subIPto)
            if where == -1:
                if half == 0:
                    print("Error Ip not found")
                    break
                end = half - 1
            elif where == 1:
                if half == len(lines) -1:
                    print("Error Ip too big, overflow the database")
                    break
                start = half + 1
            else:
                print("Found network for ", Ip,  ": range ", subline[0], " to ", subline[1], ", AS:  ", subline[4].strip())
                data.append(divideLine)
                break

        start = half
        while start != 0:
            half = half -1
            divideLine = lines[half]
            subline = divideLine.split("\t")
            subIPsupport = subline[0].split(".")
            subIPfrom = list()
            subIPto = list()
            for a in subIPsupport:
                subIPfrom.append(int(a))
            subIPsupport = subline[1].split(".")
            for b in subIPsupport:
                subIPto.append(int(b))
            where = NetNumberResolver.isInRange(subIP, subIPfrom, subIPto)
            if where == 0:
                print("Found network for ", Ip,  ": range ", subline[0], " to ", subline[1], ", AS:  ", subline[4].strip())
                data.append(divideLine)
            else:
                break

        half = start
        while start != len(lines) - 1:
            half = half + 1
            divideLine = lines[half]
            subline = divideLine.split("\t")
            subIPsupport = subline[0].split(".")
            subIPfrom = list()
            subIPto = list()
            for a in subIPsupport:
                subIPfrom.append(int(a))
            subIPsupport = subline[1].split(".")
            for b in subIPsupport:
                subIPto.append(int(b))
            where = NetNumberResolver.isInRange(subIP, subIPfrom, subIPto)
            if where == 0:
                print("Found network for ", Ip,  ": range ", subline[0], " to ", subline[1], ", AS:  ", subline[4].strip())
                data.append(divideLine)
            else:
                break

#fino a qui questo il blocco da eliminare se cambi idea
        #da qui cancella ciò che non serve più

        #fin qui cancella ciò che non serve più
        result = list()
        for each in data:
            subline = each.split("\t")
            #togli le virgole sennò poi in csv viene un casino
            netNumb = NetNumberResolver.toRangeNotation(subline[0].strip(), subline[1].strip())
            result.append(NetNumberResolver(netNumb, subline[4].strip(), subline[2].strip(), subline[3].strip()))
#ora devo fare in modo che torni una lista, al massimo di un solo elemento ma come dice il professore può essere di più elementi nel farlo do per scontato che però siano in ordine crescente di indirizzi nel database
        if len(result) == 0:
            return None
        else:
            return result

    @staticmethod
    def isInRange(target, fromIP, toIP):
        """
        This method is a staticmethod used to check if an Ipv4 is inside a range given in input. This method is used several times from the resolve method.
        :param target: a list of four numbers which are the numbers in which an IPv4 can be splitted from dots. The four number has the same order as they appear in the IPv4. This is the IP to check if is inside the given range (Example: 123.45.67.89 => target = [123, 45, 67, 89]).
        :param fromIP: a list of four numbers which are the numbers in which an IPv4 can be splitted from dots. The four number has the same order as they appear in the IPv4. This is the lower IP of a range of IPv4 managed by an autonomous system.
        :param toIP: a list of four numbers which are the numbers in which an IPv4 can be splitted from dots. The four number has the same order as they appear in the IPv4. This is the upper IP of a range of IPv4 managed by an autonomous system.
        :return: this method return an integer. The integer can be -1, 0 or 1. If the method returns -1 it means that target IP is lower than the lower IP of the range. If the method returns 1 it means that target IP is greater than the upper IP of the range. If the method returns 0 it means that target IP lies in the range of IP between fromIP and toIP.
        """
        if target[0] > fromIP[0]:
            pass
        elif target[0] == fromIP[0]:
            if target[1] > fromIP[1]:
                pass
            elif target[1] == fromIP[1]:
                if target[2] > fromIP[2]:
                    pass
                elif target[2] == fromIP[2]:
                    if target[3] >= fromIP[3]:
                        pass
                    else:
                        return -1
                else:
                    return -1
            else:
                return -1
        else:
            return -1

        if target[0] < toIP[0]:
            return 0
        elif target[0] == toIP[0]:
            if target[1] < toIP[1]:
                return 0
            elif target[1] == toIP[1]:
                if target[2] < toIP[2]:
                    return 0
                elif target[2] == toIP[2]:
                    if target[3] <= toIP[3]:
                        return 0
                    else:
                        return 1
                else:
                    return 1
            else:
                return 1
        else:
            return 1

    @staticmethod
    def toRangeNotation(IpStringFrom, IpStringTo):
        """
        This static method can be useful in different occasions. It is useful to return a range of IP addresses in the network number notation
        :param IpStringFrom: a string representing the first IP address of the range which have to be converted in the network number notation
        :param IpStringTo: a string representing the last IP address of the range which have to be converted in the network number notation
        :return: a string representing the range of IP addresses in the network number notation
        """
        splittedFrom = IpStringFrom.split(".")
        splittedTo = IpStringTo.split(".")
        integerSliceFrom = list()
        for each in splittedFrom:
            integerSliceFrom.append(int(each))
            if int(each) > 255:
                print("ERROR: ", IpStringFrom, " is not a valid IP address")
        binarySliceFrom = list()
        for i in integerSliceFrom:
            binarySliceFrom.append(bin(i)[2:].zfill(8))

        integerSliceTo = list()
        for each in splittedTo:
            integerSliceTo.append(int(each))
            if int(each) > 255:
                print("ERROR: ", IpStringTo, " is not a valid IP address")
        binarySliceTo = list()
        for i in integerSliceTo:
            binarySliceTo.append(bin(i)[2:].zfill(8))

        span = 32
        found= False
        for num in reversed(range(4)):
            byteTo = binarySliceTo[num]
            byteFrom = binarySliceFrom[num]
            for c in reversed(range(8)):
                if int(byteTo[c]) == int(byteFrom[c]):
                    found = True
                    break
                else:
                    span = span-1
            if found:
                break

        returnValue = IpStringFrom+"/"+ str(span)
        return returnValue




class OpenDataBase:
    """
    This class open a database of network numbers and autonomous system information.
    This class has one field:
    - fileHandler: is a file handler for the file with network number and autonomous system information. If the file doesn't exists fileHandler is None.
    """
    fileHandler = None

    def __init__(self, tsv):
        """
        This constructor opens a file which is a database of network numbers and autonomous systems information. The file has to be a .tsv file (tab-separated value). If the file is not found an error is printed on screen and the fileHandler field is set as None. A good public database file with network numbers and autonomous systems information could be find at this URL: https://iptoasn.com/
        :param tsv: a string which is the name of a .tsv file with network numbers information
        """
        try:
            fhand = open(tsv, "r", encoding='utf-8')
            self.fileHandler = fhand
        except FileNotFoundError:
            print("Error file not found: ", tsv)
            self.fileHandler = None




#a = NetNumberResolver.resolve("112.44.67.12")
#b = NetNumberResolver.toRangeNotation("130.186.0.0", "130.186.31.255")
