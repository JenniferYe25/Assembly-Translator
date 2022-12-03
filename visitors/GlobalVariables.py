import ast
from itertools import permutations
import string

class GlobalVariableExtraction(ast.NodeVisitor):
    """ 
        We extract all the left hand side of the global (top-level) assignments
    """

    def __init__(self) -> None:
        super().__init__()
        self.results = set()
        self.vars = set()
        self.gen = self.get_name()

    def visit_Assign(self, node):
        if len(node.targets) != 1:
            raise ValueError("Only unary assignments are supported")

        var = node.targets[0].id

        if (len(var)> 8 ):  #checks if the variable name is greater than 8 characters long
            name = self.get_next()
            if (var[0] == '_'): #preserves constant naming convention
                if len(name) > 8:
                    var = var[0]+(name[:-1]).upper()
                else:
                    var = var[0]+name.upper()
            else:
                var = name
                  
        self.vars.add(var)
        node.targets[0].id = var

        if hasattr(node.value, 'value'):
            self.results.add((node.targets[0].id, node.value.value))
        else:
            self.results.add(node.targets[0].id)

    def visit_FunctionDef(self, node):
        """We do not visit function definitions, they are not global by definition"""
        pass
    
    def get_name(self):
        i = 0  # length of new rename
        possible = []

        while i <= 8:
            for p in possible:
                yield ''.join(p)
            i += 1
            possible = permutations(string.ascii_lowercase, i)  #only permutate all the possible names of length n

    def get_next(self):
        next_name = next(self.gen)
        while (next_name in self.vars):
            next_name = next(self.gen)

        return next_name