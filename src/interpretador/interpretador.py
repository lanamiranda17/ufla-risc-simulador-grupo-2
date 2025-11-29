# interpretador.py

# Importa tipos para dicas de tipagem (type hinting)
from typing import List
# Importa o módulo de expressões regulares para manipulação de strings complexas
import re

# ------------------------------
# Dicionário de instruções (Instruction Set)
# ------------------------------
# Mapeia o nome mnemônico da instrução (ex: "add") para seu Opcode binário de 8 bits
INSTRUCOES = {
    # --- Instruções Aritméticas e Lógicas Básicas ---
    "add": "00000001",      # Soma
    "sub": "00000010",      # Subtração
    "zeros": "00000011",    # Zera um registrador
    "xor": "00000100",      # Ou Exclusivo (Bitwise XOR)
    "or": "00000101",       # Ou Lógico (Bitwise OR)
    "not": "00000110",      # Negação Lógica (Bitwise NOT)
    "and": "00000111",      # E Lógico (Bitwise AND)
    
    # --- Instruções de Deslocamento (Shifts) ---
    "asl": "00001000",      # Arithmetic Shift Left
    "asr": "00001001",      # Arithmetic Shift Right (preserva sinal)
    "lsl": "00001010",      # Logical Shift Left
    "lsr": "00001011",      # Logical Shift Right (preenche com 0)
    
    # --- Instruções de Movimentação de Dados ---
    "passa": "00001100",    # Copia valor de um registrador para outro
    "lcl_msb": "00001110",  # Load Constant Low - Most Significant Bits (Carrega 16 bits superiores)
    "lcl_lsb": "00001111",  # Load Constant Low - Least Significant Bits (Carrega 16 bits inferiores)
    "load": "00010000",     # Lê da Memória RAM para Registrador
    "store": "00010001",    # Escreve de Registrador para Memória RAM
    
    # --- Instruções de Controle de Fluxo (Saltos) ---
    "jal": "00010010",      # Jump and Link (Salto para função, salva retorno)
    "jr": "00010011",       # Jump Register (Retorno de função usando registrador)
    "beq": "00010100",      # Branch if Equal (Desvia se igual)
    "bne": "00010101",      # Branch if Not Equal (Desvia se diferente)
    "j": "00010110",        # Jump Incondicional (Salto direto)
    
    # --- Instruções Auxiliares e Especiais ---
    "loadi": "00011000",    # Load Imediato (Opcional/Extra)
    "halt": "11111111",     # Parada de execução (Fim do programa)

    # --- NOVAS INSTRUÇÕES EXTRAS IMPLEMENTADAS PELO GRUPO ---
    "mul": "00010111",      # Multiplicação Inteira (Opcode 23)
    "div": "00011000",      # Divisão Inteira (Opcode 24)
    "mod": "00011001",      # Módulo/Resto da Divisão (Opcode 25)
    "neg": "00011010",      # Negação Aritmética (Inverte sinal) (Opcode 26)
    "inc": "00011011",      # Incremento (+1) (Opcode 27)
    "dec": "00011100",      # Decremento (-1) (Opcode 28)
    "bgt": "00011101",      # Branch if Greater Than (Desvia se maior) (Opcode 29)
    "blt": "00011110"       # Branch if Less Than (Desvia se menor) (Opcode 30)
}

# ------------------------------
# Funções Auxiliares
# ------------------------------

def _to_bin(valor: int, bits: int) -> str:
    """Converte um número inteiro para uma string binária com largura fixa de bits."""
    # Formata o inteiro 'valor' preenchendo com zeros à esquerda até atingir 'bits' de largura
    return f"{valor:0{bits}b}"

def _parse_operand(operand: str) -> int:
    """Interpreta string de operando e converte para inteiro (suporta Decimal, Hex, Bin, Registrador)."""
    # Remove espaços em branco extras
    operand = operand.strip()
    
    # Detecta formato binário (prefixo '0b')
    if operand.startswith("0b"):
        return int(operand, 2)
    
    # Detecta formato hexadecimal (prefixo '0x')
    elif operand.startswith("0x"):
        return int(operand, 16)
    
    # Detecta notação de registrador (ex: 'r1', 'R10') e remove o 'r'
    elif operand.lower().startswith("r"):  
        return int(operand[1:])
    
    # Caso padrão: interpreta como número decimal
    return int(operand)

