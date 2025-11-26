class Memoria:
    def __init__(self):
        self.dados = [0] * 65536

    def load(self, endereco):
        return self.dados[endereco]

    def store(self, endereco, valor):
        self.dados[endereco] = valor & 0xFFFFFFFF
