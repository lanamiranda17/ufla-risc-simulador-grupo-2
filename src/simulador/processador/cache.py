# src/simulador/processador/cache.py

class CacheL1:
    def __init__(self, memoria_principal, nome="Cache L1"):
        """
        Inicializa a Cache L1.
        :param memoria_principal: Referência para o objeto Memoria (RAM)
        :param nome: Identificador para logs (ex: "Cache Instruções")
        """
        self.memoria = memoria_principal
        self.nome = nome
        # Dicionário para simular as linhas da cache: {endereco: valor}
        # Em uma simulação real, teríamos tags, sets, valid bits, etc.
        # Aqui, usamos um mapeamento direto simples para fins funcionais.
        self.linhas = {}
        self.hits = 0
        self.misses = 0

    def load(self, endereco):
        """Lê um valor da cache. Se não existir (Miss), busca na RAM."""
        if endereco in self.linhas:
            # Cache Hit: Retorna o valor armazenado na cache
            # print(f"[{self.nome}] HIT no endereço {endereco}") # (Opcional: Log de Hit)
            self.hits += 1
            return self.linhas[endereco]
        else:
            # Cache Miss: Busca na Memória Principal
            # print(f"[{self.nome}] MISS no endereço {endereco}") # (Opcional: Log de Miss)
            self.misses += 1
            valor = self.memoria.load(endereco)
            self.linhas[endereco] = valor # Atualiza a cache
            return valor

    def store(self, endereco, valor):
        """Escreve um valor (Write-Through: Cache + RAM)."""
        # Atualiza a cache
        self.linhas[endereco] = valor
        # Atualiza a memória principal imediatamente (Write-Through)
        self.memoria.store(endereco, valor)
        # print(f"[{self.nome}] WRITE no endereço {endereco} -> {valor}")

    def get_stats(self):
        return f"{self.nome} - Hits: {self.hits}, Misses: {self.misses}"