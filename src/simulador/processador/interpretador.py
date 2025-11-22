# interpretador.py
# Simulador UFLA-RISC - Carregador de instruções de um arquivo em binário


import os
from memoria import Memoria

class InterpretadorUFLARISC:
    def __init__(self):
        self.memoria = Memoria()

    def carregar_arquivo_instrucoes(self, caminho_arquivo):
        endereco_atual = 0
        with open(caminho_arquivo, 'r') as f:
            for linha in f:
                linha = linha.strip()
                if not linha:
                    continue
                if linha.startswith('address'):
                    partes = linha.split()
                    if len(partes) == 2:
                        endereco_atual = int(partes[1], 2)
                elif all(c in '01' for c in linha):
                    # instrução binária
                    instr_int = int(linha, 2)  # armazena como inteiro de 32 bits
                    self.memoria.store(endereco_atual, instr_int)
                    endereco_atual += 1
                # ignora linhas inválidas


    def formato_saida(self, intervalo=None):
        print('MEMORIA FINAL:')
        if intervalo is None:
            # imprime todos os endereços não nulos
            for i, valor in enumerate(self.memoria.dados):
                if valor != 0:
                    print(f'{i}: {valor:032b}')
        else:
            # imprime apenas o intervalo solicitado
            for i in intervalo:
                valor = self.memoria.load(i)
                print(f'{i}: {valor:032b}')


if __name__ == "__main__":
    arquivo = 'instrucoes.txt'  
    cpu = InterpretadorUFLARISC()
    if os.path.exists(arquivo):
        cpu.carregar_arquivo_instrucoes(arquivo)
        cpu.formato_saida()
    else:
        print(f'Arquivo {arquivo} não encontrado.')
