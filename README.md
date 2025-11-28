# UFLA-RISC Simulador (Grupo 2)

> **Simulador funcional do processador 32-bits UFLA-RISC**

Um simulador funcional escrito em Python que interpreta binários para o conjunto de instruções do processador UFLA-RISC de 32 bits, visando servir como projeto acadêmico da disciplina de Arquitetura de Computadores II.

---
## Visão Geral

O **UFLA-RISC Simulador** implementa um processador hipotético chamado UFLA-RISC (32 bits) e permite carregar e executar programas compilados para esse ISA. O simulador lê arquivos binários e simula sua execução, interpretando instruções, modificando registradores e memória conforme o comportamento definido pela arquitetura.

---

## Objetivo

O projeto foi desenvolvido como parte da disciplina de Arquitetura de Computadores II da Universidade Federal de Lavras (UFLA). 

## Como Usar

### Pré-requisitos
> ⚠️ Certifique-se de ter **Python** instalado.

### Passo a Passo

```bash
# 1. Clone o repositório
git clone https://github.com/lanamiranda17/ufla-risc-simulador-grupo-2.git

# 2. Entre na pasta do projeto
cd ufla-risc-simulador-grupo-2/
```

- **Escreva seu código:** Abra o arquivo localizado em `src/interpretador/programa.asm`. Apague o conteúdo existente e cole ou escreva o seu código Assembly neste arquivo. Na pasta `src/testes/testes_assembly` possui vários arquivos '.asm' que podem ser utilizados como conteúdo para teste, apenas copie e cole dentro de `programa.asm`.

  - Nota: O simulador sempre lerá o código deste arquivo específico.

- **Execute o simulador:** Na raiz do projeto, execute o arquivo principal:
```bash
python src/main.py
```

- **Verifique a Saída:** O terminal exibirá: 
  - Confirmação da compilação (`.asm` -> `.bin`).
  - Logs ciclo a ciclo da execução (Fetch/Decode).
  - Estado final dos registradores e memória.

### Exemplo de saída (conteúdo do arquivo 'teste_sub.asm'):
<img width="1302" height="831" alt="image" src="https://github.com/user-attachments/assets/b0a4c1a7-5765-4ca0-9390-d88b5795c507" />

---

## Integrantes

- Lana da Silva Miranda
- Fábio Damas Valim
- Guilherme Lirio Miranda
- Marcos Vinícius Pereira
- Arthur Soares Marques

---
