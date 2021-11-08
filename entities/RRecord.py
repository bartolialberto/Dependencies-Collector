from entities.TypesRR import TypesRR


class RRecord:
    name: str
    type: TypesRR
    values: list

    # qui è per ora gestito il caso ottimale ma va cambiato es se metto name che non è di un server torno errore,
    # non Ip inesistente
    def __init__(self, name: str, _type: TypesRR, values: str or list):
        self.name = name
        self.type = _type
        if isinstance(values, str):
            temp = list()
            temp.append(values)
            self.values = temp
        else:
            self.values = values

    def __eq__(self, other):
        if isinstance(other, RRecord):
            if self.name == other.name and self.type is other.type:
                return True
            else:
                return False
        else:
            return False

    def get_first_value(self) -> str:
        return self.values[0]
