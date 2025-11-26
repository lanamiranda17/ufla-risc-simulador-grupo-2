; filepath: c:\Users\arthu\OneDrive\Desktop\ProjetoARQ\ufla-risc-simulador-grupo-2\src\interpretador\programa.asm
; Programa simples de teste

zeros r1        ; r1 = 0
add r2, r1, r1  ; r2 = r1 + r1 = 0
lcl_msb r3, 0xFF  ; Carrega 0xFF nos 16 bits MSB de r3
halt            ; Finaliza