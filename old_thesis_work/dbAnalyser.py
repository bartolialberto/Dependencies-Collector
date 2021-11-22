import sqlite3
import csv


class dbAnalyser:
    """
    dbAnalyzer is a class which has some useful methods to export csv data from the database
    Fields:
    dataBase: a string which is the name of the database file the methods of this class refers to export data in a csv file
    """
    dataBase = None

    def __init__(self, dbName):
        """
        Constructor which initialize the dataBase filed.
        :param dbName: name of a data base file.
        """
        self.dataBase = dbName



    def nameResolutionPathRedundancy(self, domain):
        """
        This method takes a domain as argument and execute a query in the database to find the synctactic zones and it finds the redundancy of the nameservers of these zones, the IP ranges of the nameservers and AS_code which manage these ranges.
        These dependencies has to be previously stored on the database using the class DomainDependence.py
        :param domain: a string representing a web domain
        :return: This method has no return value, instead it create a .csv file called resolutionPathRedundancy.csv
        """


        if not isinstance(domain, str):
            print("Domain is not a string: ", domain)
            exit(1)

        if not domain.endswith("."):
            domain = domain+"."

        cur = None
        try:
            conn = sqlite3.connect(self.dataBase)
            cur = conn.cursor()

            cur.execute(
                'SELECT host  FROM host2directZone WHERE host = \'' + domain + '\'')
            row = cur.fetchone()

            if row is None:
                print('Error: ', domain,
                      ' is not the name of a host or is not present in host2directZone table')
                exit(1)


            cur.execute('select distinct zone2synctacticDependence.synctactic_zone, zone2nameserver.nameserver, host2Ip.IPv4, IP2Range.range, range2AS.AS_code\
                    from (((((host2directZone\
                    INNER JOIN zone2synctacticDependence on zone2synctacticDependence.zone = host2directZone.direct_zone)\
                    INNER JOIN zone2nameserver on zone2nameserver.zone = zone2synctacticDependence.synctactic_zone)\
                    INNER JOIN host2Ip on host2Ip.host = zone2nameserver.nameserver)\
                    INNER JOIN IP2Range on IP2Range.ip_address = host2Ip.IPv4)\
                    INNER JOIN range2AS on range2AS.IP_range = IP2Range.range)\
                    where host2directZone.host = \'' + domain + '\'')
            rows = cur.fetchall()

            print("Exporting data into csv...")

            with open("resolutionPathRedundancy.csv", "w") as csv_file:
                csv_file.write("Domain: ,"+ domain+"\n")
                csv_file.write("\n")
                csv_file.write("Synctactic_zone, nameservers, Ip, range, AS_code\n")
                line = ""
                for row in rows:
                    line = ""
                    first = True
                    for tpl in row:
                        if first:
                            first = False
                        else:
                            line = line + ","

                        line = line + str(tpl)
                    csv_file.write(line + "\n")

            print("Data stored in .csv file")
        except Exception as er:
            print("Error occurred: ", er)
        finally:
            if cur is not None:
                cur.close()


    def webAccessPathRedundancy(self, host):
        """
        This method takes a host name as argument and execute a query in the database to find the redundancy of IP addresses, their network ranges and AS_code which manage these ranges.
        These dependencies has to be previously stored on the database using the class DomainDependence.py
        :param domain: a string representing a web host
        :return: This method has no return value, instead it create a .csv file called redundancyWebAccessPath.csv
        """

        if not isinstance(host, str):
            print("Domain is not a string: ", host)
            exit(1)

        #if not host.endswith("."):
         #   domain = host+"."

        cur = None
        try:
            conn = sqlite3.connect(self.dataBase)
            cur = conn.cursor()

            cur.execute(
                'SELECT host  FROM host2directZone WHERE host = \'' + host + '\'')
            row = cur.fetchone()

            if row is None:
                print('Error: ', host,
                      ' is not the name of a host or is not present in host2IP table')
                exit(1)


            cur.execute('select distinct host2Ip.host, host2Ip.IPv4, IP2Range.range, range2AS.AS_code\
                from ((host2Ip\
                INNER JOIN IP2Range on IP2Range.ip_address = host2Ip.IPv4)\
                INNER JOIN range2AS on range2AS.IP_range = IP2Range.range)\
                where host2Ip.host = \'' + host + '\'')
            rows = cur.fetchall()

            print("Exporting data into csv...")

            with open("redundancyWebAccessPath.csv", "w") as csv_file:
                csv_file.write("host, Ip, range, AS_code\n")
                line = ""
                for row in rows:
                    line = ""
                    first = True
                    for tpl in row:
                        if first:
                            first = False
                        else:
                            line = line + ","

                        line = line + str(tpl)
                    csv_file.write(line + "\n")

            print("Data stored in .csv file")
        except Exception as er:
            print("Error occurred: ", er)
        finally:
            if cur is not None:
                cur.close()



    def nameResolutionPathArchitecturalProperties(self, domain):
        """
        This method takes a domain as argument and execute a query in the database to find the redundancy of the direct synctactic zones, the nameservers of these zones, the IP ranges of the nameservers and AS_code which manage these ranges.
        The number of different zones, nameservers, ranges of nameservers and Autonomous system the domain depends on is stored in output in a .csv file, named architecturalProperties.csv
        These dependencies has to be previously stored on the database using the class DomainDependence.py
        :param domain: a string representing a domain
        :return: This method has no return value, instead it create a .csv file called architecturalProperties.csv
        """

        if not isinstance(domain, str):
            print("Domain is not a string: ", domain)
            exit(1)

        #if not domain.endswith("."):
        #    domain = domain+"."

        cur = None
        try:
            conn = sqlite3.connect(self.dataBase)
            cur = conn.cursor()

            cur.execute(
                'SELECT host  FROM host2directZone WHERE host = \'' + domain + '\'')
            row = cur.fetchone()

            if row is None:
                print('Error: ', domain,
                      ' is not the name of a host or is not present in host2directZone table')
                exit(1)


            cur.execute('select distinct zone2synctacticDependence.synctactic_zone, zone2nameserver.nameserver, host2Ip.IPv4, IP2Range.range, range2AS.AS_code, range2AS.location_code\
                    from (((((host2directZone\
                    INNER JOIN zone2synctacticDependence on zone2synctacticDependence.zone = host2directZone.direct_zone)\
                    INNER JOIN zone2nameserver on zone2nameserver.zone = zone2synctacticDependence.synctactic_zone)\
                    INNER JOIN host2Ip on host2Ip.host = zone2nameserver.nameserver)\
                    INNER JOIN IP2Range on IP2Range.ip_address = host2Ip.IPv4)\
                    INNER JOIN range2AS on range2AS.IP_range = IP2Range.range)\
                    where host2directZone.host = \'' + domain + '\'')
            rows = cur.fetchall()

            #order the rows to zone name
            switched = True
            while switched:
                switched = False
                for i in range(len(rows) - 1):
                    print(rows[i + 1][0], rows[i][0])
                    if rows[i + 1][0] < rows[i][0]:
                        tmp = rows[i + 1]
                        rows[i + 1] = rows[i]
                        rows[i] = tmp
                        switched = True

            finalTupleList = list()

            curDom = rows[0][0]
            subRows = list()
            subRows.append(rows[0])
            for i in range(len(rows)-1):
                if i == len(rows)-2:
                    subRows.append(rows[i + 1])
                elif rows[i+1][0] == curDom:
                    subRows.append(rows[i+1])
                    continue

                nNameserver = 1
                nNetwork = 1
                nAS = 1
                nGeo = 1
                nameList = list()
                netList = list()
                asList = list()
                geoList = list()
                nameList.append(subRows[0][1])
                netList.append(subRows[0][3])
                asList.append(subRows[0][4])
                geoList.append(subRows[0][5])
                for n in range(len(subRows)-1):
                    curNameserver = subRows[n+1][1]
                    curNetwork = subRows[n+1][3]
                    curAS = subRows[n+1][4]
                    curGeo = subRows[n+1][5]
                    for b in range(n+1):
                        if curNameserver not in nameList:
                            nameList.append(curNameserver)
                            nNameserver = nNameserver +1

                        if curNetwork not in netList:
                            netList.append(curNetwork)
                            nNetwork = nNetwork +1

                        if curAS not in asList:
                            asList.append(curAS)
                            nAS = nAS +1

                        if curGeo not in geoList:
                            geoList.append(curGeo)
                            nGeo = nGeo +1

                finalTupleList.append((curDom, nNameserver, nNetwork, nAS, nGeo))
                subRows = list()
                subRows.append(rows[i+1])
                curDom = rows[i+1][0]

            print("Exporting data into csv...")

            with open("architecturalProperties.csv", "w") as csv_file:
                csv_file.write("Domain: ,"+ domain+"\n")
                csv_file.write("\n")
                csv_file.write("Zone, #nameservers, #networks, #AS, #AS_countries\n")
                line = ""
                for row in finalTupleList:
                    line = ""
                    first = True
                    for tpl in row:
                        if first:
                            first = False
                        else:
                            line = line + ","

                        line = line + str(tpl)
                    csv_file.write(line + "\n")

            print("Data stored in .csv file")
        except Exception as er:
            print("Error occurred: ", er)
        finally:
            if cur is not None:
                cur.close()


    def nameResolutionDirectZoneProperties(self, startList):
        """
                This method takes a domain as argument and execute a query in the database to find the redundancy of the direct synctactic zones, the nameservers of these zones, the IP ranges of the nameservers and AS_code which manage these ranges.
                The number of different zones, nameservers, ranges of nameservers and Autonomous system the domain depends on is stored in output in a .csv file, named architecturalProperties.csv
                These dependencies has to be previously stored on the database using the class DomainDependence.py
                :param domain: a string representing a domain
                :return: This method has no return value, instead it create a .csv file called architecturalProperties.csv
                """
        domainList = list()
        for domain in startList:
            if not isinstance(domain, str):
                print("Domain is not a string: ", domain)
                continue

            if not domain.endswith("."):
                domain = domain+"."
            domainList.append(domain)

        cur = None
        try:
            conn = sqlite3.connect(self.dataBase)
            cur = conn.cursor()
            finalTupleList = list()

            for domain in domainList:
                cur.execute(
                'SELECT host  FROM host2directZone WHERE host = \'' + domain + '\'')
                row = cur.fetchone()

                if row is None:
                    print('Error: ', domain,
                      ' is not the name of a host or is not present in host2directZone table')
                    continue

                cur.execute('select distinct host2directZone.direct_zone, zone2nameserver.nameserver, host2Ip.IPv4, IP2Range.range, range2AS.AS_code, range2AS.location_code\
                            from ((((host2directZone\
                            INNER JOIN zone2nameserver on zone2nameserver.zone = host2directZone.direct_zone)\
                            INNER JOIN host2Ip on host2Ip.host = zone2nameserver.nameserver)\
                            INNER JOIN IP2Range on IP2Range.ip_address = host2Ip.IPv4)\
                            INNER JOIN range2AS on range2AS.IP_range = IP2Range.range)\
                            where host2directZone.host = \''+domain+'\'')
                rows = cur.fetchall()

                if len(rows) == 0:
                    print("Query is not working for domain:", domain)
                    continue
                dirZone = rows[0][0]
                listNameserver = list()
                listNetwork = list()
                listAS = list()
                listGeo = list()

                for row in rows:
                    if row[1] not in listNameserver:
                        listNameserver.append(row[1])
                    if row[3] not in listNetwork:
                        listNetwork.append(row[3])
                    if row[4] not in listAS:
                        listAS.append(row[4])
                    if row[5] not in listGeo:
                        listGeo.append(row[5])

                finalTupleList.append((dirZone, len(listNameserver), len(listNetwork), len(listAS), len(listGeo)))

            print("Exporting data into csv...")

            with open("directZonesProperties.csv", "w") as csv_file:
                csv_file.write("DirectZone, #nameservers, #networks, #AS, #AS_countries\n")
                line = ""
                for row in finalTupleList:
                    line = ""
                    first = True
                    for tpl in row:
                        if first:
                            first = False
                        else:
                            line = line + ","

                        line = line + str(tpl)
                    csv_file.write(line + "\n")

            print("Data stored in .csv file")
        except Exception as er:
            print("Error occurred: ", er)
        finally:
            if cur is not None:
                cur.close()


    def nameResolutionAllDirectZoneProperties(self, startList):
        """
                This method takes a domain as argument and execute a query in the database to find the redundancy of the direct synctactic zones, the nameservers of these zones, the IP ranges of the nameservers and AS_code which manage these ranges.
                The number of different zones, nameservers, ranges of nameservers and Autonomous system the domain depends on is stored in output in a .csv file, named architecturalProperties.csv
                These dependencies has to be previously stored on the database using the class DomainDependence.py
                :param domain: a string representing a domain
                :return: This method has no return value, instead it create a .csv file called architecturalProperties.csv
                """
        domainList = list()
        for domain in startList:
            if not isinstance(domain, str):
                print("Domain is not a string: ", domain)
                continue

            if not domain.endswith("."):
                domain = domain+"."
            domainList.append(domain)

        cur = None
        try:
            conn = sqlite3.connect(self.dataBase)
            cur = conn.cursor()
            finalTupleList = list()
            cnameList = list()
            zoneAlreadyLookedFor = list()
            for domain in domainList:
                cnameList = list()
                cur.execute(
                'SELECT host  FROM host2directZone WHERE host = \'' + domain + '\'')
                row = cur.fetchone()

                if row is None:
                    print('Error: ', domain,
                      ' is not the name of a host or is not present in host2directZone table')
                    continue

                cur.execute(
                    'SELECT host, cname  FROM hostInformation WHERE host = \'' + domain + '\'')
                row = cur.fetchone()

                if row is None:
                    print('Error: ', domain,
                      ' is not the name of a host or is not present in hostInformation table')
                    continue

                cnameList.append(domain)
                cnames = None
                if row[1] != 0:
                    cur.execute('WITH RECURSIVE new_table AS (\
                        SELECT *\
                        FROM domain2cname\
                        where id = '+str(row[1])+'\
                        UNION ALL\
                        Select domain2cname.*\
                        from domain2cname\
                        join new_table on domain2cname.ID = new_table.cname)\
                        SELECT Domain from new_table')
                    cnames = cur.fetchall()

                    for each in cnames:
                        cnameList.append(each[0])

                for dom in cnameList:
                    cur.execute('select distinct host2directZone.direct_zone, zone2synctacticDependence.synctactic_zone\
                            from(host2directZone\
                            INNER JOIN zone2synctacticDependence on zone2synctacticDependence.zone = host2directZone.direct_zone)\
                            where host2directZone.host = \''+dom+'\'')
                    domns = cur.fetchall()

                    for dm in domns:
                        curDom = dm[1]
                        if curDom in zoneAlreadyLookedFor:
                            continue

                        cur.execute('select distinct zone2nameserver.zone, zone2nameserver.nameserver, host2Ip.IPv4, IP2Range.range, range2AS.AS_code, range2AS.location_code\
                            from (((zone2nameserver\
                            INNER JOIN host2Ip on host2Ip.host = zone2nameserver.nameserver)\
                            INNER JOIN IP2Range on IP2Range.ip_address = host2Ip.IPv4)\
                            INNER JOIN range2AS on range2AS.IP_range = IP2Range.range)\
                            where zone2nameserver.zone = \''+curDom+'\'')
                        rows = cur.fetchall()

                        zoneAlreadyLookedFor.append(curDom)
                        if len(rows) == 0:
                            print("Query is not working for domain:", curDom)
                            continue

                        dirZone = rows[0][0]
                        listNameserver = list()
                        listNetwork = list()
                        listAS = list()
                        listGeo = list()

                        for row in rows:
                            if row[1] not in listNameserver:
                                listNameserver.append(row[1])
                            if row[3] not in listNetwork:
                                listNetwork.append(row[3])
                            if row[4] not in listAS:
                                listAS.append(row[4])
                            if row[5] not in listGeo:
                                listGeo.append(row[5])

                        finalTupleList.append((dirZone, len(listNameserver), len(listNetwork), len(listAS), len(listGeo)))

            print("Exporting data into csv...")

            with open("allDirectZonesProperties.csv", "w") as csv_file:
                csv_file.write("DirectZone, #nameservers, #networks, #AS, #AS_countries\n")
                line = ""
                for row in finalTupleList:
                    line = ""
                    first = True
                    for tpl in row:
                        if first:
                            first = False
                        else:
                            line = line + ","

                        line = line + str(tpl)
                    csv_file.write(line + "\n")

            print("Data stored in .csv file")
        except Exception as er:
            print("Error occurred: ", er)
        finally:
            if cur is not None:
                cur.close()



    def webAccessPathRedundancyProperties(self, startList, csv = "redundancyWebAccessPathProperties.csv"):
        """
        This method takes a host name as argument and execute a query in the database to find the redundancy of IP addresses, their network ranges and AS_code which manage these ranges.
        The number of different IP, ranges and Autonomous system the domain depends on is stored in output in a .csv file, named architecturalProperties.csv
        These dependencies has to be previously stored on the database using the class DomainDependence.py
        :param domain: a string representing a web host
        :return: This method has no return value, instead it create a .csv file called redundancyWebAccessPath.csv
        """
        hostList = list()

        for host in startList:
            if not isinstance(host, str):
                print("Domain is not a string: ", host)
                continue

            if not host.endswith("."):
                host = host+"."
            hostList.append(host)

        cur = None
        try:
            conn = sqlite3.connect(self.dataBase)
            cur = conn.cursor()
            finalList = list()
            for host in hostList:
                cur.execute(
                    'SELECT host  FROM host2directZone WHERE host = \'' + host + '\'')
                row = cur.fetchone()
                if row is None:
                    print('Error: ', host,
                      ' is not the name of a host or is not present in host2IP table')
                    continue


                cur.execute('select distinct host2Ip.host, host2Ip.IPv4, IP2Range.range, range2AS.AS_code, range2AS.location_code\
                    from ((host2Ip\
                    INNER JOIN IP2Range on IP2Range.ip_address = host2Ip.IPv4)\
                    INNER JOIN range2AS on range2AS.IP_range = IP2Range.range)\
                    where host2Ip.host = \'' + host + '\'')
                rows = cur.fetchall()

                rangeList = list()
                asList = list()
                geoList = list()

                for row in rows:
                    if row[2] not in rangeList:
                        rangeList.append(row[2])
                    if row[3] not in asList:
                        asList.append(row[3])
                    if row[4] not in geoList:
                        geoList.append(row[4])

                finalList.append((host, len(rows), len(rangeList), len(asList), len(geoList)))

            print("Exporting data into csv...")

            with open(csv, "w") as csv_file:
                csv_file.write("host, #Ip, #range, #as, #locations\n")
                for el in finalList:
                    line = ""
                    line = el[0] +"," + str(el[1]) +"," + str(el[2]) +"," + str(el[3]) + "," + str(el[4])
                    csv_file.write(line + "\n")

            print("Data stored in .csv file")
        except Exception as er:
            print("Error occurred: ", er)
        finally:
            if cur is not None:
                cur.close()


    def softwareDependenciesRecurring(self, listOfDomain, csv = "softwareDependenciesRecurring.csv"):
        domainList = list()

        for dom in listOfDomain:
            if not isinstance(dom, str):
                print("Domain is not a string: ", dom)
                exit(1)

            if not dom.endswith("."):
                domainList.append(dom)
            else:
                domainList.append(dom[:len(dom)-1])

        cur = None
        try:
            conn = sqlite3.connect(self.dataBase)
            cur = conn.cursor()
            query = 'select distinct domain2Software_Dependencies.domain, domain2Software_Dependencies.software_dependence from domain2Software_Dependencies where '
            isFirst = True
            for domain in domainList:
                """
                Si deve capire se tenere domain con punto o senza perché in table domain2Software_dependencies sono senza punto
                cur.execute(
                    'SELECT host  FROM host2directZone WHERE host = \'' + domain + '\'')
                row = cur.fetchone()

                if row is None:
                    print('Error: ', domain,
                         ' is not the name of a host or is not present in host2IP table')

                    continue
                """
                if isFirst:
                    query = query + 'domain2Software_Dependencies.domain = \''+ domain + '\''
                    isFirst = False
                else:
                    query = query + ' or domain2Software_Dependencies.domain = \''+ domain + '\''


            cur.execute(query)
            rows = cur.fetchall()


            finalList = list()
            listWithoutRecurrencies = list()

            for i in range(len(rows)):
                if rows[i][1] not in listWithoutRecurrencies:
                    listWithoutRecurrencies.append(rows[i][1])
                    count = 1
                    for j in range(i +1, len(rows)):
                        if rows[i][1] == rows[j][1]:
                            count= count + 1
                    finalList.append((rows[i][1], count))

            print("Exporting data into csv...")

            with open(csv, "w") as csv_file:
                csv_file.write("Recurring software dependencies\nDomain, #recurrencies\n")
                line = ""
                for r in finalList:
                    line = r[0] +", " + str(r[1])
                    csv_file.write(line + "\n")

            print("Data stored in .csv file")
        except Exception as er:
            print("Error occurred: ", er)
        finally:
            if cur is not None:
                cur.close()


    def softwareDependenciesQuantity(self, listOfDomain, csv="softwareDependenciesQuantity.csv"):
        """
        This method given a list of domains return how many software dependencies domain each domain of the list depends on.
        :param listOfDomain: a list of domain
        :param csv: the csv file in which to save the list of domains and number of software dependencies. Default is softwareDependenciesQuantity.csv
        :return: nothing
        """
        domainList = list()

        for dom in listOfDomain:
            if not isinstance(dom, str):
                print("Domain is not a string: ", dom)
                exit(1)

            if not dom.endswith("."):
                domainList.append(dom)
            else:
                domainList.append(dom[:len(dom)-1])

        cur = None
        try:
            conn = sqlite3.connect(self.dataBase)
            cur = conn.cursor()
            finalList = list()
            for domain in domainList:
                cur.execute(
                    'SELECT host  FROM host2directZone WHERE host = \'' + domain + '.\'')
                row = cur.fetchone()

                if row is None:
                    print('Error: ', domain,
                          ' is not the name of a host or is not present in host2IP table')
                    continue

                query = 'select distinct domain2Software_Dependencies.domain, domain2Software_Dependencies.software_dependence from domain2Software_Dependencies where domain2Software_Dependencies.domain = \'' + domain + '\''
                cur.execute(query)
                rows = cur.fetchall()
                finalList.append((domain, len(rows)))


            print("Exporting data into csv...")

            with open(csv, "w") as csv_file:
                csv_file.write("Domain, #softwareDependencies\n")
                line = ""
                for r in finalList:
                    line = r[0] +", " + str(r[1])
                    csv_file.write(line + "\n")

            print("Data stored in .csv file")
        except Exception as er:
            print("Error occurred: ", er)
        finally:
            if cur is not None:
                cur.close()


    def softwareDependenciesIntegrityAndIframe(self, startingList, csv = "softwareDependenciesIntegrityAndIframe.csv"):
        domainList = list()

        for dom in startingList:
            if not isinstance(dom, str):
                print("Domain is not a string: ", dom)
                exit(1)

            if not dom.endswith("."):
                domainList.append(dom[:len(dom)-1])
            else:
                domainList.append(dom)

        cur = None
        finalList = list()
        try:
            conn = sqlite3.connect(self.dataBase)
            cur = conn.cursor()
            isFirst = True
            for domain in domainList:
                cur.execute('select distinct domain, host_dependence, integrity_present, same_iframe\
                        from domain2Software_Dependencies\
                        where domain = \''+domain+'\'')
                rows = cur.fetchall()

                for each in rows:
                    finalList.append(each)

            print("Exporting data into csv...")

            with open(csv, "w") as csv_file:
                csv_file.write("Domain, host_dependes_on, integrity_present, same_frame\n")
                line = ""
                for r in finalList:
                    line = r[0] +", " + r[1] +", " +str(r[2]) +", " + str(r[3])
                    csv_file.write(line + "\n")

            print("Data stored in .csv file")
        except Exception as er:
            print("Error occurred: ", er)
        finally:
            if cur is not None:
                cur.close()





    def geoLocalDirectZoneNameservers(self, startList, csv="geoLocalNamservers.csv"):
        """
        This method given a list of domains (name of zones) finds the nameserver of the zones, the network they belongs to, which autonomus system managed thoso networks and the county code of the AS.
        This method count how many nameservers have the same country code.
        :param domainList: a list of string representing the name of a zone
        :param csv: the csv file in which to save the list of different country code and number of nameservers which depends on it. Default is geoLocalNamservers
        :return: nothing
        """
        geoDict = dict()
        domainList = list()
        for d in startList:
            if not isinstance(d, str):
                print("Domain is not a string: ", d)
                continue

            if not d.endswith("."):
                d = d+"."
            domainList.append(d)

        cur = None
        try:
            conn = sqlite3.connect(self.dataBase)
            cur = conn.cursor()

            for domain in domainList:
                cur.execute(
                    'SELECT zone  FROM zone2synctacticDependence WHERE synctactic_zone = \'' + domain + '\'')
                row = cur.fetchone()

                if row is None:
                    print('Error: ', domain,
                      ' is not the name of a direct zone or is not present in zone2synctacticDependence table')
                    continue

                cur.execute('select distinct zone2synctacticDependence.synctactic_zone, zone2nameserver.nameserver, host2Ip.IPv4, IP2Range.range, range2AS.AS_code, range2AS.location_code\
                        from ((((zone2synctacticDependence\
                        INNER JOIN zone2nameserver on zone2nameserver.zone = zone2synctacticDependence.synctactic_zone)\
                        INNER JOIN host2Ip on host2Ip.host = zone2nameserver.nameserver)\
                        INNER JOIN IP2Range on IP2Range.ip_address = host2Ip.IPv4)\
                        INNER JOIN range2AS on range2AS.IP_range = IP2Range.range)\
                        where zone2synctacticDependence.synctactic_zone = \''+ domain+'\'')
                rows = cur.fetchall()

                if len(rows) == 0:
                    print("No result from query, domain: ", domain)
                    continue


                already = False
                for r in range(len(rows)):
                    for li in geoDict.keys():
                        if rows[r][5] == li:
                            already = True
                            geoDict[li] = geoDict[li] + 1
                            break

                    if not already:
                        geoDict[rows[r][5]]= 1
                    already = False

            with open(csv, "w") as csv_file:
                csv_file.write("GeolocNameserver, HowMany\n")
                line = ""
                for k, v in geoDict.items():
                    line = k +", " + str(v)
                    csv_file.write(line + "\n")

            print("Data stored in .csv file")
        except Exception as er:
            print("Error occurred: ", er)
        finally:
            if cur is not None:
                cur.close()



    def geoLocalIPHost(self, startList, csv="geoLocalHostIp.csv"):
        """
        This method given a list of host name finds in the database the network they belongs to, which autonomus system managed thoso networks and the county code of the AS.
        This method count how many IP have the same country code.
        :param hostList: list of host name as strings
        :param csv: the csv file in which to save the list of different country code and number of IP which depends on it. Default is geoLocalHostIp.csv
        :return: nothing
        """
        geoDict = dict()
        hostList = list()
        for d in startList:
            if not isinstance(d, str):
                print("Domain is not a string: ", d)
                continue

            if not d.endswith("."):
                d = d +"."
            hostList.append(d)

        cur = None
        try:
            conn = sqlite3.connect(self.dataBase)
            cur = conn.cursor()

            for host in hostList:
                cur.execute(
                    'SELECT host  FROM host2Ip WHERE host = \'' + host + '\'')
                row = cur.fetchone()

                if row is None:
                    print('Error: ', host,
                          ' is not the name of a host or is not present in host2Ip table')
                    continue

                cur.execute('select distinct host2Ip.host, host2Ip.IPv4, IP2Range.range, range2AS.AS_code, range2AS.location_code\
                        from ((host2Ip\
                        INNER JOIN IP2Range on IP2Range.ip_address = host2Ip.IPv4)\
                        INNER JOIN range2AS on range2AS.IP_range = IP2Range.range)\
                        where host2Ip.host =\'' + host + '\'')
                rows = cur.fetchall()

                if len(rows) == 0:
                    print("No result from query, host: ", host)
                    continue

                already = False
                for r in range(len(rows)):
                    for li in geoDict.keys():
                        if rows[r][4] == li:
                            already = True
                            geoDict[li] = geoDict[li] + 1
                            break

                    if not already:
                        geoDict[rows[r][4]] = 1
                    already = False

            with open(csv, "w") as csv_file:
                csv_file.write("GeolocIP, HowMany\n")
                line = ""
                for k, v in geoDict.items():
                    line = k + ", " + str(v)
                    csv_file.write(line + "\n")

            print("Data stored in .csv file")
        except Exception as er:
            print("Error occurred: ", er)
        finally:
            if cur is not None:
                cur.close()


    def sameNetworkandASDependence(self, domainList, csv="networkAndASDep.csv"):
        """
        This method given a list of domain (name of zones) return how many of these zones depends on a network, has at least a nameserver which belong to a specific network, and on a autonomous system, has at least a nameserver which belongs to a network managed by a specific autonomous system
        The result is stored in a csv file.
        :param domainList: a list of domain, name of zones, as string
        :param csv: the name of a csv file in which to store the result. Default is networkAndASDep.csv
        :return: nothing
        """
        #how many direct zones depends on the same network and as with their nameserver
        #conto il numero di zone differenti che dipendono da stessa network o as
        listRows = list()
        for d in domainList:
            if not isinstance(d, str):
                print("Domain is not a string: ", d)
                exit(1)

          # if not domain.endswith("."):
       #    domain = domain+"."

        cur = None
        try:
            conn = sqlite3.connect(self.dataBase)
            cur = conn.cursor()

            for domain in domainList:
                cur.execute(
                    'SELECT zone  FROM zone2synctacticDependence WHERE synctactic_zone = \'' + domain + '\'')
                row = cur.fetchone()

                if row is None:
                    print('Error: ', domain,
                      ' is not the name of a direct zone or is not present in zone2synctacticDependence table')
                    continue

                cur.execute('select distinct zone2synctacticDependence.synctactic_zone, zone2nameserver.nameserver, host2Ip.IPv4, IP2Range.range, range2AS.AS_code, range2AS.location_code\
                        from ((((zone2synctacticDependence\
                        INNER JOIN zone2nameserver on zone2nameserver.zone = zone2synctacticDependence.synctactic_zone)\
                        INNER JOIN host2Ip on host2Ip.host = zone2nameserver.nameserver)\
                        INNER JOIN IP2Range on IP2Range.ip_address = host2Ip.IPv4)\
                        INNER JOIN range2AS on range2AS.IP_range = IP2Range.range)\
                        where zone2synctacticDependence.synctactic_zone = \''+ domain+'\'')
                rows = cur.fetchall()

                if len(rows) == 0:
                    print("No result from query, domain: ", domain)
                    continue

                for row in rows:
                    listRows.append(row)

            #i velue dei dizionari sono una lista di due elementi, il primo è quanti diversi as o net da cui dipende zona, il secondo è l'ultima zona di riferimento
            asDict = dict()
            already = False
            for r in range(len(listRows)):
                for li in asDict.keys():
                    if listRows[r][4] == li:
                        already = True
                        if asDict[li][1] != listRows[r][0]:
                            asDict[li] = [asDict[li][0] + 1, listRows[r][0]]
                        break

                if not already:
                    asDict[listRows[r][4]]= [1, listRows[r][0]]
                already = False

            netDict = dict()
            already = False
            for r in range(len(listRows)):
                for li in netDict.keys():
                    if listRows[r][3] == li:
                        already = True
                        if netDict[li][1] != listRows[r][0]:
                            netDict[li] = [netDict[li][0] + 1, listRows[r][0]]
                        break

                if not already:
                    netDict[listRows[r][3]] = [1, listRows[r][0]]
                already = False

            with open(csv, "w") as csv_file:
                csv_file.write("AS, HowManyDependsOnIt\n")
                line = ""
                for k, v in asDict.items():
                    line = k +", " + str(v[0])
                    csv_file.write(line + "\n")

                csv_file.write("\n")
                csv_file.write("Network, HowManyDependsOnIt\n")
                for k, v in netDict.items():
                    line = k +", " + str(v[0])
                    csv_file.write(line + "\n")

            print("Data stored in .csv file")
        except Exception as er:
            print("Error occurred: ", er)
        finally:
            if cur is not None:
                cur.close()



    def sameNetworkandASgivenIPs(self, hostList, csv = "networkAndASgivenIPs.csv"):
        """
        This method given a list of hosts (name of hosts) return how many of these depends on a network, has at least an IP which belong to a specific network, and on a autonomous system, has at least an IP which belongs to a network managed by a specific autonomous system
        The result is stored in a csv file.
        :param domainList: a list of host, name of host, as string
        :param csv: the name of a csv file in which to store the result. Default is networkAndASgivenIPs.csv
        :return: nothing
        """
        listRows = list()
        for d in hostList:
            if not isinstance(d, str):
                print("Domain is not a string: ", d)
                exit(1)

        # if not domain.endswith("."):
        #    domain = domain+"."

        cur = None
        try:
            conn = sqlite3.connect(self.dataBase)
            cur = conn.cursor()

            for host in hostList:
                cur.execute(
                    'SELECT host  FROM host2Ip WHERE host = \'' + host + '\'')
                row = cur.fetchone()

                if row is None:
                    print('Error: ', host,
                          ' is not the name of a host or is not present in host2Ip table')
                    continue

                cur.execute('select distinct host2Ip.host, host2Ip.IPv4, IP2Range.range, range2AS.AS_code, range2AS.location_code\
                        from ((host2Ip\
                        INNER JOIN IP2Range on IP2Range.ip_address = host2Ip.IPv4)\
                        INNER JOIN range2AS on range2AS.IP_range = IP2Range.range)\
                        where host2Ip.host =\'' + host + '\'')
                rows = cur.fetchall()

                if len(rows) == 0:
                    print("No result from query, host: ", host)
                    continue

                for row in rows:
                    listRows.append(row)


            asDict = dict()
            already = False
            for r in range(len(listRows)):
                for li in asDict.keys():
                    if listRows[r][3] == li:
                        already = True
                        if asDict[li][1] != listRows[r][0]:
                            asDict[li] = [asDict[li][0] + 1, listRows[r][0]]
                        break

                if not already:
                    asDict[listRows[r][3]] = [1, listRows[r][0]]
                already = False

            netDict = dict()
            already = False
            for r in range(len(listRows)):
                for li in netDict.keys():
                    if listRows[r][2] == li:
                        already = True
                        if netDict[li][1] != listRows[r][0]:
                            netDict[li] = [netDict[li][0] + 1, listRows[r][0]]
                        break

                if not already:
                    netDict[listRows[r][2]] = [1, listRows[r][0]]
                already = False

            with open(csv, "w") as csv_file:
                csv_file.write("AS, HowManyDependsOnIt\n")
                line = ""
                for k, v in asDict.items():
                    line = k + ", " + str(v[0])
                    csv_file.write(line + "\n")

                csv_file.write("\n")
                csv_file.write("Network, HowManyDependsOnIt\n")
                for k, v in netDict.items():
                    line = k + ", " + str(v[0])
                    csv_file.write(line + "\n")

            print("Data stored in .csv file")
        except Exception as er:
            print("Error occurred: ", er)
        finally:
            if cur is not None:
                cur.close()



    def exportHostToASData(self):
        """
        This method execute a query in the database, which the name is saved in dataBase field, and save the information about hosts, their IP addresses, network numbers and autonomous system in a .csv file called hostToAS.csv
        :return: This method has no return value, instead it create a .csv file called hostToAS.csv
        """
        try:
            conn = sqlite3.connect(self.dataBase)
            cur = conn.cursor()
            cur.execute('select distinct host2Ip.host, host2Ip.IPv4, IP2Range.range, range2verificated.verificated, range2AS.AS_description\
                from (((host2Ip INNER JOIN IP2Range on host2Ip.IPv4 = IP2Range.ip_address)\
                INNER JOIN range2AS on IP2Range.range = range2AS.IP_range)\
                INNER JOIN  range2verificated on range2verificated.range = IP2Range.range)')
            rows = cur.fetchall()

            print("Exporting data into csv...")

            with open("hostsToAS.csv", "w") as csv_file:
                csv_file.write("Host, IPv4, Range, verificated,AS_description\n")
                line = ""
                for row in rows:
                    line = ""
                    first = True
                    for tpl in row:
                        if first:
                            first = False
                        else:
                            line = line + ","

                        if isinstance(tpl, str):
                            newTpl = tpl.replace(",", " ")
                            line = line + newTpl
                        else:
                            line = line + str(tpl)
                    csv_file.write(line + "\n")

            print("Data stored in .csv file")
        except Exception as er:
            print("Error occurred: ", er)
        finally:
            if cur is not None:
                cur.close()



    def exportWebHostDependenciesData(self, hostName):
        """
        This method takes a webhost name as attribute and execute a query in the database, which the name is saved in dataBase field, to find the zones name, nameserver and IP address of the nameservers that webhost depends on.
        These dependencies has to be previously stored on the database using the class DomainDependence.py
        :param hostName: a string, the name of a webhost to look for in the database
        :return: This method has no return value, instead it create a .csv file called webhostZoneNameserversDependencies.csv
        """
        try:
            conn = sqlite3.connect(self.dataBase)
            cur = conn.cursor()
            listDomainOther = list()

            cur.execute('SELECT * FROM hostInformation WHERE host = \''+hostName+'\'')
            row = cur.fetchone()

            if row is None:
                print('Error: ', hostName, ' is not a web server, maybe is not resolved yet, no information are stored in database')
                return

            startCname = row[2]
            query = 'WITH RECURSIVE new_table AS (\
                SELECT *\
                FROM domain2cname\
                where id = '+str(startCname)+'\
                UNION ALL\
                Select domain2cname.*\
                from domain2cname\
                join new_table on domain2cname.ID = new_table.cname\
                )\
                SELECT Domain from new_table'

            cur.execute(query)
            rows = cur.fetchall()
            for el in rows:
                listDomainOther.append(el[0])

            query = 'WITH RECURSIVE new_table AS (\
                select host2directZone.host, zone2synctacticDependence.synctactic_zone, zone2nameserver.nameserver\
                from ((host2directZone\
                INNER JOIN zone2synctacticDependence on host2directZone.direct_zone = zone2synctacticDependence.zone)\
                INNER JOIN zone2nameserver on zone2nameserver.zone = zone2synctacticDependence.synctactic_zone)\
                where host2directZone.host = \''+hostName+'\''

            for el in listDomainOther:
                query = query + ' OR host2directZone.host = \''+el+'\''

            query = query + ' UNION\
                select host2directZone.host, zone2synctacticDependence.synctactic_zone, zone2nameserver.nameserver\
                from ((host2directZone\
                INNER JOIN zone2synctacticDependence on host2directZone.direct_zone = zone2synctacticDependence.zone)\
                INNER JOIN zone2nameserver on zone2nameserver.zone = zone2synctacticDependence.synctactic_zone)\
                join new_table on host2directZone.host = new_table.nameserver\
                )\
                SELECT DISTINCT new_table.synctactic_zone as zone, new_table.nameserver, host2Ip.IPv4\
                from new_table\
                INNER JOIN host2Ip on host2Ip.host = new_table.nameserver'


            cur.execute(query)
            rows = cur.fetchall()

            print("Exporting data into csv...")

            with open("webhostZoneNameserversDependencies.csv", "w") as csv_file:
                csv_file.write("Zone, NameServers, IPv4\n")
                line = ""
                for row in rows:
                    line = ""
                    first = True
                    for tpl in row:
                        if first:
                            first = False
                        else:
                            line = line + ","
                        newTpl = tpl.replace(",", " ")
                        line = line + newTpl
                    csv_file.write(line + "\n")

            print("Data stored in .csv file")
        except Exception as er:
            print("Error occurred: ", er)
        finally:
            if cur is not None:
                cur.close()


    def exportNameserverDependenciesData(self, nameServer):
        """
        This method takes a nameserver name as attribute and execute a query in the database, which the name is saved in dataBase field, to find the zones name, nameserver and IP address of the nameservers that nameserver depends on.
        These dependencies has to be previously stored on the database using the class DomainDependence.py
        :param nameServer: a string representing the name of a nameserver
        :return: This method has no return value, instead it create a .csv file called nameserverDependencies.csv
        """
        try:
            conn = sqlite3.connect(self.dataBase)
            cur = conn.cursor()
            cur.execute(
                'WITH RECURSIVE new_table AS (\
                select host2directZone.host, zone2synctacticDependence.synctactic_zone, zone2nameserver.nameserver\
                from ((host2directZone\
                INNER JOIN zone2synctacticDependence on host2directZone.direct_zone = zone2synctacticDependence.zone)\
                INNER JOIN zone2nameserver on zone2nameserver.zone = zone2synctacticDependence.synctactic_zone)\
                where host2directZone.host = \'' + nameServer + '\'\
                           UNION\
                           select host2directZone.host, zone2synctacticDependence.synctactic_zone, zone2nameserver.nameserver\
                           from ((host2directZone\
                           INNER JOIN zone2synctacticDependence on host2directZone.direct_zone = zone2synctacticDependence.zone)\
                           INNER JOIN zone2nameserver on zone2nameserver.zone = zone2synctacticDependence.synctactic_zone)\
                           join new_table on host2directZone.host = new_table.nameserver\
                           )\
                           SELECT DISTINCT new_table.synctactic_zone as zone, new_table.nameserver, host2Ip.IPv4\
                           from new_table\
                           INNER JOIN host2Ip on host2Ip.host = new_table.nameserver')
            rows = cur.fetchall()

            print("Exporting data into csv...")

            with open("nameserverDependencies.csv", "w") as csv_file:
                csv_file.write("Zone, NameServers, IPv4\n")
                line = ""
                for row in rows:
                    line = ""
                    first = True
                    for tpl in row:
                        if first:
                            first = False
                        else:
                            line = line + ","
                        newTpl = tpl.replace(",", " ")
                        line = line + newTpl
                    csv_file.write(line + "\n")

            print("Data stored in .csv file")
        except Exception as er:
            print("Error occurred: ", er)
        finally:
            if cur is not None:
                cur.close()



    def exportZoneToNameserver(self, zoneName):
        try:
            conn = sqlite3.connect(self.dataBase)
            cur = conn.cursor()

            cur.execute('SELECT synctactic_zone  FROM zone2synctacticDependence WHERE synctactic_zone = \'' + zoneName + '\'')
            row = cur.fetchone()

            if row is None:
                print('Error: ', zoneName,
                      ' is not the name of a zone or is not present in database')
                exit(1)

            cur.execute('select distinct zone2nameserver.nameserver, host2Ip.IPv4, IP2Range.range, range2verificated.verificated, range2AS.AS_code, range2AS.AS_description\
                from (((((zone2synctacticDependence\
                INNER JOIN zone2nameserver on zone2synctacticDependence.synctactic_zone = zone2nameserver.zone)\
                INNER JOIN  host2Ip on host2Ip.host = zone2nameserver.nameserver)\
                INNER JOIN IP2Range on IP2Range.ip_address = host2Ip.IPv4)\
                INNER JOIN range2verificated on range2verificated.range = IP2Range.range)\
                INNER JOIN range2AS on range2AS.IP_range = IP2Range.range)\
                where zone2synctacticDependence.synctactic_zone =  \'' + zoneName + '\'')
            rows = cur.fetchall()

            print("Exporting data into csv...")

            with open("nameserverGivenZone.csv", "w") as csv_file:
                csv_file.write("ZONE: ,"+ zoneName+"\n")
                csv_file.write("\n")
                csv_file.write("NameServers, IPv4, NetNumber, Verificated, AS_code, AS_description\n")
                line = ""
                for row in rows:
                    line = ""
                    first = True
                    for tpl in row:
                        if first:
                            first = False
                        else:
                            line = line + ","

                        if isinstance(tpl, str):
                            newTpl = tpl.replace(",", " ")
                            line = line + newTpl
                        else:
                            line = line + str(tpl)
                    csv_file.write(line + "\n")

            print("Data stored in .csv file")
        except Exception as er:
            print("Error occurred: ", er)
        finally:
            if cur is not None:
                cur.close()



#finalScriptDB3.sqlite, finalDB, finalScriptDBInfocertSFDEP
#o = dbAnalyser("baselineDBSoftware.sqlite")
#o.nameResolutionPathArchitecturalProperties("www.gstatic.com.")

#fhand = open("Buff.txt", 'r')
#lines = fhand.readlines()
#lista = list()
#for line in lines:
#    lista.append(line.strip())
#print(lista)
#o.sameNetworkandASgivenIPs(lista)
#o.softwareDependenciesIntegrityAndIframe(["www.google-analytics.com."])


#riprova code.jquery.com e maxcdn.bootstrapcdn.com.