; Teste: Lógica e Shifts
; Objetivo: Testar AND, OR, XOR e Shifts
; Dados: R1 = 12 (1100 bin), R2 = 10 (1010 bin)
; Resultados Esperados:
; R3 (AND) = 8 (1000)
; R4 (OR)  = 14 (1110)
; R5 (XOR) = 6  (0110)
; R6 (LSL) = 48 (12 deslocado 2x a esq -> 110000)

lcl_lsb r1, 12      ; 1100
lcl_lsb r2, 10      ; 1010
lcl_lsb r7, 2       ; Auxiliar para shift (quantidade 2)

and r3, r1, r2      ; 1100 & 1010 = 1000 (8)
or  r4, r1, r2      ; 1100 | 1010 = 1110 (14)
xor r5, r1, r2      ; 1100 ^ 1010 = 0110 (6)
lsl r6, r1, r7      ; Shift Left lógico de 12 por 2 bits = 48

halt
