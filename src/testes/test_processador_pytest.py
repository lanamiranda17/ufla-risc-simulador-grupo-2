import sys
import os

# Garante que a pasta `src` esteja no caminho de import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulador.processador.processador_main import Processador


def test_memoria_store_load():
    cpu = Processador()

    cpu.memoria.store(0, 123)
    assert cpu.memoria.load(0) == 123
