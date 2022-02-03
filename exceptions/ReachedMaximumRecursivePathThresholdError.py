class ReachedMaximumRecursivePathThresholdError(Exception):
    message: str
    for_param: str or int

    def __init__(self, domain_name: str):      # str --> a ip address. int --> an as number.
        temp = f"Reached maximum number of recursive invocation for path resolution of domain name: {domain_name}"
        self.for_param = domain_name
        self.message = temp
        BaseException.__init__(self, temp)

    def __str__(self):
        return f'{self.message}'
