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

    def get_first_value(self):
        return self.values[0]

