import sys
import os

# adiciona a pasta pai (`src`) ao caminho para permitir import absoluto do pacote `simulador`
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulador.processador.processador_main import Processador


def test_simples():
    cpu = Processador()

    # Grava e lê diretamente da memória
    cpu.memoria.store(0, 42)
    valor_lido = cpu.memoria.load(0)
    assert valor_lido == 42

    # Verifica o estágio IF implementado: fetch deve carregar IR e incrementar PC
    cpu.pc.read(0)
    cpu.fetch()
    assert cpu.ir.instrucao == 42
    assert cpu.pc.load() == 1
