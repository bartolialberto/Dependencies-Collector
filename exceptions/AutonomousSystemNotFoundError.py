class AutonomousSystemNotFoundError(Exception):
    message: str
    for_ip: str

    def __init__(self, ip: str):
        temp = f"No Autonomous System found for ip '{ip}'."
        self.for_ip = ip
        self.message = temp
        BaseException.__init__(self, temp)

    def __str__(self):
        return f'{self.message}'
