#Imports da EX/MEM
from src.simulador.exmem.execute import execute_instruction
from src.simulador.exmem.memory_access import memory_access
from src.simulador.exmem.flags import update_flags   # sua função

# ...existing code...
from .loader import ProgramLoader
from .memoria import Memoria
from .registradores import Registradores
from .pc import PC
from .ir import IR
from .flags import Flags


class _MemWrapper:
    """
    Adaptador simples para permitir que memory_access use .get e [address]
    em cima da classe Memoria do grupo.
    """
    def __init__(self, memoria: Memoria):
        self._memoria = memoria

    def get(self, addr: int, default=0):
        try:
            return self._memoria.load(addr)
        except Exception:
            return default

    def __getitem__(self, addr: int):
        return self._memoria.load(addr)

    def __setitem__(self, addr: int, value: int):
        self._memoria.store(addr, value)


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



    def _mapear_opcode(self, opcode_num: int):
        """
        Converte o opcode numérico (8 bits) para:
        - mnemonic: string que o execute_instruction espera
        - mem_access: None / 'load' / 'store'

        ATENÇÃO: ajuste os valores conforme o PDF da ISA.
        """
        tabela = {
            0x01: ("add",  None),
            0x02: ("sub",  None),
            0x03: ("and",  None),
            0x04: ("or",   None),
            0x05: ("xor",  None),
            0x06: ("shift_left",  None),
            0x07: ("shift_right", None),

            # EXEMPLO – troque pelos opcodes reais do PDF:
            0x20: ("load",  "load"),
            0x21: ("store", "store"),
        }

        if opcode_num not in tabela:
            raise ValueError(f"Opcode numérico desconhecido: {opcode_num:#04x}")

        return tabela[opcode_num]        

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
        """[ID] Instruction Decode: Decodifica instrução e busca operandos."""

        # [ID] Lê a instrução do IR
        instrucao = self._ir_get()

        # ------------------------------------------------------------
        # [ID] Extrai campos usando máscaras e shifts
        # ------------------------------------------------------------
        opcode   = (instrucao >> 24) & 0xFF
        ra_idx   = (instrucao >> 16) & 0xFF
        rb_idx   = (instrucao >> 8)  & 0xFF
        rc_idx   =  instrucao        & 0xFF

        end24    = instrucao & 0xFFFFFF        # Usado para Jumps
        const16  = (instrucao >> 8) & 0xFFFF   # Usado para LCL (constantes)

        # ------------------------------------------------------------
        # [ID] Busca de operandos no banco de registradores
        # ------------------------------------------------------------
        val_ra = self.registradores.load(ra_idx) if ra_idx < 32 else 0
        val_rb = self.registradores.load(rb_idx) if rb_idx < 32 else 0

        # ------------------------------------------------------------
        # Retorna dados decodificados para o estágio EX
        # ------------------------------------------------------------
        return {
            'opcode': opcode,

            'ra_idx': ra_idx,
            'val_ra': val_ra,

            'rb_idx': rb_idx,
            'val_rb': val_rb,

            'rc_idx': rc_idx,

            'end24': end24,
            'const16': const16,

            'instrucao_bin': f"{instrucao:032b}"
        }
  
  
    def executar_passo(self):
        """
        Executa um ciclo completo:
        IF -> ID -> EX -> MEM -> WB (e atualiza FLAGS).

        Tudo que não é EX/MEM foi mantido o mais próximo possível
        do seu código original.
        """
        if self.parado:
            return False

        # ----- IF: busca instrução -----
        self.buscar_instrucao()

        # ----- ID: decodifica -----
        decodificado = self.decodificar()
        opcode_num = decodificado['opcode']

        # HALT (opcode 255): mantém o fluxo antigo (só detecta no laço)
        if opcode_num == 255:
            novo_pc = (self._pc_get() + 1) & 0xFFFFFFFF
            self._pc_set(novo_pc)
            return decodificado

        # ----- Mapeia opcode numérico -> texto + acesso à memória -----
        mnemonic, mem_access = self._mapear_opcode(opcode_num)

        # Monta instrução no formato que o execute_instruction espera
        instruction = {
            'opcode': mnemonic,                         # 'add', 'sub', ...
            'rs1': f"r{decodificado['ra_idx']}",
            'rs2': f"r{decodificado['rb_idx']}",
            'rd':  f"r{decodificado['rc_idx']}",
            'mem_access': mem_access,                   # None / 'load' / 'store'
        }

        # Snapshot dos registradores em dict, como o EX/MEM usa
        registers = {f"r{i}": self.registradores.load(i) for i in range(32)}

        # ----- EX: ALU -----
        result_alu, op_a, op_b, is_sub = execute_instruction(instruction, registers)

        # ----- MEM: acesso à memória (se load/store) -----
        mem_wrapper = _MemWrapper(self.memoria)
        mem_result = memory_access(result_alu, instruction, mem_wrapper, registers)

        # Para operações ALU, memory_access devolve o próprio result_alu.
        # Para LOAD, mem_result é o dado lido.
        # Para STORE, mem_result normalmente é None.
        final_value = mem_result if mem_result is not None else result_alu

        # ----- FLAGS: atualiza só para operações aritméticas/lógicas -----
        if mnemonic not in ['load', 'store']:
            is_logic = mnemonic in ['and', 'or', 'xor', 'not', 'shift_left', 'shift_right']
            flags_dict = update_flags(final_value, op_a, op_b, is_sub, is_logic=is_logic)

            self.flags.zero     = 1 if flags_dict.get('zero') else 0
            self.flags.neg      = 1 if flags_dict.get('negative') else 0
            self.flags.carry    = 1 if flags_dict.get('carry') else 0
            self.flags.overflow = 1 if flags_dict.get('overflow') else 0

        # ----- WB: write-back no banco de registradores -----
        # Não escreve em registrador se for STORE, e nunca escreve em r0
        if mem_access != 'store':
            rd_str = instruction['rd']       # ex: 'r3'
            try:
                rd_idx = int(rd_str[1:])    # 'r3' -> 3
            except ValueError:
                rd_idx = None

            if rd_idx is not None and rd_idx != 0:
                # No seu Registradores, "read" é o método que escreve
                self.registradores.read(rd_idx, final_value & 0xFFFFFFFF)

        # ----- PC: incrementa para próxima instrução -----
        novo_pc = (self._pc_get() + 1) & 0xFFFFFFFF
        self._pc_set(novo_pc)

        # Mantém o retorno antigo (dados decodificados) para o executar_programa()
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