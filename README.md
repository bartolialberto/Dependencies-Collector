# LavoroTesi
## Python setup
The python modules used/imported in this project:

```
dns
csv
pathlib
re
selenium
seleniumwire
ipaddress
requests
gzip
peewee
```

Make sure your python interpreter has all of them.
Probably the only modules to install for default environments are: dnspython (version >= 2.0.0), selenium, 
selenium-wire and peewee.
So you can install every one of them using pip (if present in the environment):

```
pip install dnspython==2.1.0
pip install selenium
pip install selenium-wire
pip install peewee
```

You can install them all using one command:

```
pip install selenium selenium-wire dnspython==2.0.0 peewee
```

##Configuration
To configure the application you have to:
1) Use Windows as OS
2) Have Firefox installed
3) Download geckodriver (https://github.com/mozilla/geckodriver/releases) and put the executable file in the
input folder of the application
4) You can already download the network's numbers database (https://iptoasn.com/) and put the .tsv file in the
input folder. The application will ask you to download a newer version anyway.

##Run application
The application starts executing the main.py file.
The only application input/argument is a list of domain name. You can set them in 3 ways:
1) via command line
2) via a .txt file put in the input folder
3) via shell by hand one at time

##Results
Results will be exported as files in the output folder.

##Snapshot exception mechanism
If an unwanted exception occurs, the application will notice that and will take a snapshot of the initial state of
the execution to be studied/resolved later. It will create a sub-folder (relative to the SNAPSHOTS folder) using
the current timestamp (as name) containing:
1) a .csv file of the cache before the actual elaboration occurred
2) a .txt file containing the final domain name list
3) a .txt containing the type of the exception, the result of the str(.) method used on the exception and the traceback
object print