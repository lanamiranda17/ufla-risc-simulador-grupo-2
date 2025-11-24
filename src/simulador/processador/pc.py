class PC:                       # Program Counter
    def __init__(self):
        self.valor = 0

    def load(self):
        return self.valor

    def read(self, novo_valor):
        self.valor = novo_valor & 0xFFFFFFFF # Mesma lógica da memória