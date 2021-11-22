from Resolver import Resolver
from NetNumberResolver import NetNumberResolver
from SoftwareDependencies import SoftwareDependencies
from LandingSite import LandingSite
from DomainDependence import DomainDependence
from ROVScrape import ROVScraper
from ScriptOriginScrape import ScriptOriginScraper


"""
Configuration
A few things has to be configured before the start:

1)  For SoftwareDependencies, ROVScraper and DomainDependence classes to work the user needs to install selenium selenium-wire and requests.
    To do that the user can use the command line:
    pip install selenium
    pip install selenium-wire
    pip install requests
    
    Down below the methods filterDependencies of SoftwareDependencies class, the method rangeVerificated of DomainDependence class and ROVScrape constructor and loadASPage method are called, 
    in this way it is possible for the user to check if selenium is properly installed 

2)  For Resolver class to work the user needs to install the dnspython package.
    To do that the user can use the command line:
    pip install dnspython
        
    For more details visit: https://github.com/rthalley/dnspython
    
3)  To make class netNumberResolver.py works the user has to set the path to a .tsv file, which should be a database with network number information. A good database is downloadable from site: https://iptoasn.com/
    To do so put the path as input in line 49 of this script
    Example:
    path_ip2asn = 'C:/Users/leona/Desktop/TesiMagistrale/IPv4ToASN/ip2asn-v4.tsv'

4)  To make some classes works the user has to set the path to Firefox executable file.
    To do so put the path as input in line 50 of this main script and change the 'path_firefox' variable
    Example:
    path_firefox = 'C:/Program Files/Mozilla Firefox/firefox.exe'
    
5)  Download geckodriver and then set the path to geckodriver in variable path_geckodriver in line 51, this is needed to make some classes works
    Example:
    path_geckodriver = '/Users/leona/Desktop/TesiMagistrale/PythonProject/MyPackages/geckodriver'

6) OPTIONAL: you can change the variables domain and ip in lines 54 and 55 to try different execution of this main script.
    
The configuration is now complete, try to execute this script to see if everything is fine. You can also change the domain and ip parameters down below if you want to test the execution with different parameters
"""

#define path here:
path_ip2asn = 'C:\\Users\\fabbi\\PycharmProjects\\ThesisWork\\file_cache\\ip2asn-v4.tsv' #C:/Users/leona/Desktop/TesiMagistrale/IPv4ToASN/ip2asn-v4.tsv
path_firefox = '"C:\\Program Files\\Mozilla Firefox\\firefox.exe"' #C:/Program Files/Mozilla Firefox/firefox.exe
path_geckodriver = 'C:\\geckodriver-v0.30.0-win64' #C:/Users/Alberto/Downloads/geckodriver

#Try: www.units.it, www.wordreference.com and different IP addresses
domain = "www.networkfabbio.ns0.it"
ip = "112.44.67.12"

#Resolver input a cache file or nothing
#findDNSInfo input a web domain
print("Test Resolver:")
objResolver = Resolver()
objResolver.findDNSInfo(domain)
print("Resolver test completed!")
"""
Output will looks like this:
Test Resolver:
Looking for zones  www.google.com depends on...
Depends on:  .
Depends on:  com.
Depends on:  google.com.
Depends on:  net.
Depends on:  root-servers.net.
Depends on:  gtld-servers.net.
Depends on:  nstld.com.
Resolver test completed!
"""
print("\n\n")

#NetNumberResolver.resolve input is a IP address
print("Test NetNumberResolver:")
print("Trying to find the network of the example IP address \'", ip,"\' in database")
objNetNumberResolver = NetNumberResolver.resolve(ip, netNumberDatabase=path_ip2asn)
print("NetNumberResolver test completed!")
"""
Output will be like this:
Test NetNumberResolver:
Trying to find the network of the example IP address ' 112.44.67.12 ' in database
Looking for network number of address:  112.44.67.12
Found network for  112.44.67.12 : range  112.43.0.0  to  112.44.71.255 , AS:   CMNET-GD Guangdong Mobile Communication Co.Ltd.
NetNumberResolver test completed!
"""
print("\n")

#SoftwareDependencies.filterDependencies input is an url and the firefox binary file path, modify this path as appropriate
print("Test class SoftwareDependencies:")
SoftwareDependencies.filterDependencies("https://"+domain+"/", fPath=path_firefox, dPath=path_geckodriver)
print("SoftwareDependencies class test completed!")
"""Will print something which looks like:
Test SoftwareDependencies:
Looking for software dependencies of domain:  www.google.com
Dependencies found:
 URL  |   response_code   |   content-Type
https://tracking-protection.cdn.mozilla.net/social-track-digest256/91.0/1626815062   |    200  |    application/octet-stream
https://tracking-protection.cdn.mozilla.net/analytics-track-digest256/91.0/1626815062   |    200  |    application/octet-stream
https://tracking-protection.cdn.mozilla.net/content-track-digest256/91.0/1626815062   |    200  |    application/octet-stream
https://www.gstatic.com/external_hosted/createjs/createjs-2015.11.26.min.js   |    200  |    text/javascript
...
SoftwareDependencies class test completed!
"""
print("\n\n")


