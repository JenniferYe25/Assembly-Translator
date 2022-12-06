import argparse
import ast
from generators.FunctionEntry import FunctionEntry
from visitors.FunctionVariables import LocalVariableExtraction
from visitors.GlobalVariables import GlobalVariableExtraction
from visitors.TopLevelProgram import TopLevelProgram
from visitors.FunctionCalls import FunctionalLevel
from generators.StaticMemoryAllocation import StaticMemoryAllocation
from generators.EntryPoint import EntryPoint
from generators.TempMemory import TempMemoryAllocation

def main():
    input_file, print_ast = process_cli()
    with open(input_file) as f:
        source = f.read()
    node = ast.parse(source)
    if print_ast:
        print(ast.dump(node, indent=2))
    else:
        process(input_file, node)
    
def process_cli():
    """"Process Command Line Interface options"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', help='filename to compile (.py)')
    parser.add_argument('--ast-only', default=False, action='store_true')
    args = vars(parser.parse_args())
    return args['f'], args['ast_only']

def process(input_file, root_node):
    print(f'; Translating {input_file}')
    extractor = GlobalVariableExtraction()
    extractor.visit(root_node)
    memory_alloc = StaticMemoryAllocation(extractor.results)
    print('; Branching to top level (tl) instructions')
    print('\t\tBR tl')
    memory_alloc.generate()

    top_level = TopLevelProgram('tl', extractor.vars)
    top_level.visit(root_node)
    tlInstruct, funcDef = top_level.finalize()

    proerties = LocalVariableExtraction(extractor.vars)
    proerties.visit(funcDef[0][1])
  
    fInstruct = []
    for f in funcDef:
        functional_level = FunctionalLevel(f[0], extractor.vars, proerties.local, proerties.re)
        local_alloc = TempMemoryAllocation(proerties.local, proerties.args, proerties.re, f[0])
        local_alloc.generate()  # generating local vars, args and return
        for node in f[1].body: #translating function body
            functional_level.visit(node)
        # fInstruct = fInstruct + functional_level.finalize()
        fe = FunctionEntry( functional_level.finalize(), f[0]) 
        fe.generate()  # printing body before top level  
    
    ep = EntryPoint(tlInstruct)
    ep.generate() 

if __name__ == '__main__':
    main()
