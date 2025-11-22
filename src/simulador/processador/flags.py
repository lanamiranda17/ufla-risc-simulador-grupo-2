class Flags:
    def __init__(self):         # Inicia todas as flags como desligadas
        self.neg = 0                # Resultado foi negativo
        self.zero = 0               # Resultado foi zero
        self.carry = 0              # Vai um bit “a mais” em operações de soma/subtração
        self.overflow = 0           # Valor estourou o limite dos 32 bits (sinal errado)

    def reset(self):
        self.neg = self.zero = self.carry = self.overflow = 0
