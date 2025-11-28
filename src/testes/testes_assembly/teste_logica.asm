; Teste Lógica e Shifts
; Objetivo: Testar AND, OR e Deslocamentos

lcl_lsb r1, 15      ; r1 = 15 (0000 1111)
lcl_lsb r2, 240     ; r2 = 240 (1111 0000)

; Teste Lógico
and r3, r1, r2      ; r3 = 15 AND 240 (Resultado deve ser 0) 
or r4, r1, r2       ; r4 = 15 OR 240 (Resultado deve ser 255) 
xor r5, r1, r1      ; r5 = 15 XOR 15 (Resultado deve ser 0) 

; Teste Shifts
lcl_lsb r6, 1       ; Carrega 1 para usar como quantidade de shift
lsl r7, r1, r6      ; Shift Left Lógico em r1 por 1 bit (r7 = 30) 
lsr r8, r2, r6      ; Shift Right Lógico em r2 por 1 bit (r8 = 120) 

halt
