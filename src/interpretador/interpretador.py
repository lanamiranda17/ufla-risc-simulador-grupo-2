# interpretador.py

from typing import List
import re

# ------------------------------
# Dicionário de instruções
# ------------------------------
INSTRUCOES = {
    # Instruções Originais
    "add": "00000001",
    "sub": "00000010",
    "zeros": "00000011",
    "xor": "00000100",
    "or": "00000101",
    "not": "00000110",
    "and": "00000111",
    "asl": "00001000",
    "asr": "00001001",
    "lsl": "00001010",
    "lsr": "00001011",
    "passa": "00001100",
    "lcl_msb": "00001110",  # Carrega 16 bits mais significativos
    "lcl_lsb": "00001111",  # Carrega 16 bits menos significativos
    "load": "00010000",
    "store": "00010001",
    "jal": "00010010",  # jump and link
    "jr": "00010011",  # jump register
    "beq": "00010100",  # jump se igual
    "bne": "00010101",  # jump se diferente
    "j": "00010110",  # jump incondicional
    "loadi": "00011000",  # Carrega imediato (opcional do interpretador original)
    "halt": "11111111",

    # --- NOVAS INSTRUÇÕES EXTRAS ---
    "mul": "00010111",    # Opcode 23
    "div": "00011000",    # Opcode 24
    "mod": "00011001",    # Opcode 25
    "neg": "00011010",    # Opcode 26
    "inc": "00011011",    # Opcode 27
    "dec": "00011100",    # Opcode 28
    "bgt": "00011101",    # Opcode 29 (Branch >)
    "blt": "00011110"     # Opcode 30 (Branch <)
}

# ------------------------------
# Funções Auxiliares
# ------------------------------
def _to_bin(valor: int, bits: int) -> str:
    """Converte valor inteiro para binário com número fixo de bits."""
    return f"{valor:0{bits}b}"

def _parse_operand(operand: str) -> int:
    """Converte operando para inteiro, suportando hex, bin e decimal."""
    operand = operand.strip()
    if operand.startswith("0b"):
        return int(operand, 2)
    elif operand.startswith("0x"):
        return int(operand, 16)
    elif operand.startswith("r"):  # Considerando registrador como 'r'
        return int(operand[1:])
    return int(operand)

def montar_instrucao(asm: str) -> str:
    """Recebe uma linha de assembly e retorna uma string binária de 32 bits."""
    # Remove comentários e espaços
    asm = asm.split(";")[0].strip()
    if not asm: return ""

    partes = [t for t in re.split(r'[,\s]+', asm) if t]
    mnemonic = partes[0].lower()
    args = partes[1:]

    if mnemonic not in INSTRUCOES:
        raise ValueError(f"Mnemonico desconhecido: {mnemonic}")

    opcode = INSTRUCOES[mnemonic]
    ra = rb = rc = 0
    const16 = end24 = 0

    # 1. Instruções com 3 Registradores
    if mnemonic in ["add", "sub", "xor", "or", "and", "asl", "asr", "lsl", "lsr", 
                    "mul", "div", "mod"]:
        rc = _parse_operand(args[0])
        ra = _parse_operand(args[1])
        rb = _parse_operand(args[2])

    elif mnemonic == "zeros":
        rc = _parse_operand(args[0])

    # 2. Instruções com 2 Registradores
    elif mnemonic in ["passa", "neg", "inc", "dec"]:
        rc = _parse_operand(args[0])
        ra = _parse_operand(args[1])

    elif mnemonic in ["lcl_msb", "lcl_lsb"]:
        rc = _parse_operand(args[0])
        const16 = _parse_operand(args[1])

    elif mnemonic in ["load", "store"]:
        rc = _parse_operand(args[0])
        ra = _parse_operand(args[1])

    # 3. Jumps Incondicionais (Usam 24 bits)
    elif mnemonic in ["jal", "j"]:
        end24 = _parse_operand(args[0])

    elif mnemonic == "jr":
        rc = _parse_operand(args[0])

    # 4. Branches Condicionais (CORREÇÃO AQUI)
    # O endereço vai em RC (8 bits), pois RA e RB ocupam espaço
    elif mnemonic in ["beq", "bne", "bgt", "blt"]:
        ra = _parse_operand(args[0])
        rb = _parse_operand(args[1])
        rc = _parse_operand(args[2]) # <--- MUDADO: Usa RC para o endereço

    elif mnemonic == "halt":
        pass

    # Monta o binário
    if mnemonic in ["lcl_msb", "lcl_lsb"]:
        return opcode + _to_bin(const16, 16) + _to_bin(rc, 8)
    elif mnemonic in ["jal", "j"]:
        return opcode + _to_bin(end24, 24)
    else:
        # Branchs condicionais caem aqui agora, usando opcode+ra+rb+rc(endereço)
        return opcode + _to_bin(ra, 8) + _to_bin(rb, 8) + _to_bin(rc, 8)

# ------------------------------
# Função principal de montagem de arquivo
# ------------------------------

def montar_arquivo_assembly(caminho_asm: str, caminho_bin_out: str) -> None:
    """
    Lê um arquivo em assembly (sem 'address') e gera um arquivo .bin
    com a diretiva address para cada instrução gerada.
    """
    endereco = 0
    try:
        with open(caminho_asm, "r") as fin, open(caminho_bin_out, "w") as fout:
            for raw in fin:
                linha = raw.strip()
                if not linha:
                    continue

                bits = montar_instrucao(linha)
                if bits:
                    fout.write(f"address {endereco:08b}\n")
                    fout.write(bits + "\n")
                    endereco += 1  # Próximo endereço na memória
        print(f"Arquivo {caminho_bin_out} gerado com sucesso!")
    except Exception as e:
        print(f"Erro ao processar os arquivos: {e}")
        
if __name__ == "__main__":
    # Caminho do arquivo assembly
    caminho_asm = "programa.asm"  # Arquivo de entrada
    caminho_bin = "programa.bin"  # Arquivo de saída
    
    try:
        montar_arquivo_assembly(caminho_asm, caminho_bin)
        print(f"✓ Assembly compilado com sucesso!")
        print(f"✓ Arquivo gerado: {caminho_bin}")
    except FileNotFoundError:
        print(f"✗ Erro: Arquivo '{caminho_asm}' não encontrado")
    except Exception as e:
        print(f"✗ Erro durante compilação: {e}")
