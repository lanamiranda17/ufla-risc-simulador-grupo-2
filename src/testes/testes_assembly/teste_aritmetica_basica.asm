; Teste Aritmética Básica
; Objetivo: Carregar valores e somar
; Esperado: r1=5, r2=3, r3=8

lcl_lsb r1, 5       ; Carrega constante 5 em r1 (Opcode 15) 
lcl_lsb r2, 3       ; Carrega constante 3 em r2 (Opcode 15) 
add r3, r1, r2      ; r3 = r1 + r2 (r3 = 8) (Opcode 1) 
sub r4, r3, r2      ; r4 = r3 - r2 (r4 = 5) (Opcode 2) 
passa r5, r4        ; Copia r4 para r5 (Opcode 12) 
halt                ; Para a execução