def montar_instrucao(asm: str) -> str:
    """
    Processa uma única linha de código Assembly e a converte para instrução de máquina (32 bits).
    Retorna uma string contendo os 32 bits (0s e 1s).
    """
    # Remove comentários (tudo após ';') e espaços em branco das extremidades
    asm = asm.split(";")[0].strip()
    
    # Se a linha estiver vazia após limpeza, retorna string vazia
    if not asm: return ""

    # Divide a linha em partes usando vírgula ou espaço como separador (regex)
    partes = [t for t in re.split(r'[,\s]+', asm) if t]
    
    # A primeira parte é sempre o mnemônico (comando) - normalizado para minúsculo
    mnemonic = partes[0].lower()
    # O restante são os argumentos (operandos)
    args = partes[1:]

    # Verifica se a instrução existe no conjunto definido
    if mnemonic not in INSTRUCOES:
        raise ValueError(f"Mnemonico desconhecido: {mnemonic}")

    # Recupera o Opcode base da instrução
    opcode = INSTRUCOES[mnemonic]
    
    # Inicializa os campos da instrução com zero
    ra = rb = rc = 0
    const16 = end24 = 0

    # --- CATEGORIA 1: Instruções com 3 Registradores (Op Destino, Origem1, Origem2) ---
    if mnemonic in ["add", "sub", "xor", "or", "and", "asl", "asr", "lsl", "lsr", 
                    "mul", "div", "mod"]:
        rc = _parse_operand(args[0]) # 1º argumento: Registrador Destino (RC)
        ra = _parse_operand(args[1]) # 2º argumento: Operando 1 (RA)
        rb = _parse_operand(args[2]) # 3º argumento: Operando 2 (RB)

    # --- CATEGORIA ESPECIAL: Zeros (Apenas destino) ---
    elif mnemonic == "zeros":
        rc = _parse_operand(args[0]) # Zera o registrador RC

    # --- CATEGORIA 2: Instruções com 2 Registradores (Op Destino, Origem) ---
    # Inclui operações unárias e movimentação. NOT foi adicionado aqui corretamente.
    elif mnemonic in ["passa", "neg", "inc", "dec", "not"]:
        rc = _parse_operand(args[0]) # Destino (RC)
        ra = _parse_operand(args[1]) # Origem (RA)

    # --- CATEGORIA 3: Carregamento de Constantes (LCL) ---
    elif mnemonic in ["lcl_msb", "lcl_lsb"]:
        rc = _parse_operand(args[0])      # Registrador alvo
        const16 = _parse_operand(args[1]) # Imediato de 16 bits

    # --- CATEGORIA 4: Acesso à Memória (Load/Store) ---
    elif mnemonic in ["load", "store"]:
        rc = _parse_operand(args[0]) # Registrador de Dados (RC)
        ra = _parse_operand(args[1]) # Registrador de Endereço (RA)

    # --- CATEGORIA 5: Jumps Incondicionais (Endereço longo) ---
    elif mnemonic in ["jal", "j"]:
        end24 = _parse_operand(args[0]) # Endereço de 24 bits

    # --- CATEGORIA 6: Jump Register (Indireto) ---
    elif mnemonic == "jr":
        rc = _parse_operand(args[0]) # Registrador contendo o endereço

    # --- CATEGORIA 7: Branches Condicionais ---
    # Estrutura: Branch Op1, Op2, Endereço
    elif mnemonic in ["beq", "bne", "bgt", "blt"]:
        ra = _parse_operand(args[0]) # Operando 1 para comparação
        rb = _parse_operand(args[1]) # Operando 2 para comparação
        rc = _parse_operand(args[2]) # Endereço de salto (armazenado no campo RC de 8 bits)

    # --- CATEGORIA 8: Halt ---
    elif mnemonic == "halt":
        pass # Não requer operandos

    # --- MONTAGEM FINAL DA STRING BINÁRIA (32 bits) ---
    
    # Formato Tipo I (Imediato 16 bits): Opcode(8) + Const(16) + Reg(8)
    if mnemonic in ["lcl_msb", "lcl_lsb"]:
        return opcode + _to_bin(const16, 16) + _to_bin(rc, 8)
    
    # Formato Tipo J (Jump Longo): Opcode(8) + Endereço(24)
    elif mnemonic in ["jal", "j"]:
        return opcode + _to_bin(end24, 24)
    
    # Formato Tipo R (Registradores): Opcode(8) + RA(8) + RB(8) + RC(8)
    # Usado pela maioria das instruções, inclusive branches condicionais (onde RC é endereço curto)
    else:
        return opcode + _to_bin(ra, 8) + _to_bin(rb, 8) + _to_bin(rc, 8)

# ------------------------------
# Função Principal de Montagem (Assembly -> Binário)
# ------------------------------

def montar_arquivo_assembly(caminho_asm: str, caminho_bin_out: str) -> None:
    """
    Lê um arquivo .asm completo e gera o arquivo .bin correspondente.
    Suporta diretiva 'address X' para criar lacunas na memória.
    """
    endereco = 0 # Contador de endereço de memória atual
    
    try:
        # Abre arquivo de entrada (leitura) e saída (escrita)
        with open(caminho_asm, "r") as fin, open(caminho_bin_out, "w") as fout:
            # Itera sobre cada linha do arquivo fonte
            for raw in fin:
                linha = raw.strip()
                
                # Ignora linhas vazias ou linhas de comentário puro
                if not linha or linha.startswith(";"):
                    continue
                
                # Limpa comentários inline para processar apenas o código
                linha_limpa = linha.split(";")[0].strip()
                if not linha_limpa:
                    continue

                # --- TRATAMENTO DA DIRETIVA ADDRESS ---
                # Permite definir manualmente o endereço de memória atual
                if linha_limpa.lower().startswith("address"):
                    partes = linha_limpa.split()
                    if len(partes) > 1:
                        # Analisa o número do endereço e atualiza o contador
                        novo_endereco = _parse_operand(partes[1])
                        endereco = novo_endereco
                    # Pula para a próxima iteração, pois 'address' não gera código binário por si só
                    continue
                
                # --- MONTAGEM DA INSTRUÇÃO ---
                # Tenta converter a linha Assembly para binário de 32 bits
                bits = montar_instrucao(linha_limpa)
                
                if bits:
                    # Escreve o cabeçalho de endereço (necessário para o loader do simulador)
                    fout.write(f"address {endereco:08b}\n")
                    # Escreve a instrução em binário
                    fout.write(bits + "\n")
                    # Incrementa o contador para a próxima posição de memória
                    endereco += 1
                    
        print(f"Arquivo {caminho_bin_out} gerado com sucesso!")
        
    except Exception as e:
        # Captura e exibe erros de compilação (sintaxe inválida, arquivo não encontrado, etc)
        print(f"Erro ao processar os arquivos: {e}")