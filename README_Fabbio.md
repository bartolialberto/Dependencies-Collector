# LavoroTesi
## Python setup
The python version used to develop this software is 3.8
The package manager(pip) version used is 21.2.2

The python modules imported in this project:

```
dns
csv
pathlib
re
urllib
selenium
seleniumwire
ipaddress
requests
gzip
peewee
```

Make sure your python interpreter has all of them.
Probably the only modules to install for default environments are: dnspython, selenium, 
selenium-wire and peewee.
So you can install every one of them using pip (if present in the environment):

```
pip install dnspython==2.1.0
pip install selenium==4.1.0
pip install selenium-wire==4.5.5
pip install peewee==3.14.8
```

You can install them all using one command:

```
pip install dnspython==2.1.0 selenium==4.1.0 selenium-wire==4.5.5 dnspython==2.1.0 peewee==3.14.8
```

## Configuration
The application input consists in 2 lists: a list of webservers (URLs without scheme) and a list of mail domains
(domain names).

The application uses 2 vital folders: the 'input' folder used to contain all the necessary files to function
(described later), and the 'output' folder that contains the results of an execution gone well.
Both folders are created in the project root directory (PRD): 'LavoroTesi'.

To configure the application you have to:
1) Use Windows as OS
2) Have Firefox installed
3) Download geckodriver (https://github.com/mozilla/geckodriver/releases) and put the executable file in the
input folder of the application

Also, the application needs the .tsv database taken from https://iptoasn.com/ (in the 'input' folder) but
it is controlled by the application itself, and if it is absent (or updated less than an hour ago) it will be
downloaded, extracted and replaced automatically.
Obviously you can copy such database in the folder manually.

## Configuration: input folder
The input folder is a directory contained in the project root directory (PRD) named 'input'.
This folder's purpose is to contain all the necessary "tools" to make the application work.
The expected tools' list is:

1) the geckodriver executable file (not the archive); you can name this file whatever you want as long it is a
.exe file
2) the network number database (.tsv file); you can name this file whatever you want as long it is a .tsv file
3) OPTIONAL: a file named 'webservers.txt' containing all the webserver you want to use as input, one per line
4) OPTIONAL: a file named 'mail_domains.txt' containing all the mail domains you want to use as input, one per line
5) just for application' safety it is present a .gitkeep file. Do not modify/delete this file

![alt text](res/input.jpg)

## Configuration: output folder
The output folder is a directory contained in the project root directory (PRD) named 'output'.
This folder's purpose is to contain all the results (as files) from the execution of the application.
The expected result files are:

1) a .csv file named 'dns_cache.csv' containing the entire cache from the DNS resolver. If this file is not absent, it
is automatically loaded when the application starts, otherwise the DNS cache resolver starts empty
2) a .csv file named 'error_logs.csv' containing all the registered errors encountered during the entire elaboration of
the application
3) a .sqlite file named 'results.sqlite' containing all the application data registered during its elaboration using the
E-R schema presented further in this Readme.md file
4) just for application' safety it is present a .gitkeep file. Do not modify/delete this file.

![alt text](res/output.jpg)

## How to run
The application starts executing the main.py file.
The only application input/argument is a list of domain name. You can set them in 2 ways:
1) via command line
2) via 2 .txt file put in the input folder: one named 'websites.txt' containing websites one per line and one named
'mail_domains.txt' containing mail domains one per line.

If no arguments are found, the application will start using 2 default list to show its behaviour:

websites:
```
google.it/doodles
www.youtube.it/feed/explore
```

mail domains:
```
gmail.com
outlook.com
```

## Snapshot exception mechanism
If an unwanted exception occurs, the application will notice that and will take a snapshot of the initial state of
the execution to be studied/resolved later. It will create a sub-folder (relative to the SNAPSHOTS folder) using
the current timestamp (as name) containing:
1) a .csv file of the cache before the actual elaboration occurred
2) a .txt file containing the final domain name list
3) a .txt containing the type of the exception, the result of the str(.) method used on the exception and the traceback
object print

## Execution results
The final state of the DNS cache will be exported as .csv file, and so will be the application error logs. Everything
will be put in the 'output' folder.
Results of each entity are saved in the sqlite database put in the 'output' folder with name: 'results.sqlite' .

The ER schema of such database is shown at the end of this readme file.

The application can be seen as a block diagram:
![alt text](res/schema_flusso.jpg)

The expected prints during its execution of each component are:

