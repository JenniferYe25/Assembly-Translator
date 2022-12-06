from .TopLevelProgram import TopLevelProgram
import ast

class FunctionalLevel(TopLevelProgram):
    """We supports assignments and input/print calls"""

    def __init__(self, entry_point, vars, locals) -> None:
        super().__init__(entry_point, vars)
        self.locals = locals
        self.instructions = [(entry_point,'SUBSP ' +
                                  str(len(self.locals)*2) + ', i')]

    def finalize(self):
        self.instructions.append((None, 'ADDSP ' +
                                    str(len(self.locals)*2)+', i'))
        self.instructions.append((None, '.RET'))
        return self.instructions

    def visit_Assign(self, node):
        # remembering the name of the target
        if node.targets[0].id in self.locals:
            self.current_variable = self.locals[node.targets[0].id]
        else:
            self.current_variable = node.targers[0].id

        # visiting the left part, now knowing where to store the result
        self.visit(node.value)
        if self.should_save:
            super().record_instruction(f'STWA {self.current_variable},s')
        else:
            self.should_save = True
        self.current_variable = None


    def visit_Name(self, node):
        if node.id in self.locals:
            node.id = self.locals[node.id]
        super().record_instruction(f'LDWA {node.id},s')


    def visit_Call(self, node):
        match node.func.id:
            case 'int':
                # Let's visit whatever is casted into an int
                self.visit(node.args[0])
            case 'input':
                # We are only supporting integers for now
                super().record_instruction(f'DECI {self.current_variable},d')
                self.should_save = False  # DECI already save the value in memory
            case 'print':
                # We are only supporting integers for now
                super().record_instruction(f'DECO {node.args[0].id},d')
            case _:
                raise ValueError(f'Unsupported function call: { node.func.id}')

    def access_memory(self, node, instruction, label=None):
        if isinstance(node, ast.Constant):
            self.record_instruction(f'{instruction} {node.value}, i', label)
        else:
            self.record_instruction(
                f'{instruction} {self.rename(node.id)}, s', label)
 
