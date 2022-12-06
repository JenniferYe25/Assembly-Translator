import ast


class TopLevelProgram(ast.NodeVisitor):
    """We supports assignments and input/print calls"""
    
    def __init__(self, entry_point) -> None:
        super().__init__()
        self.__instructions = list()
        self.__record_instruction('NOP1', label=entry_point)
        self.__should_save = True
        self.__current_variable = None
        self.__elem_id = 0

    def finalize(self):
        self.__instructions.append((None, '.RET'))
        return self.__instructions

    def visit_Assign(self, node):
        # remembering the name of the target
        self.__current_variable = node.targets[0].id
        # visiting the left part, now knowing where to store the result
        self.visit(node.value)
        if self.__should_save:
            self.__record_instruction(f'STWA {self.__current_variable},s')
        else:
            self.__should_save = True
        self.__current_variable = None
    
    def visit_Constant(self, node):
        self.__record_instruction(f'LDWA {node.value},i')
    
    def visit_Name(self, node):
        self.__record_instruction(f'LDWA {node.id},s')

    def visit_BinOp(self, node):
        self.__access_memory(node.left, 'LDWA')
        if isinstance(node.op, ast.Add):
            self.__access_memory(node.right, 'ADDA')
        elif isinstance(node.op, ast.Sub):
            self.__access_memory(node.right, 'SUBA')
        else:
            raise ValueError(f'Unsupported binary operator: {node.op}')

    def visit_Call(self, node):
        match node.func.id:
            case 'int': 
                # Let's visit whatever is casted into an int
                self.visit(node.args[0])
            case 'input':
                # We are only supporting integers for now
                self.__record_instruction(f'DECI {self.__current_variable},d')
                self.__should_save = False # DECI already save the value in memory
            case 'print':
                # We are only supporting integers for now
                self.__record_instruction(f'DECO {node.args[0].id},d')
            case _:
                raise ValueError(f'Unsupported function call: { node.func.id}')


    def visit_FunctionDef(self, node):
            # print(dir(node))
            # print(node.name, node.args, node.body)
            # print(node.args.args)
            function_name = node.name
            arguments = node.args.args
            
            for arg in arguments:
                self.visit(arg, count)

            self.__record_instruction(f'SUBSP {(len(arguments)+1)*2}, i', label = f'end_{function_name}')
            
            for contents in node.body:
                # print(contents)
                self.visit(contents)
            

        
    def visit_arg(self, node):
        print(node.arg)
    #     return super().visit_arg(node)
        # print(dir(arguments))
        # print(arguments)
        # print(function_name, arguments)
        # print(node.body[0])
        # body = node.body[0]
        # self.visit(body)
        # print("hello")
        # for contents in body:
            # self.visit(contents)
        # print(dir(node.body[0]))
        # print(dir(node.body[1]))
        # print(node.body[1].value)
        # print(node.body[0].args.args) #function arguments

    def __record_instruction(self, instruction, label = None):
        self.__instructions.append((label, instruction))

    def __access_memory(self, node, instruction, label = None):
        if isinstance(node, ast.Constant):
            self.__record_instruction(f'{instruction} {node.value},i', label)
        else:
            self.__record_instruction(f'{instruction} {node.id},d', label)