#LandingSite input is a webdomain
print("Test LandingSite:")
print("Looking for landing site of domain: ", domain)
objLanding = LandingSite(domain)
print("Landing site via HTTP: ", objLanding.httpSite, "\nLanding site via HTTPS:", objLanding.httpsSite, "\nAccessing via HTTP history:",objLanding.httpHistory, "\nAccessing via HTTPS history:", objLanding.httpsHistory)
print("LandingSite test completed!")
"""
Output will be:
Test LandingSite:
Looking for landing site of domain:  www.google.com
Landing site via HTTP:  www.google.com. 
Landing site via HTTPS: www.google.com. 
Accessing via HTTP history: ['http://www.google.com/'] 
Accessing via HTTPS history: ['https://www.google.com/']
LandingSite test completed!
"""
print("\n\n")


#DomainDependence.rangeVerificated inputs are: an autonomous system code, a list of range managed by the same autonomous system and a driver Path and firefox binary path
print("Test DomainDependence:")
print("Testing an example AS: AS21342, and two of its network: 96.7.49.0/22, 95.100.168.0/24")
listRange = DomainDependence.rangeVerificated("AS21342", ["96.7.49.0/22", "95.100.168.0/24"], dPath=path_geckodriver, fPath=path_firefox)
print("Network  |   VLD")
for l in listRange:
    print(l[0], "   |   ", l[1])
print("DomainDependence test completed!")
"""
Output will be:
Test DomainDependence:
Testing an example AS: AS21342, and two of its network: 96.7.49.0/22, 95.100.168.0/24
Headless browser created
Loading page  https://stats.labs.apnic.net/roa/AS21342  ...
Page loaded
Script being executed, sleeping...
Awakened!
Destructor executed
Network  |   VLD
96.7.49.0/22    |    False
95.100.168.0/24    |    True
DomainDependence test completed!
"""
print("\n\n")

#ROVScraper input dPath and fPath are, respectively, the geckodriver path and firefox path
print("Test ROVScraper:")
print("Testing with AS702")
rovScraperObj = ROVScraper(dbg=True, dPath=path_geckodriver, fPath=path_firefox)
rovScraperObj.loadASPage('702')
print("ROVScraper test completed!")
"""Output will be:
Test ROVScraper:
Testing with AS702
Headless browser created
Loading page  https://stats.labs.apnic.net/roa/AS702  ...
Page loaded
Script being executed, sleeping...
Awakened!
ROVScraper test completed!
"""
print("\n\n")

#scrapingScriptObject.getScriptOriginsDomainsList input is an url
print("Test ScriptOriginScraper:")
print("Testing the Url https://"+domain+"/")
scrapingScriptObject = ScriptOriginScraper(dPath=path_geckodriver, fPath=path_firefox)
li = scrapingScriptObject.getScriptOriginsDomainsList("https://"+domain+"/")
print(" Domain  |   script  |   integrity_present   |   same_iframe")
for i in li:
    print(i[0], "   |   ", i[1], "  |   ", i[2], "  |   ", i[3])
print("ScriptOriginScraper test completed!")
"""Will be printed:
Test ScriptOriginScraper:
Testing the Url https://www.google.com/
Domain:  www.google.com
Destructor executed
Starting headless browser...
Scraping scripts...
 Domain  |   script  |   integrity_present   |   same_iframe
apis.google.com    |    _/scs/abc-static/_/js/k=gapi.gapi.en.7RphtNcGHDQ.O/m=gapi_iframes,googleapis_client/rt=j/sv=1/d=1/ed=1/rs=AHpOoo_-zmYhp_Ir7_CCxM3l-AckMvaI9A/cb=gapi.loaded_0   |    False   |    False
www.gstatic.com    |    og/_/js/k=og.qtm.en_US.eyZtLN7gU00.O/rt=j/m=qabr,q_dnp,qcwid,qapid,qald/exm=qaaw,qadd,qaid,qein,qhaw,qhbr,qhch,qhga,qhid,qhin,qhpr/d=1/ed=1/rs=AA2YrTvbnfZ7vgSllYOF3f_IHBGeFFy7Mg   |    False   |    False
www.gstatic.com    |    external_hosted/createjs/createjs-2015.11.26.min.js   |    False   |    False
www.gstatic.com    |    external_hosted/cannonjs/cannon.min.js   |    False   |    False
www.gstatic.com    |    external_hosted/expr_eval/dist/bundle.min.js   |    False   |    False
Destructor executed
ScriptOriginScraper test completed!
"""