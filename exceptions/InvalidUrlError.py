class InvalidUrlError(Exception):
    for_domain_name: str

    def __init__(self, url: str):
        temp = f"URL '{url}' is not well-formatted for a correct URL."
        self.message = temp
        self.for_url = url
        BaseException.__init__(self, temp)

    def __str__(self):
        return f'{self.message}'
