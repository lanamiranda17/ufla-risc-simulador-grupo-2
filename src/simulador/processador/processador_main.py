# src/simulador/processador/processador_main.py

from .loader import ProgramLoader
from .memoria import Memoria
from .registradores import Registradores
from .pc import PC
from .ir import IR
from .flags import Flags
# Nova importação
from .cache import CacheL1 

class Processador:
    def __init__(self, caminho_programa_bin: str = None):
        # Inicializa a estrutura física do processador simulado
        
        # Instancia a memória principal (RAM)
        self.memoria = Memoria()
        
        # --- NOVO: Instancia as Caches L1 separadas ---
        # Ambas são "backed" pela mesma RAM (self.memoria), mas operam independentemente
        self.cache_instrucoes = CacheL1(self.memoria, nome="L1 Instruções")
        self.cache_dados = CacheL1(self.memoria, nome="L1 Dados")
        # ----------------------------------------------

        self.registradores = Registradores() 
        self.pc = PC()                       
        self.ir = IR()                       
        self.flags = Flags()                 
        
        if caminho_programa_bin:
            self.carregar_programa(caminho_programa_bin)
        
        self.parado = False 

    # ... (Os métodos _pc_get, _pc_set, _ir_set, _ir_get permanecem iguais) ...
    def _pc_get(self):
        if hasattr(self.pc, "load"): return self.pc.load()
        return getattr(self.pc, "valor", 0) 

    def _pc_set(self, valor):
        if hasattr(self.pc, "read"): return self.pc.read(valor)
        setattr(self.pc, "valor", valor) 

    def _ir_set(self, valor):
        if hasattr(self.ir, "carregar"): return self.ir.carregar(valor)
        setattr(self.ir, "valor", valor) 

    def _ir_get(self):
        if hasattr(self.ir, "instrucao"): return self.ir.instrucao
        return getattr(self.ir, "valor", 0) 

    def carregar_programa(self, caminho_programa_bin: str):
        """Carrega o programa na memória principal."""
        loader = ProgramLoader(caminho_programa_bin)
        # O Loader continua escrevendo direto na RAM (o que é correto, simula I/O de disco)
        # As caches estarão frias (vazias) e buscarão os dados sob demanda.
        endereco_inicio = loader.carregar_na_memoria(self.memoria)
        
        self._pc_set(endereco_inicio) 
        
        print(f"✓ Programa carregado na memória principal")
        print(f"✓ Endereço inicial (PC): {endereco_inicio:08b}")
        print(f"✓ Total de instruções: {len(loader.instrucoes)}")

    def _atualizar_flags(self, resultado, op1, op2, operacao):
        # ... (Método permanece inalterado) ...
        res_32 = resultado & 0xFFFFFFFF 
        self.flags.zero = 1 if res_32 == 0 else 0
        self.flags.neg = 1 if (res_32 >> 31) & 1 else 0
        self.flags.carry = 0
        self.flags.overflow = 0
        
        if operacao == 'add':
            if resultado > 0xFFFFFFFF: self.flags.carry = 1
            s_op1 = (op1 >> 31) & 1
            s_op2 = (op2 >> 31) & 1
            s_res = (res_32 >> 31) & 1
            if s_op1 == s_op2 and s_res != s_op1: self.flags.overflow = 1
                
        elif operacao == 'sub':
            if op2 > op1: self.flags.carry = 1
            s_op1 = (op1 >> 31) & 1
            s_op2 = (op2 >> 31) & 1
            s_res = (res_32 >> 31) & 1
            if s_op1 != s_op2 and s_res != s_op1: self.flags.overflow = 1

    def buscar_instrucao(self):
        """Etapa IF: Busca a próxima instrução usando a Cache de Instruções."""
        endereco = self._pc_get()               
        
        # --- ALTERAÇÃO: Usa a Cache L1 de Instruções ---
        instrucao = self.cache_instrucoes.load(endereco)
        # -----------------------------------------------
        
        self._ir_set(instrucao)                 
        return instrucao

    def decodificar(self):
        # ... (Método permanece inalterado) ...
        instrucao = self._ir_get() 
        opcode = (instrucao >> 24) & 0xFF
        ra_idx = (instrucao >> 16) & 0xFF
        rb_idx = (instrucao >> 8) & 0xFF
        rc_idx = instrucao & 0xFF
        end24 = instrucao & 0xFFFFFF        
        const16 = (instrucao >> 8) & 0xFFFF 
        
        val_ra = 0
        val_rb = 0
        if ra_idx < 32: val_ra = self.registradores.load(ra_idx) 
        if rb_idx < 32: val_rb = self.registradores.load(rb_idx) 

        return {
            'opcode': opcode,
            'ra_idx': ra_idx, 'val_ra': val_ra,
            'rb_idx': rb_idx, 'val_rb': val_rb,
            'rc_idx': rc_idx,
            'end24': end24,
            'const16': const16,
            'instrucao_bin': f"{instrucao:032b}"
        }

    def executar_instrucao(self, dec):
        """Etapa EX/MEM/WB: Executa usando a Cache de Dados para Load/Store."""
        op = dec['opcode']
        val_ra = dec['val_ra']
        val_rb = dec['val_rb']
        rc = dec['rc_idx'] 
        const16 = dec['const16']
        end24 = dec['end24']
        
        wb_result = None
        realizar_wb = False
        wb_destino = rc

        # --- OPERAÇÕES ARITMÉTICAS E LÓGICAS (ALU) ---
        # (Mantém toda a lógica aritmética inalterada: add, sub, zeros, xor, etc...)
        if op == 1:   # ADD
            res = val_ra + val_rb
            wb_result = res & 0xFFFFFFFF
            self._atualizar_flags(res, val_ra, val_rb, 'add')
            realizar_wb = True
        elif op == 2: # SUB
            res = val_ra - val_rb
            wb_result = res & 0xFFFFFFFF
            self._atualizar_flags(res, val_ra, val_rb, 'sub')
            realizar_wb = True
        elif op == 3: # ZEROS
            wb_result = 0
            self._atualizar_flags(0, 0, 0, 'logic')
            realizar_wb = True
        elif op == 4: # XOR
            wb_result = val_ra ^ val_rb
            self._atualizar_flags(wb_result, 0, 0, 'logic')
            realizar_wb = True
        elif op == 5: # OR
            wb_result = val_ra | val_rb
            self._atualizar_flags(wb_result, 0, 0, 'logic')
            realizar_wb = True
        elif op == 6: # NOT
            wb_result = (~val_ra) & 0xFFFFFFFF
            self._atualizar_flags(wb_result, 0, 0, 'logic')
            realizar_wb = True
        elif op == 7: # AND
            wb_result = val_ra & val_rb
            self._atualizar_flags(wb_result, 0, 0, 'logic')
            realizar_wb = True
        elif op == 8 or op == 10: # ASL/LSL
            shift = val_rb & 0x1F
            wb_result = (val_ra << shift) & 0xFFFFFFFF
            self._atualizar_flags(wb_result, 0, 0, 'logic')
            realizar_wb = True
        elif op == 9: # ASR
            shift = val_rb & 0x1F
            if (val_ra >> 31) & 1:
                mask = (0xFFFFFFFF << (32 - shift)) & 0xFFFFFFFF
                wb_result = (val_ra >> shift) | mask
            else:
                wb_result = (val_ra >> shift)
            self._atualizar_flags(wb_result, 0, 0, 'logic')
            realizar_wb = True
        elif op == 11: # LSR
            shift = val_rb & 0x1F
            wb_result = (val_ra >> shift)
            self._atualizar_flags(wb_result, 0, 0, 'logic')
            realizar_wb = True
        elif op == 12: # PASSA
            wb_result = val_ra
            self._atualizar_flags(wb_result, 0, 0, 'logic')
            realizar_wb = True
        elif op == 14: # LCL_MSB
            rc_atual = self.registradores.load(rc)
            wb_result = ((const16 << 16) & 0xFFFF0000) | (rc_atual & 0xFFFF)
            realizar_wb = True
        elif op == 15: # LCL_LSB
            rc_atual = self.registradores.load(rc)
            wb_result = (rc_atual & 0xFFFF0000) | (const16 & 0xFFFF)
            realizar_wb = True

        # --- AQUI ESTÁ A MUDANÇA PARA DADOS ---
        elif op == 16: # Instrução LOAD (Memória -> Registrador)
            # Lê da Cache L1 de Dados
            wb_result = self.cache_dados.load(val_ra)
            realizar_wb = True
            
        elif op == 17: # Instrução STORE (Registrador -> Memória)
            # Escreve na Cache L1 de Dados (que escreverá na RAM)
            self.cache_dados.store(self.registradores.load(rc), val_ra)
            print(f"    > [MEM/Cache] Endereço {self.registradores.load(rc)} <- {val_ra}")
        # --------------------------------------

        elif op == 18: # JAL
            pc_ret = self._pc_get()
            self.registradores.read(31, pc_ret)
            print(f"    > [WB] JAL: R31 <- {pc_ret}")
            self._pc_set(end24)
        elif op == 19: # JR
            self._pc_set(self.registradores.load(rc))
        elif op == 20: # BEQ
            if val_ra == val_rb: self._pc_set(rc)
        elif op == 21: # BNE
            if val_ra != val_rb: self._pc_set(rc)
        elif op == 22: # J
            self._pc_set(end24) 
        
        # ... (Instruções extras permanecem iguais: MUL, DIV, etc) ...
        elif op == 23: # MUL
            wb_result = (val_ra * val_rb) & 0xFFFFFFFF
            self._atualizar_flags(val_ra * val_rb, val_ra, val_rb, 'logic')
            realizar_wb = True
        elif op == 24: # DIV
            if val_rb != 0: wb_result = (val_ra // val_rb) & 0xFFFFFFFF
            else: wb_result = 0 
            self._atualizar_flags(wb_result, 0, 0, 'logic')
            realizar_wb = True
        elif op == 25: # MOD
            if val_rb != 0: wb_result = (val_ra % val_rb) & 0xFFFFFFFF
            else: wb_result = 0
            self._atualizar_flags(wb_result, 0, 0, 'logic')
            realizar_wb = True
        elif op == 26: # NEG
            res = -val_ra
            wb_result = res & 0xFFFFFFFF
            self._atualizar_flags(res, val_ra, 0, 'sub')
            realizar_wb = True
        elif op == 27: # INC
            res = val_ra + 1
            wb_result = res & 0xFFFFFFFF
            self._atualizar_flags(res, val_ra, 1, 'add')
            realizar_wb = True
        elif op == 28: # DEC
            res = val_ra - 1
            wb_result = res & 0xFFFFFFFF
            self._atualizar_flags(res, val_ra, 1, 'sub')
            realizar_wb = True
        elif op == 29: # BGT
            if val_ra > val_rb: self._pc_set(rc)
        elif op == 30: # BLT
            if val_ra < val_rb: self._pc_set(rc)

        # Write Back
        if realizar_wb and wb_destino < 32:
            self.registradores.read(wb_destino, wb_result)
            print(f"    > [WB] R{wb_destino} <- {wb_result}")

    def executar_passo(self):
        # ... (Inalterado) ...
        if self.parado: return False
        self.buscar_instrucao()
        dec = self.decodificar()
        pc_atual = self._pc_get()
        self._pc_set((pc_atual + 1) & 0xFFFFFFFF)
        self.executar_instrucao(dec)
        return dec

    def executar_programa(self):
        # ... (Pequena adição para mostrar status das caches no final, se desejar) ...
        print("\n=== Iniciando execução ===\n")
        ciclo = 0
        while not self.parado and ciclo < 1000:
            try:
                res = self.executar_passo()
                if res and res['opcode'] == 255: 
                    print(f"Ciclo {ciclo}: HALT encontrado.")
                    self.parado = True
                    break
                elif res:
                    print(f"Ciclo {ciclo}: Opcode={res['opcode']:02x} PC={self._pc_get():04x}")
                ciclo += 1
            except Exception as e:
                print(f"✗ Erro na execução: {e}")
                break
        
        if ciclo >= 1000:
            print("⚠ Limite de ciclos atingido!")
        
        self.estado()

    def estado(self):
        # ... (Exibição normal dos registradores) ...
        print("\n=== Estado Final ===")
        print(f"PC: {self._pc_get():08b} (Dec: {self._pc_get()})")
        print(f"IR: {self._ir_get():032b}")

        print("\n--- Estatísticas das Caches ---")
        print(self.cache_instrucoes.get_stats())
        print(self.cache_dados.get_stats())

        print("\n--- Registradores ---")
        tem_valor = False
        for i, valor in enumerate(self.registradores.regs):
            if valor != 0:
                print(f"R{i:<2}: {valor:<10} (Hex: 0x{valor:X})")
                tem_valor = True
        if not tem_valor:
            print("(Todos os registradores estão zerados)")