LandingResolver:
```
START DNS DEPENDENCIES RESOLVER
Cache has 395 entries.
Looking at zone dependencies for 'google.it'..
Depends on zone: .    [NON-AUTHORITATIVE]
Depends on zone: it.
Depends on zone: google.it.
Depends on zone: net.    [NON-AUTHORITATIVE]
Depends on zone: root-servers.net.    [NON-AUTHORITATIVE]
Depends on zone: nic.it.
Depends on zone: dns.it.
Depends on zone: cnr.it.
Depends on zone: com.    [NON-AUTHORITATIVE]
Depends on zone: google.com.    [NON-AUTHORITATIVE]
Depends on zone: gtld-servers.net.    [NON-AUTHORITATIVE]
Depends on zone: ge.cnr.it.
Depends on zone: nstld.com.    [NON-AUTHORITATIVE]
Depends on zone: ieiit.cnr.it.
Dependencies recap: 14 zones, 19 cache entries added, 0 errors.

[...]

END DNS DEPENDENCIES RESOLVER
```


LandingResolver for websites:
```
START WEB SITE LANDING RESOLVER
Trying to resolve landing page of web site: google.it/doodles
***** via HTTPS *****
HTTPS Landing url: https://www.google.com/doodles
HTTPS WebServer: www.google.com/doodles
HTTPS IP: 216.58.198.36
Strict Transport Security: False
HTTPS Redirection path:
----> [1/1]: https://www.google.com/doodles
***** via HTTP *****
HTTP Landing url: https://www.google.com/doodles
HTTP WebServer: www.google.com/doodles
HTTP IP: 216.58.198.36
Strict Transport Security: False
HTTP Redirection path:
----> [1/1]: https://www.google.com/doodles

[...]

END WEB SITE LANDING RESOLVER
```

Mail domains resolver (DnsResolver):
```
START MAIL DOMAINS RESOLVER
Resolving mail domain: gmail.com
mail_server[1/5]: 30 alt3.gmail-smtp-in.l.google.com.
mail_server[2/5]: 5 gmail-smtp-in.l.google.com.
mail_server[3/5]: 20 alt2.gmail-smtp-in.l.google.com.
mail_server[4/5]: 10 alt1.gmail-smtp-in.l.google.com.
mail_server[5/5]: 40 alt4.gmail-smtp-in.l.google.com.

[...]

END MAIL DOMAINS RESOLVER
```


DnsResolver:
```
START DNS DEPENDENCIES RESOLVER
Cache has 77 entries.
Looking at zone dependencies for 'www.google.com'..
Depends on zone: .			[NON-AUTHORITATIVE]
Depends on zone: com.			[NON-AUTHORITATIVE]
Depends on zone: google.com.			[NON-AUTHORITATIVE]
Depends on zone: net.			[NON-AUTHORITATIVE]
Depends on zone: root-servers.net.			[NON-AUTHORITATIVE]
Depends on zone: gtld-servers.net.			[NON-AUTHORITATIVE]
Depends on zone: nstld.com.			[NON-AUTHORITATIVE]
Dependencies recap: 7 zones, 0 cache entries added, 0 errors.

[...]

END DNS DEPENDENCIES RESOLVER
```


IpAsDatabase:
```
START IP-AS RESOLVER
Handling domain[0] 'www.google.com'
--> Handling zone[0] '.'
----> for nameserver[0] 'c.root-servers.net.' (192.33.4.12) found AS2149: [192.33.4.0 - 192.33.4.255]. Belonging network: 192.33.4.0/24
----> for nameserver[1] 'a.root-servers.net.' (198.41.0.4) found AS396540: [198.41.0.0 - 198.41.0.255]. Belonging network: 198.41.0.0/24
----> for nameserver[2] 'f.root-servers.net.' (192.5.5.241) found AS3557: [192.5.4.0 - 192.5.5.255]. Belonging network: 192.5.4.0/23
----> for nameserver[3] 'i.root-servers.net.' (192.36.148.17) found AS29216: [192.36.148.0 - 192.36.149.255]. Belonging network: 192.36.148.0/23
----> for nameserver[4] 'b.root-servers.net.' (199.9.14.201) found AS394353: [199.9.14.0 - 199.9.15.255]. Belonging network: 199.9.14.0/23
----> for nameserver[5] 'l.root-servers.net.' (199.7.83.42) found AS20144: [199.7.82.0 - 199.7.83.255]. Belonging network: 199.7.82.0/23
----> for nameserver[6] 'm.root-servers.net.' (202.12.27.33) found AS7500: [202.12.27.0 - 202.12.27.255]. Belonging network: 202.12.27.0/24
----> for nameserver[7] 'd.root-servers.net.' (199.7.91.13) found AS10886: [199.7.91.0 - 199.7.91.255]. Belonging network: 199.7.91.0/24
----> for nameserver[8] 'h.root-servers.net.' (198.97.190.53) found AS1508: [198.97.190.0 - 198.97.190.255]. Belonging network: 198.97.190.0/24
----> for nameserver[9] 'e.root-servers.net.' (192.203.230.10) found AS21556: [192.203.230.0 - 192.203.230.255]. Belonging network: 192.203.230.0/24
----> for nameserver[10] 'j.root-servers.net.' (192.58.128.30) found AS26415: [192.58.128.0 - 192.58.128.255]. Belonging network: 192.58.128.0/24
----> for nameserver[11] 'k.root-servers.net.' (193.0.14.129) found AS25152: [193.0.14.0 - 193.0.15.255]. Belonging network: 193.0.14.0/23
----> for nameserver[12] 'g.root-servers.net.' (192.112.36.4) found AS5927: [192.112.36.0 - 192.112.36.255]. Belonging network: 192.112.36.0/24

[...]

END IP-AS RESOLVER
```

