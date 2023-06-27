from keyword import kwlist
import json

def fact(n):
    if n <= 1:
        return 1

    return n * fact(n - 1)    


     
# ================================== Auto Completetions =============== #
class AutoCompleter:
    def __init__(self, options):
        self.options = options
        self.matches = []
    
    def complete(self, word, state):
        if state == 0:
            if word:
                self.matches = [option for option in self.options if option and option.startswith(word)]
            else:
                self.matches = []
        
        return self.matches



def main():
    options = kwlist + dir(__builtins__)
    print(options)
    completer = AutoCompleter(options)
    kw = {}
    kw["py_builtins"] = options
    with open("data/plugins/IntelliSense/dataset.json", "w") as file:
        json.dump(kw, file)

if __name__ == "__main__":
    main()