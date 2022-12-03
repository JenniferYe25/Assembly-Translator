         BR      program     
a:       .BLOCK  2           
b:       .BLOCK  2           
program: DECI    a,d         
         DECI    b,d         
test:    LDWA    a,d         
         CPWA    b,d         
         BREQ    end         
test_if: LDWA    a,d         
         CPWA    b,d         
         BRGT    if_r        
else:    LDWA    b,d         
         SUBA    a,d         
         STWA    b,d 
         BR      test        
if_r:    LDWA    a,d         
         SUBA    b,d         
         STWA    a,d                
         BR      test        
end:     DECO    a,d         
         .END                  
