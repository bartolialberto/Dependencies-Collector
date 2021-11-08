from entities.RRecord import RRecord
from entities.TypesRR import TypesRR
from utils import list_utils

r1 = RRecord("prova", TypesRR.A, ["192.168.0.2", "192.168.0.3"])
r2 = RRecord("prova", TypesRR.A, ["82.144.67.2"])
l = []
l.append(r1)
list_utils.update_element(l, r2, r2)
print("THE END")
