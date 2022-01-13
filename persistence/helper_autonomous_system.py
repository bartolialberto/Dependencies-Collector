from persistence.BaseModel import AutonomousSystemEntity


def insert(as_number: int) -> AutonomousSystemEntity:
    ase, created = AutonomousSystemEntity.get_or_create(number=as_number)
    return ase
