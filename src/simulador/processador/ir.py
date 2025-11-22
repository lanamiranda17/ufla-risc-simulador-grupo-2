class IR:                       # Instruction Register
    def __init__(self):
        self.instrucao = 0

    def carregar(self, valor):
        self.instrucao = valor & 0xFFFFFFFF # Mesma lógica anterior
