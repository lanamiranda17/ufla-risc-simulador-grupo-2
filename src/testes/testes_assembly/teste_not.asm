; Teste NOT
; Objetivo: Inverter os bits de 0
; Resultado esperado: r2 = -1 (ou 111...111 em binário)

zeros r1            ; r1 = 0 (tudo 0)
not r2, r1          ; r2 = NOT 0 (vira tudo 1, que é -1 em complemento de 2) 
halt
