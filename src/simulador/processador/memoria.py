class Memoria: #Representação da RAM
    def __init__(self):
        self.dados = [0] * 65536 #2^16 endereços: cada posição representa uma palavra de 32 bits

    def load(self, endereco):
        return self.dados[endereco] #retorna o valor armazenado nessa posição da memória
    
    def store(self, endereco, valor):
        self.dados[endereco] = valor & 0xFFFFFFFF #   = 1111 1111 1111 1111 1111 1111 1111 1111  (32 bits 1)
                                                  # & = E bit a bit -> Só deixa o bit como 1 se ele for 1 nos dois números
                                                  # Máscara garante que o número 'valor' não tenha mais do que 32 bits



