import ipaddress
from pathlib import Path
from entities.IpAsDatabase import IpAsDatabase
from exceptions.AutonomousSystemNotFoundError import AutonomousSystemNotFoundError
from exceptions.FileWithExtensionNotFoundError import FileWithExtensionNotFoundError
from utils import file_utils, network_utils

prova_file = file_utils.set_file_in_folder(Path.cwd().parent, "prova", "prova.txt")
with open(str(prova_file), 'w') as f:  # 'w' or 'x'
    f.write(f"PROVA")
    f.close()

print("END")
