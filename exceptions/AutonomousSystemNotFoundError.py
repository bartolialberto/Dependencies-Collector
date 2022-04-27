from typing import Union


class AutonomousSystemNotFoundError(Exception):
    message: str
    for_param: str or int

    def __init__(self, param: Union[str, int]):      # str --> a ip address. int --> an as number.
        if isinstance(param, str):
            temp = f"No Autonomous System found for IP address: {param}."
        else:
            temp = f"No Autonomous System found for AS number: {str(param)}."
        self.for_param = param
        self.message = temp
        BaseException.__init__(self, temp)

    def __str__(self):
        return f'{self.message}'
