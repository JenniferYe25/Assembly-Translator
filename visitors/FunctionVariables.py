import ast
from itertools import permutations
from visitors.GlobalVariables import GlobalVariableExtraction
import string

class LocalVariableExtraction(GlobalVariableExtraction):
    """ 
        We extract all function arguments, local variables and 
    """

    def __init__(self, vars) -> None:
        super().__init__()
        self.local = set()  
        self.param = set() # tuple()
        self.vars = vars
        self.gen = self.get_name()
        
    def visit_Assign(self, node):
        if len(node.targets) != 1:
            raise ValueError("Only unary assignments are supported")

        var = node.targets[0].id
        if (var not in self.vars):
            if (len(var)> 8):  #checks if the variable name is greater than 8 characters long
                name = self.get_next()
                if (var[0] == '_'): #preserves constant naming convention
                    if len(name) > 8:
                        var = var[0]+(name[:-1]).upper()
                    else:
                        var = var[0]+name.upper()
                else:
                    var = name
            self.vars[node.targets[0].id] = var
                    
            node.targets[0].id = var

            if hasattr(node.value, 'value'):
                self.local.add((node.targets[0].id, node.value.value))
            else:
                self.local.add(node.targets[0].id)

    def visit_While(self, node):
        if(node.test.left.id in self.vars): # ensure iterator variables are set to 1 by default
            for var in self.local: # must iterate since set of tuples and strings
                if (type(var) is tuple) and (var[0] == node.test.left.id and var[1] < 1): 
                    self.local.remove(var)
                    self.local.add((node.test.left.id, 1))

        for contents in node.body:
            self.visit(contents)

    def visit_FunctionDef(self, node):
        arguments = node.args.args
            
        for arg in arguments:
            self.visit(arg)
        
        for contents in node.body:
            self.visit(contents)
    
    def visit_arg(self, node):
        if (var not in self.vars):
            if (len(var)> 8):  #checks if the variable name is greater than 8 characters long
                name = self.get_next()
                var = name
            self.vars[node.targets[0].id] = var
                    
            node.targets[0].id = var
        self.param.add(node.arg) 
    
    def get_name(self):
        i = 0  # length of new rename
        possible = []

        while i <= 8:
            for p in possible:
                yield ''.join(p)
            i += 1
            possible = permutations(string.ascii_uppercase, i)  #only permutate all the possible names of length n

    def get_next(self):
        next_name = next(self.gen)
        while (next_name in self.vars):
            next_name = next(self.gen)

        return next_name