class ErrorLogger:
    logs = list()

    def __init__(self):
        pass

    def add_entry(self, entry):
        self.logs.append(entry)

    def write_to_file(self):
        pass
