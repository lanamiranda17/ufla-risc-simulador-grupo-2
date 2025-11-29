; === Teste: ALU básica (add, sub, and, or, xor, zeros, not, shifts) ===

; Carrega constantes simples
lcl_lsb r1, 10          ; r1 = 10
lcl_lsb r2, 20          ; r2 = 20

; Operações aritméticas
add r3, r1, r2          ; r3 = 10 + 20 = 30
sub r4, r2, r1          ; r4 = 20 - 10 = 10

; Operações lógicas
and r5, r1, r2          ; r5 = 10 & 20 = 8
or  r6, r1, r2          ; r6 = 10 | 20 = 30
xor r7, r1, r2          ; r7 = 10 ^ 20 = 22

; Zerar e negar
zeros r8                ; r8 = 0
not r9, r8              ; r9 = ~0 = 0xFFFFFFFF (-1 em complemento de dois)

; Shifts lógicos
lcl_lsb r10, 1          ; r10 = 1 (quantidade de shift)
lsl r11, r1, r10        ; r11 = 10 << 1 = 20
lsr r12, r2, r10        ; r12 = 20 >> 1 = 10

; Teste de 'passa' (cópia de registrador)
passa r13, r3           ; r13 = r3 = 30

halt

; --- GABARITO ESPERADO ---
; R1  = 10
; R2  = 20
; R3  = 30      ; add
; R4  = 10      ; sub
; R5  = 8       ; and
; R6  = 30      ; or
; R7  = 22      ; xor
; R8  = 0       ; zeros
; R9  = 0xFFFFFFFF (-1) ; not 0
; R10 = 1       ; quantidade de shift
; R11 = 20      ; 10 << 1
; R12 = 10      ; 20 >> 1
; R13 = 30      ; cópia de R3