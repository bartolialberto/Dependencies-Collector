class NetworkNotFoundError(Exception):
    message: str
    for_ip: str

    def __init__(self, ip: str):      # str --> a ip address. int --> an as number.
        temp = f"No network found for address {ip}."
        self.for_param = ip
        self.message = temp
        BaseException.__init__(self, temp)

    def __str__(self):
        return f'{self.message}'
