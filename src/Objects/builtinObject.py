class BuiltInFunctionObject():

    def __init__(self, ast):
        self.ast = ast['PrebuiltFunction']
        self.exec_string = ""


    def transpile(self):
        for ast in self.ast:
            try:
                if ast['type'] == "print":
                    self.exec_string += "print("
            except: pass
            try: self.exec_string += ast['arguments'][0] + ")"
            except: pass

        return self.exec_string