# ...existing code...
from .loader import ProgramLoader
from .memoria import Memoria
from .registradores import Registradores
from .pc import PC
from .ir import IR
from .flags import Flags

class Processador:
    def __init__(self, caminho_programa_bin: str = None):
        # Inicializar componentes
        self.memoria = Memoria()
        self.registradores = Registradores()
        self.pc = PC()
        self.ir = IR()
        self.flags = Flags()
        
        # Carregar programa se fornecido
        if caminho_programa_bin:
            self.carregar_programa(caminho_programa_bin)
        
        self.parado = False

    # helpers para lidar com nomes diferentes de métodos nas classes PC/IR
    def _pc_get(self):
        if hasattr(self.pc, "load"):
            return self.pc.load()
        if hasattr(self.pc, "obter"):
            return self.pc.obter()
        if hasattr(self.pc, "get"):
            return self.pc.get()
        # fallback: tentar atributo direto
        return getattr(self.pc, "valor", 0)

    def _pc_set(self, valor):
        if hasattr(self.pc, "read"):
            return self.pc.read(valor)
        if hasattr(self.pc, "definir"):
            return self.pc.definir(valor)
        if hasattr(self.pc, "set"):
            return self.pc.set(valor)
        if hasattr(self.pc, "write"):
            return self.pc.write(valor)
        # fallback: atribuir direto
        setattr(self.pc, "valor", valor)
        return None

    def _ir_set(self, valor):
        if hasattr(self.ir, "definir"):
            return self.ir.definir(valor)
        if hasattr(self.ir, "load"):
            return self.ir.load(valor)
        if hasattr(self.ir, "write"):
            return self.ir.write(valor)
        if hasattr(self.ir, "set"):
            return self.ir.set(valor)
        # fallback: armazenar em atributo
        setattr(self.ir, "valor", valor)
        return None

    def _ir_get(self):
        if hasattr(self.ir, "obter"):
            return self.ir.obter()
        if hasattr(self.ir, "load"):
            return self.ir.load()
        if hasattr(self.ir, "read"):
            return self.ir.read()
        if hasattr(self.ir, "get"):
            return self.ir.get()
        return getattr(self.ir, "valor", 0)

    def carregar_programa(self, caminho_programa_bin: str):
        """Carrega um programa compilado (.bin) na memória."""
        loader = ProgramLoader(caminho_programa_bin)
        endereco_inicio = loader.carregar_na_memoria(self.memoria)
        
        # Define o PC para o endereço inicial usando helper
        self._pc_set(endereco_inicio)
        
        print(f"✓ Programa carregado na memória")
        print(f"✓ Endereço inicial (PC): {endereco_inicio:08b}")
        print(f"✓ Total de instruções: {len(loader.instrucoes)}")
    
    def buscar_instrucao(self):
        """Busca a instrução na memória apontada pelo PC."""
        endereco = self._pc_get()              # usa helper para ler PC
        instrucao = self.memoria.load(endereco)
        # define IR usando helper
        self._ir_set(instrucao)
        return instrucao
    
    def decodificar(self):
        """Decodifica a instrução no IR."""
        instrucao = self._ir_get()
        opcode = (instrucao >> 24) & 0xFF
        
        return {
            'opcode': opcode,
            'instrucao_bin': f"{instrucao:032b}"
        }
    
    def executar_passo(self):
        """Executa um ciclo completo: Fetch -> Decode."""
        if self.parado:
            return False
        
        # Fetch
        self.buscar_instrucao()
        
        # Decode
        decodificado = self.decodificar()
        
        # Incrementar PC para próxima instrução usando helper
        novo_pc = (self._pc_get() + 1) & 0xFFFFFFFF
        self._pc_set(novo_pc)
        
        return decodificado
    
    def executar_programa(self):
        """Executa o programa completo."""
        print("\n=== Iniciando execução ===\n")
        
        ciclo = 0
        while not self.parado and ciclo < 1000:  # Limite de segurança
            try:
                resultado = self.executar_passo()
                if resultado:
                    print(f"Ciclo {ciclo}: Opcode={resultado['opcode']:08b}, Instrução={resultado['instrucao_bin']}")
                
                # Verificar se é HALT (11111111)
                if resultado and resultado['opcode'] == 255:
                    print("\n✓ HALT encontrado. Programa finalizado.")
                    self.parado = True
                    break
                
                ciclo += 1
            except Exception as e:
                print(f"✗ Erro na execução: {e}")
                break
        
        if ciclo >= 1000:
            print("⚠ Limite de ciclos atingido!")
    
    def estado(self):
        """Exibe o estado atual do processador."""
        print("\n=== Estado do Processador ===")
        pc_val = self._pc_get()
        ir_val = self._ir_get()
        print(f"PC: {pc_val:08b}")
        print(f"IR: {ir_val:032b}")
        print(f"Registradores: {self.registradores}")
        print(f"Flags: {self.flags}")
# ...existing code...