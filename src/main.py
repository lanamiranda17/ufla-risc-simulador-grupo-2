import sys
import os
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent))

from interpretador.interpretador import montar_arquivo_assembly
from simulador.processador.processador_main import Processador

def main():
    # Caminhos
    caminho_asm = "src/interpretador/programa.asm"
    caminho_bin = "src/interpretador/programa.bin"
    
    print("=== RISC Simulator ===\n")
    
    # Step 1: Compilar Assembly
    print("1️⃣  Compilando Assembly...")
    try:
        montar_arquivo_assembly(caminho_asm, caminho_bin)
        print("✓ Assembly compilado com sucesso!\n")
    except FileNotFoundError:
        print(f"✗ Erro: Arquivo '{caminho_asm}' não encontrado")
        return
    except Exception as e:
        print(f"✗ Erro na compilação: {e}")
        return
    
    # Step 2: Criar Processador e Carregar Programa
    print("2️⃣  Carregando programa no processador...")
    try:
        processador = Processador(caminho_bin)
        print("✓ Programa carregado!\n")
    except Exception as e:
        print(f"✗ Erro ao carregar programa: {e}")
        return
    
    # Step 3: Executar Programa
    print("3️⃣  Executando programa...\n")
    processador.executar_programa()
    
    # Step 4: Exibir Estado Final
    processador.estado()

if __name__ == "__main__":
    main()
