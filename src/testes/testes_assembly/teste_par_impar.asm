; Teste: Par ou Ímpar
; Verifica o resto da divisão de 15 por 2.

lcl_lsb r1, 15      ; Número a ser testado
lcl_lsb r2, 2       ; Divisor (para checar paridade)

mod r3, r1, r2      ; R3 = 15 % 2
                    ; Se R3 for 1, o número é ímpar.
                    ; Se R3 for 0, o número é par.

halt
