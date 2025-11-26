# ...existing code...
import os

class ProgramLoader:
    """Carrega programas compilados (.bin) na memória do processador."""
    
    def __init__(self, caminho_bin: str):
        self.caminho_bin = caminho_bin
        self.instrucoes = []
        self.endereco_inicio = None
    
    def carregar(self):
        """Lê o arquivo .bin e extrai instruções e endereços."""
        if not os.path.exists(self.caminho_bin):
            raise FileNotFoundError(f"Arquivo {self.caminho_bin} não encontrado")
        
        with open(self.caminho_bin, "r") as f:
            linhas = f.readlines()
        
        i = 0
        while i < len(linhas):
            linha = linhas[i].strip()
            
            if linha.startswith("address"):
                endereco_bin = linha.split()[1]
                endereco = int(endereco_bin, 2)
                
                if i + 1 < len(linhas):
                    instrucao_bin = linhas[i + 1].strip()
                    self.instrucoes.append({
                        'endereco': endereco,
                        'instrucao': instrucao_bin
                    })
                    if self.endereco_inicio is None:
                        self.endereco_inicio = endereco
                    i += 2
                else:
                    i += 1
            else:
                i += 1
        
        return self.instrucoes
    
    def carregar_na_memoria(self, memoria):
        """Carrega as instruções na memória do processador usando Memoria.store/load."""
        if not self.instrucoes:
            self.carregar()
        
        for item in self.instrucoes:
            endereco = item['endereco']
            instrucao_bin = item['instrucao']
            valor = int(instrucao_bin, 2) & 0xFFFFFFFF
            
            # Usa store() da sua classe Memoria
            if hasattr(memoria, 'store'):
                memoria.store(endereco, valor)
            elif hasattr(memoria, 'write'):
                memoria.write(endereco, valor)
            elif hasattr(memoria, '__setitem__'):
                memoria[endereco] = valor
            else:
                raise AttributeError(f"Memoria não tem método de escrita. Métodos disponíveis: {dir(memoria)}")
        
        return self.endereco_inicio if self.endereco_inicio is not None else 0
