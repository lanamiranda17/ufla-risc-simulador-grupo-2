# interpretador_de_instrucoes.py
# Responsabilidade:
# - Ler arquivo de instruções (texto binário com 'address')
# - Carregar instruções na Memoria (como int de 32 bits)
# - Decodificar uma instrução (int -> campos/nomes) para ser usada pelo processador

from typing import Dict, Optional
import os
import sys
from simulador.processador.memoria import Memoria



# Map opcode -> mnemonic
INSTRUCOES = {
    "00000001": "add",
    "00000010": "sub",
    "00000011": "zeros",
    "00000100": "xor",
    "00000101": "or",
    "00000110": "passnota",  # not
    "00000111": "and",
    "00001000": "asl",
    "00001001": "asr",
    "00001010": "lsl",
    "00001011": "lsr",
    "00001100": "passa",     # copy
    "00001110": "lcl_msb",   # load const high (bits 23-8)
    "00001111": "lcl_lsb",   # load const low
    "00010000": "load",
    "00010001": "store",
    "00010010": "jal",
    "00010011": "jr",
    "00010100": "beq",
    "00010101": "bne",
    "00010110": "j",
    "00010111": "storei",
    "00011000": "loadi",
    "00011001": "mul",
    "00011010": "div",
    "00011011": "mod",
    "00011100": "neg",
    "00011101": "inc",
    "00011110": "dec",
    "11111111": "halt",
}


def decode_instruction_int(instr_int: int) -> dict:
    bits = f"{instr_int & 0xFFFFFFFF:032b}"

    opcode = bits[0:8]             # 8 bits
    ra = bits[8:13]                # 5 bits
    rb = bits[13:18]               # 5 bits
    rc = bits[18:23]               # 5 bits

    end24 = bits[8:32]             # campo 23..0 (para j, jal)
    const16 = bits[8:24]           # campo 23..8  (para loadi, lcl, lch)

    mnemonic = INSTRUCOES.get(opcode, "unknown")

    return {
        "bits": bits,
        "opcode": opcode,
        "mnemonic": mnemonic,
        "ra": int(ra, 2),
        "rb": int(rb, 2),
        "rc": int(rc, 2),
        "end24": int(end24, 2),
        "const16": int(const16, 2),
    }



class InterpretadorDeInstrucoes:
    """
    Interpretador que:
      - carrega um arquivo de instruções no formato:
            address 0
            00011000100000000001100010000000
            ...
            address 1000001
            ...
      - grava na Memoria (como int de 32 bits)
      - permite decodificar / listar instruções
    """

    def __init__(self, memoria: Optional[Memoria] = None):
        # ou você passa a Memoria do processador, ou ele cria uma só para debug
        self.memoria = memoria if memoria is not None else Memoria()

    def carregar_arquivo(self, caminho_arquivo: str) -> None:
        """
        Lê arquivo de instruções (texto) e grava na Memoria:
        - 'address BINARIO' define o endereço atual
        - linhas de 32 bits são instruções
        """
        endereco_atual = 0

        with open(caminho_arquivo, "r") as f:
            for raw in f:
                linha = raw.strip()
                if not linha:
                    continue

                # diretiva address
                if linha.startswith("address"):
                    partes = linha.split()
                    if len(partes) >= 2:
                        endereco_atual = int(partes[1], 2)
                    continue

                # linha de instrução (32 bits)
                if all(c in "01" for c in linha):
                    instr_bits = "".join(linha.split())
                    if len(instr_bits) != 32:
                        raise ValueError(f"Instrução com tamanho != 32: '{instr_bits}'")
                    instr_int = int(instr_bits, 2)
                    self.memoria.store(endereco_atual, instr_int)
                    endereco_atual += 1
                # qualquer outra coisa é ignorada

    def decodificar_endereco(self, endereco: int) -> Optional[dict]:
        """
        Decodifica a instrução armazenada em 'endereco' da Memoria.
        Se estiver 0 (vazio), retorna None.
        """
        instr_int = self.memoria.load(endereco)
        if instr_int == 0:
            return None
        return decode_instruction_int(instr_int)

    def listar_programa(self, intervalo=None) -> None:
        """
        Imprime as instruções decodificadas.
        - Se intervalo for None: imprime apenas endereços não nulos.
        - Se intervalo for iterável (range, lista): imprime só esses endereços.
        """
        if intervalo is None:
            # percorre toda a memória; imprime só posições não vazias
            for addr, valor in enumerate(self.memoria.dados):
                if valor != 0:
                    info = decode_instruction_int(valor)
                    print(
                        f"{addr:5d}: {info['bits']}  "
                        f"{info['mnemonic']} "
                        f"ra={info['ra']} rb={info['rb']} rc={info['rc']}"
                    )
        else:
            for addr in intervalo:
                valor = self.memoria.load(addr)
                if valor == 0:
                    continue
                info = decode_instruction_int(valor)
                print(
                    f"{addr:5d}: {info['bits']}  "
                    f"{info['mnemonic']} "
                    f"ra={info['ra']} rb={info['rb']} rc={info['rc']}"
                )