ScriptDependenciesResolver:
```
START SCRIPT DEPENDENCIES RESOLVER
Searching script dependencies for website: google.it/doodles
******* via HTTPS *******
script[1/2]: integrity=None, src=https://ssl.google-analytics.com/ga.js
script[2/2]: integrity=None, src=https://www.google.com/doodles/js/slashdoodles__it.js
******* via HTTP *******
script[1/2]: integrity=None, src=https://ssl.google-analytics.com/ga.js
script[2/2]: integrity=None, src=https://www.google.com/doodles/js/slashdoodles__it.js

[...]

END SCRIPT DEPENDENCIES RESOLVER
```

LandingResolver for script sites:
```
START SCRIPT SITE LANDING RESOLVER
Trying to resolve landing page of script site: www.youtube.com/s/desktop/5650b92e/jsbin/webcomponents-sd.vflset/webcomponents-sd.js
***** via HTTPS *****
HTTPS Landing url: https://www.youtube.com/s/desktop/5650b92e/jsbin/webcomponents-sd.vflset/webcomponents-sd.js/
HTTPS ScriptServer: www.youtube.com/s/desktop/5650b92e/jsbin/webcomponents-sd.vflset/webcomponents-sd.js
HTTPS IP: 216.58.206.78
Strict Transport Security: False
HTTPS Redirection path:
----> [1/1]: https://www.youtube.com/s/desktop/5650b92e/jsbin/webcomponents-sd.vflset/webcomponents-sd.js/
***** via HTTP *****
HTTP Landing url: https://www.youtube.com/s/desktop/5650b92e/jsbin/webcomponents-sd.vflset/webcomponents-sd.js/
HTTP ScriptServer: www.youtube.com/s/desktop/5650b92e/jsbin/webcomponents-sd.vflset/webcomponents-sd.js
HTTP IP: 216.58.206.78
Strict Transport Security: False
HTTP Redirection path:
----> [1/1]: https://www.youtube.com/s/desktop/5650b92e/jsbin/webcomponents-sd.vflset/webcomponents-sd.js/

[...]

END SCRIPT SITE LANDING RESOLVER
```

Then DnsResolver and IpAsDatabase will execute again for script sites, then in the end:

ROVPageScraper:
```
START ROV PAGE SCRAPING
Loading page for AS2149
--> for 'c.root-servers.net.' (192.33.4.12), found row: [AS2149	192.33.4.0/24	256	US	9	UNK	]
Loading page for AS396540
!!! Found empty table in ROV page for AS number '396540'. !!!
!!! Found empty table in ROV page for AS number '396540'. !!!
!!! Found empty table in ROV page for AS number '396540'. !!!
!!! Found empty table in ROV page for AS number '396540'. !!!
!!! Found empty table in ROV page for AS number '396540'. !!!
Loading page for AS3557
--> for 'f.root-servers.net.' (192.5.5.241), found row: [AS3557	192.5.5.0/24	256	US	8	UNK	]
Loading page for AS29216
--> for 'i.root-servers.net.' (192.36.148.17), found row: [AS29216	192.36.148.0/23	256	SE	9	VLD	[Addr:192.36.148.0/23,Max:23,AS:29216]]
Loading page for AS394353
--> for 'b.root-servers.net.' (199.9.14.201), found row: [AS394353	199.9.14.0/23	0	US	9	UNK	]

[...]

END ROV PAGE SCRAPING
```

The database result ER schema is:
![alt text](res/schema_er.jpg)
 