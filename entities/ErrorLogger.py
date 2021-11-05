class ErrorLogger:
    logs = list()

    def __init__(self):
        pass

    def add_entry(self, entry):
        self.logs.append(entry)

    # TODO
    def write_to_file(self):
        name = "todo"
        try:
            fhand = open(name, "a")
            if len(self.logError) == 0:
                print("No error occurred")
                return
            for each in self.logError:
                line = each["Domain"] + "," + each["Description"] +"\n"
                fhand.write(line)
            fhand.close()
        except:
            print("Error in opening file: ", name)
            return
