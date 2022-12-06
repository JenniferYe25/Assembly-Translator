import ast

LabeledInstruction = tuple[str, str]


class TopLevelProgram(ast.NodeVisitor):
    """We supports assignments and input/print calls"""

    def __init__(self, entry_point, vars) -> None:
        super().__init__()
        self.functions = list()
        self.instructions = list()
        self.record_instruction('NOP1', label=entry_point)
        self.should_save = True
        self.current_variable = None
        self.elem_id = 0
        self.vars = vars

    def finalize(self):
        self.instructions.append((None, '.END'))
        return (self.instructions, self.functions)

    ####
    # Handling Assignments (variable = ...)
    ####

    def visit_Assign(self, node):
        # remembering the name of the target
        self.current_variable = self.rename(node.targets[0].id)
        # visiting the left part, now knowing where to store the result
        self.visit(node.value)
        if self.should_save:
            self.record_instruction(f'STWA {self.current_variable},d')
        else:
            self.should_save = True
        self.current_variable = None

    def visit_Constant(self, node):
        self.record_instruction(f'LDWA {node.value},i')

    def visit_Name(self, node):
        self.record_instruction(f'LDWA {node.id},d')

    def visit_BinOp(self, node):
        self.access_memory(node.left, 'LDWA')
        if isinstance(node.op, ast.Add):
            self.access_memory(node.right, 'ADDA')
        elif isinstance(node.op, ast.Sub):
            self.access_memory(node.right, 'SUBA')
        else:
            raise ValueError(f'Unsupported binary operator: {node.op}')

    def visit_Call(self, node):
        match node.func.id:
            case 'int':
                # Let's visit whatever is casted into an int
                self.visit(node.args[0])
            case 'input':
                # We are only supporting integers for now
                self.record_instruction(f'DECI {self.current_variable},d')
                self.should_save = False  # DECI already save the value in memory
            case 'print':
                # We are only supporting integers for now
                self.record_instruction(f'DECO {node.args[0].id},d')
            case _:
                self.record_instruction(f'CALL {node.func.id}')

    ####
    # Handling While loops (only variable OP variable)
    ####

    def visit_While(self, node, loop_id=''):
        loop_id = self.identify()
        inverted = self.conditons()
        # left part can only be a variable
        self.access_memory(node.test.left, 'LDWA', label=f't_{loop_id}')
        # right part can only be a variable
        self.access_memory(node.test.comparators[0], 'CPWA')
        # Branching is condition is not true (thus, inverted)
        self.record_instruction(
            f'{inverted[type(node.test.ops[0])]} end_l_{loop_id}')
        # print(node.body)
        # Visiting the body of the loop
        for contents in node.body:
            self.visit(contents)
        self.record_instruction(f'BR t_{loop_id}')
        # Sentinel marker for the end of the loop
        self.record_instruction(f'NOP1', label=f'end_l_{loop_id}')

    def visit_If(self, node):
        loop_id = self.identify()
        inverted = self.conditons()
        self.access_memory(node.test.left, 'LDWA', label=f'if_{loop_id}')
        self.access_memory(node.test.comparators[0], 'CPWA')

        if hasattr(node, 'orelse') and node.orelse != []:
            if ast.If in [type(i) for i in node.orelse]:  # there is an else if
                self.record_instruction(
                    f'{inverted[type(node.test.ops[0])]} if_{loop_id + 1}')
                for contents in node.body:
                    self.visit(contents)
                self.record_instruction(f'BR end_{loop_id}')
            else:  # there is an else
                self.record_instruction(
                    f'{inverted[type(node.test.ops[0])]} else_{loop_id}')
                for contents in node.body:
                    self.visit(contents)
                self.record_instruction(f'BR end_{loop_id}')

                self.record_instruction(f'NOP1', label=f'else_{loop_id}')
            for contents in node.orelse:
                self.visit(contents)
        else:
            self.record_instruction(f'BR end_{loop_id}')

        self.record_instruction(f'NOP1', label=f'end_{loop_id}')

    ####
    # Not handling function calls
    ####

    def visit_FunctionDef(self, node):
        """We do not visit function definitions, they are not top level"""
        self.functions.append((node.name, node))

    ####
    # Helper functions to
    ####

    def record_instruction(self, instruction, label=None):
        self.instructions.append((label, instruction))

    def access_memory(self, node, instruction, label=None):
        if isinstance(node, ast.Constant):
            self.record_instruction(f'{instruction} {node.value},i', label)
        else:
            self.record_instruction(
                f'{instruction} {self.rename(node.id)},d', label)

    def identify(self):
        result = self.elem_id
        self.elem_id = self.elem_id + 1
        return result

    def conditons(self):
        inverted = {
            ast.Lt:  'BRGE',  # '<'  in the code means we branch if '>='
            ast.LtE: 'BRGT',  # '<=' in the code means we branch if '>'
            ast.Gt:  'BRLE',  # '>'  in the code means we branch if '<='
            ast.GtE: 'BRLT',  # '>=' in the code means we branch if '<'
            ast.NotEq: 'BREQ',  # '!=' in the code means we branch if '=='
            ast.Eq: 'BRNE',  # '==; in the code means we branch if '!='
        }
        return inverted

    def rename(self, name):
        if (name in self.vars):
            return self.vars.get(name)
        else:
            return name
