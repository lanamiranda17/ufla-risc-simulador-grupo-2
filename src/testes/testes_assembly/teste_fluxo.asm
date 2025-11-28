; Teste Controle de Fluxo (If/Else simulado)
; Objetivo: Pular instruções condicionalmente

address 0
lcl_lsb r1, 5       ; r1 = 5
lcl_lsb r2, 5       ; r2 = 5
lcl_lsb r3, 10      ; r3 = 10 (Alvo do salto se diferente)
lcl_lsb r4, 7       ; r4 = 7 (Alvo do salto se igual)

; Teste BEQ (Branch if Equal)
beq r1, r2, 7       ; Se r1 == r2, vá para endereço 7 
add r5, r1, r1      ; (Esta linha deve ser pulada se o BEQ funcionar)

; O salto cai aqui (Endereço 6, mas como pulamos para 7...)
address 7           ; Forçando posição para visualização
lcl_lsb r10, 1      ; Código que executa se o salto ocorrer (Flag de sucesso)

; Teste J (Jump Incondicional)
j 9                 ; Pula para o HALT no endereço 9 
lcl_lsb r11, 1      ; (Esta linha deve ser pulada pelo J)

address 9
halt
