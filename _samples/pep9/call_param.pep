         BR      program
_UNIV:   .WORD 42
x:       .BLOCK 2
; *** my_func(value) -> void
; local variable:
value:   .EQUATE 2 
result:  .EQUATE 0
my_func: LDWA value, s
         ADDA _UNIV, d
         STWA result, d
         DECO result, d
         RET
program: DECI x, d
         LDWA x, d
         STWA 0, s 
         CALL my_func
         .END