import sys  
import os
# adiciona a pasta que está acima de /testes ao caminho de import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from simulador.processador.processador_main import Processador

def teste_simples():
    cpu = Processador()

    cpu.memoria.store(0, 42)
    valor_lido = cpu.memoria.load(0)
    
    print(f"Valor lido da memória: {valor_lido}")

teste_simples()
