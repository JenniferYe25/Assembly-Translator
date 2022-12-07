         BR      program
_UNIV:   .WORD 42
x:       .BLOCK 2
; *** my_func(value) -> void
; local variable:
value:   .EQUATE 2 
result:  .EQUATE 0
my_func: SUBSP 4, i
         LDWA value, s
         ADDA _UNIV, d
         STWA result, d
         DECO result, d
         ADDSP 4, i
         RET
program: DECI x, d
         SUBSP 2, i
         LDWA x, d
         STWA 0, s 
         CALL my_func
         ADDSP 2, i
         .END