class Registradores:                # Regitradores de uso geral R0–R31
    def __init__(self):
        self.regs = [0] * 32        # Cria 32 registradores começando com 0

    def load(self, indice):
        return self.regs[indice]

    def read(self, indice, valor):
        self.regs[indice] = valor & 0xFFFFFFFF # Mesma lógica da memória
 