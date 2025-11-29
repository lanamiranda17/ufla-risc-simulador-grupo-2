; Teste: Memória RAM
; Objetivo: Gravar na memória e ler de volta
; Resultado esperado: R3 deve terminar com o valor 123

lcl_lsb r1, 100     ; R1 = 100 (Este será o Endereço de Memória)
lcl_lsb r2, 123     ; R2 = 123 (Este será o Dado)

store r1, r2        ; Mem[100] = 123

zeros r2            ; Zera R2 para garantir que não estamos roubando
load r3, r1         ; R3 = Mem[100] (Deve carregar 123)

halt
