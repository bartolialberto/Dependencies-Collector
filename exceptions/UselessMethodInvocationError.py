class UselessMethodInvocationError(Exception):
    def __init__(self):
        BaseException.__init__(self)
