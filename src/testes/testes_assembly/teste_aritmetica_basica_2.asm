; Teste: Aritmética Básica e Negativos
; Objetivo: Testar SOMA, SUBTRAÇÃO, MULTIPLICAÇÃO, DIVISÃO e NEGAÇÃO
; Resultado esperado no final:
; R1 = 10, R2 = 20
; R3 = 30  (10 + 20)
; R4 = -10 (10 - 20) -> Em hexa será FFFFFFF6
; R5 = 200 (10 * 20)
; R6 = 2   (20 / 10)
; R7 = -20 (neg r2)

lcl_lsb r1, 10      ; Carrega 10 em R1
lcl_lsb r2, 20      ; Carrega 20 em R2

add r3, r1, r2      ; R3 = 10 + 20 = 30
sub r4, r1, r2      ; R4 = 10 - 20 = -10
mul r5, r1, r2      ; R5 = 10 * 20 = 200
div r6, r2, r1      ; R6 = 20 / 10 = 2
neg r7, r2          ; R7 = -20

halt
