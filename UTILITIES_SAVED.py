from Zones import RRecord
import socket
import dns.resolver
import socket
import urllib.request


with open('domainlist.txt') as f:
    my_list = [line.strip() for line in f.readlines()]

resolver = dns.resolver.Resolver()
resolver.nameservers = [socket.gethostbyname('dns.example.com')]

for domain in my_list:
    try:
        q = resolver.query(domain, 'CNAME')
        for rdata in q:
            print(f'{domain}: {rdata.target}')
    except dns.resolver.NoAnswer:
        print(f'{domain}: No answer')


def get_local_ip():
    return socket.gethostbyname(socket.gethostname())


def get_public_ip_from_ident_me():
    return urllib.request.urlopen('https://ident.me').read().decode('utf8')


def load(self, csv):
    fhand = open(csv, "r", encoding="utf8")
    for line in fhand:
        splitted = line.split("\t")     # \t is TAB
        if len(splitted) >= 3:
            if splitted[2].strip() == "NoAnswer" or splitted[2].strip() == "NXDomain":
                self.cache.append(RRecord(splitted[0], splitted[1], splitted[2].strip()))
                continue
            listRespose = list()
            for a in splitted[2:]:
                listRespose.append(a.strip())
            rrecord = RRecord(splitted[0], splitted[1], listRespose)
            self.cache.append(rrecord)
        else:
            print("Line: ", line, " has too few arguments")
    fhand.close()
