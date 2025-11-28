; Teste Memória
; Objetivo: Escrever e ler da memória RAM

address 0           ; Define início do código no endereço 0 

lcl_lsb r1, 10      ; r1 = 10 (Endereço de memória)
lcl_lsb r2, 99      ; r2 = 99 (Valor a ser guardado)

store r1, r2        ; Mem[r1] = r2 -> Mem[10] = 99 
load r3, r1         ; r3 = Mem[r1] -> r3 deve virar 99 

halt
