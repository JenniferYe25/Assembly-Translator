         BR      program     
_UNIV:   .WORD   42          
x:       .BLOCK  2           
result:  .BLOCK  2           
; *** my_func(value) -> void
; local variable:
re:      .EQUATE 0           
value:   .EQUATE 4           ; parameter
return:  .EQUATE 6           ; return value
my_func: SUBSP   2,i         ; get local
         LDWA    value,s     
         ADDA    _UNIV,d     
         STWA    re,s        
         LDWA    re,s        
         STWA    return,s       
         ADDSP   2,i         ; pop local
         RET                 
program: DECI    x,d
         SUBSP   4,i             
         LDWA    x,d      
         STWA    0,s         
         CALL    my_func     
         ADDSP   2,i         
         LDWA    0,s         
         STWA    result,d    
         ADDSP   2,i         
         DECO    result,d    
         .END                  
