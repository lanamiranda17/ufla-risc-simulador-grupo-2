# ✔️ Checklist do Trabalho – Simulador UFLA-RISC

---

## 1. Implementar a estrutura do hardware

Criar representações internas para:

- Memória de **65536 palavras × 32 bits**
- **32 registradores** (32 bits cada)
- **PC** (Program Counter)
- **IR** (Instruction Register)
- **Flags**: `neg`, `zero`, `carry`, `overflow`

---

## 2. Implementar o Interpretador

O arquivo de entrada deve:

- Ler uma linha por vez
- Tratar `address <binário>`
- Posicionar instruções na memória
- Validar tamanho das instruções (32 bits)
- Armazenar tudo na memória simulada

---

## 3. Criar o ciclo do processador

Implementar as quatro etapas, em ordem:

### 🔹 IF (Instruction Fetch)
- Buscar instrução na memória
- Colocar no IR
- Incrementar PC

### 🔹 ID (Instruction Decode)
- Decodificar:
  - opcode  
  - ra  
  - rb  
  - rc  
  - imediato  
  - endereço
- Preparar operandos

### 🔹 EX/MEM (Execute / Memory)
- Executar ALU
- Acessar memória (load/store)
- Resolver branches e jumps

### 🔹 WB (Write Back)
- Gravar resultado no registrador

⚠ **O ciclo deve rodar até encontrar HALT (todos os 32 bits = 1).**

---

## 4. Implementar TODAS as instruções obrigatórias

### 🔸 ALU
- add  
- sub  
- zero  
- xor  
- or  
- not  
- and  
- asl  
- asr  
- lsl  
- lsr  
- copy  

### 🔸 Constantes e Memória
- load const 16 bits (parte alta)
- load const 16 bits (parte baixa)
- load word
- store word

### 🔸 Controle de fluxo
- jal  
- jr  
- beq  
- bne  
- jump  

### 🔸 HALT
- **32 bits = 1**

---

## 5. Criar pelo menos 8 novas instruções

- Definir opcodes
- Especificar formato
- Justificar
- Implementar
- Documentar

---

## 6. Criar a saída do simulador

O simulador deve exibir:

- Alterações nos registradores por ciclo
- Alterações na memória quando ocorrer
- Estado final dos registradores
- Estado final da memória modificada

---

## 7. Criar testes

Testes essenciais:

- Teste para cada instrução isolada
- Teste de loop com branch
- Teste de função com jal/jr
- Teste de load e store
- Teste de HALT
- Testes com programinhas reais (ex.: soma, multiplicação, repetição)

---

## 8. Montar a documentação

Deve conter:

- Resumo da máquina simulada
- Decisões de implementação
- Novas instruções criadas
- Tutorial de uso do simulador
- Descrição das estruturas internas
- Datapath (diagrama simples)
- Exemplos de execução
- Lista de testes
- Como rodar
- Link do GitHub

---

## 9. Criar arquivos de exemplo

- Programas simples em binário
- Programas com `address`
- Exemplos com múltiplos saltos

---
