; Teste ZEROS
; Objetivo: Carregar um valor e depois apaga-lo
; Resultado esperado: r1 termina com 0

lcl_lsb r1, 255     ; Coloca 255 no r1 (enche de 1s os 8 bits baixos)
zeros r1            ; Zera o r1 
halt                ; Fim
