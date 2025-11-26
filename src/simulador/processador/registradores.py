class Registradores:
    def __init__(self):
        self.regs = [0] * 32

    # LER registrador
    def load(self, indice):
        return self.regs[indice]

    # ESCREVER registrador
    def write(self, indice, valor):
        self.regs[indice] = valor & 0xFFFFFFFF
