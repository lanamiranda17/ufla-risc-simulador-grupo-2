from .loader import ProgramLoader
from .memoria import Memoria
from .registradores import Registradores
from .pc import PC
from .ir import IR
from .flags import Flags

class Processador:
    def __init__(self, caminho_programa_bin: str = None):
        # Inicializa os componentes físicos simulados
        self.memoria = Memoria()             # Cria a memória RAM
        self.registradores = Registradores() # Cria o banco de registradores (R0-R31)
        self.pc = PC()                       # Cria o contador de programa (PC)
        self.ir = IR()                       # Cria o registrador de instrução (IR)
        self.flags = Flags()                 # Cria o registrador de status (Flags)
        
        # Se um arquivo foi passado, carrega na memória
        if caminho_programa_bin:
            self.carregar_programa(caminho_programa_bin)
        
        self.parado = False # Controle para saber se o processador deve continuar rodando

    # ------------------------------------------------------------------
    # HELPERS (Camada de compatibilidade para PC e IR)
    # ------------------------------------------------------------------
    def _pc_get(self):
        # Tenta diferentes nomes de métodos para ler o PC
        if hasattr(self.pc, "load"): return self.pc.load()
        if hasattr(self.pc, "obter"): return self.pc.obter()
        if hasattr(self.pc, "get"): return self.pc.get()
        return getattr(self.pc, "valor", 0) # Fallback

    def _pc_set(self, valor):
        # Tenta diferentes nomes de métodos para escrever no PC
        if hasattr(self.pc, "read"): return self.pc.read(valor)
        if hasattr(self.pc, "definir"): return self.pc.definir(valor)
        if hasattr(self.pc, "set"): return self.pc.set(valor)
        if hasattr(self.pc, "write"): return self.pc.write(valor)
        setattr(self.pc, "valor", valor) # Fallback

    def _ir_set(self, valor):
        # Prioriza 'carregar' (nome usado na sua classe IR)
        if hasattr(self.ir, "carregar"): return self.ir.carregar(valor)
        if hasattr(self.ir, "definir"): return self.ir.definir(valor)
        if hasattr(self.ir, "load"): return self.ir.load(valor)
        setattr(self.ir, "valor", valor) # Fallback

    def _ir_get(self):
        # Prioriza 'instrucao' (nome do atributo na sua classe IR)
        if hasattr(self.ir, "instrucao"): return self.ir.instrucao
        if hasattr(self.ir, "obter"): return self.ir.obter()
        if hasattr(self.ir, "load"): return self.ir.load()
        return getattr(self.ir, "valor", 0) # Fallback

    # ------------------------------------------------------------------
    # LÓGICA DO PROCESSADOR
    # ------------------------------------------------------------------

    def carregar_programa(self, caminho_programa_bin: str):
        """Carrega um programa compilado (.bin) na memória."""
        loader = ProgramLoader(caminho_programa_bin)
        endereco_inicio = loader.carregar_na_memoria(self.memoria)
        
        self._pc_set(endereco_inicio) # Define onde o PC começa
        
        print(f"✓ Programa carregado na memória")
        print(f"✓ Endereço inicial (PC): {endereco_inicio:08b}")
        print(f"✓ Total de instruções: {len(loader.instrucoes)}")

    def _atualizar_flags(self, resultado, op1, op2, operacao):
        """[EX] Atualiza as flags com base no resultado da ALU."""
        res_32 = resultado & 0xFFFFFFFF # Garante que olhamos apenas os 32 bits
        
        # [EX] Flag ZERO: Se o resultado for 0, flag = 1
        self.flags.zero = 1 if res_32 == 0 else 0
        
        # [EX] Flag NEG: Olha o bit mais significativo (sinal)
        self.flags.neg = 1 if (res_32 >> 31) & 1 else 0
        
        self.flags.carry = 0
        self.flags.overflow = 0
        
        if operacao == 'add':
            # [EX] Carry: Se o resultado real for maior que 32 bits
            if resultado > 0xFFFFFFFF:
                self.flags.carry = 1
            # [EX] Overflow: Lógica de sinal para soma (sinais iguais geram sinal oposto)
            s_op1 = (op1 >> 31) & 1
            s_op2 = (op2 >> 31) & 1
            s_res = (res_32 >> 31) & 1
            if s_op1 == s_op2 and s_res != s_op1:
                self.flags.overflow = 1
                
        elif operacao == 'sub':
            # [EX] Carry (Borrow): Se subtrair um número maior de um menor (unsigned)
            if op2 > op1:
                self.flags.carry = 1
            # [EX] Overflow: Lógica de sinal para subtração
            s_op1 = (op1 >> 31) & 1
            s_op2 = (op2 >> 31) & 1
            s_res = (res_32 >> 31) & 1
            if s_op1 != s_op2 and s_res != s_op1:
                self.flags.overflow = 1

    def buscar_instrucao(self):
        """[IF] Instruction Fetch: Busca a instrução."""
        endereco = self._pc_get()               # [IF] Lê o endereço atual no PC
        instrucao = self.memoria.load(endereco) # [IF] Busca a instrução na Memória
        self._ir_set(instrucao)                 # [IF] Grava a instrução no IR
        return instrucao

    def decodificar(self):
        """[ID] Instruction Decode: Decodifica e busca operandos."""
        instrucao = self._ir_get() # [ID] Lê a instrução do IR
        
        # [ID] Extrai os campos usando máscaras e shifts (Decodificação)
        opcode = (instrucao >> 24) & 0xFF
        ra_idx = (instrucao >> 16) & 0xFF
        rb_idx = (instrucao >> 8) & 0xFF
        rc_idx = instrucao & 0xFF
        end24 = instrucao & 0xFFFFFF        # Usado para Jumps
        const16 = (instrucao >> 8) & 0xFFFF # Usado para LCL (constantes)
        
        # [ID] Busca de Operandos (Fetch Operands) no Banco de Registradores
        val_ra = 0
        val_rb = 0
        if ra_idx < 32: val_ra = self.registradores.load(ra_idx) # [ID] Lê valor de RA
        if rb_idx < 32: val_rb = self.registradores.load(rb_idx) # [ID] Lê valor de RB

        # Retorna todos os dados prontos para o estágio EX
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
        """[EX / MEM / WB] Executa a lógica baseada no Opcode."""
        op = dec['opcode']
        val_ra = dec['val_ra']
        val_rb = dec['val_rb']
        rc = dec['rc_idx'] # <--- O endereço de salto condicional está AQUI
        const16 = dec['const16']
        end24 = dec['end24']
        
        wb_result = None
        realizar_wb = False
        wb_destino = rc

        # --- [EX] ARITMÉTICA E LÓGICA (ALU) ---
        if op == 1: # ADD
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
            
        # --- [EX] SHIFTS ---
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

        # --- [EX] CONSTANTES E MEMÓRIA ---
        elif op == 14: # LCL_MSB
            rc_atual = self.registradores.load(rc)
            wb_result = ((const16 << 16) & 0xFFFF0000) | (rc_atual & 0xFFFF)
            realizar_wb = True
        elif op == 15: # LCL_LSB
            rc_atual = self.registradores.load(rc)
            wb_result = (rc_atual & 0xFFFF0000) | (const16 & 0xFFFF)
            realizar_wb = True
        elif op == 16: # LOAD
            wb_result = self.memoria.load(val_ra)
            realizar_wb = True
        elif op == 17: # STORE
            self.memoria.store(self.registradores.load(rc), val_ra)
            print(f"    > [MEM] Mem[{self.registradores.load(rc)}] <- {val_ra}")

        # --- [EX] CONTROLE DE FLUXO ---
        # Nota: J e JAL usam end24. Branches condicionais usam RC.
        elif op == 18: # JAL
            pc_ret = self._pc_get()
            self.registradores.read(31, pc_ret)
            print(f"    > [WB] JAL: R31 <- {pc_ret}")
            self._pc_set(end24)
        elif op == 19: # JR
            self._pc_set(self.registradores.load(rc))
        
        # CORREÇÃO: Branches condicionais usam 'rc' como endereço
        elif op == 20: # BEQ
            if val_ra == val_rb: self._pc_set(rc)
        elif op == 21: # BNE
            if val_ra != val_rb: self._pc_set(rc)
        elif op == 22: # J (Incondicional)
            self._pc_set(end24) # J usa 24 bits

        # --- NOVAS INSTRUÇÕES ---
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
        
        # CORREÇÃO: Novas condicionais também usam 'rc'
        elif op == 29: # BGT
            if val_ra > val_rb: self._pc_set(rc)
        elif op == 30: # BLT
            if val_ra < val_rb: self._pc_set(rc)

        # --- [WB] WRITE BACK ---
        if realizar_wb and wb_destino < 32:
            self.registradores.read(wb_destino, wb_result)
            print(f"    > [WB] R{wb_destino} <- {wb_result}")

    def executar_passo(self):
        """Ciclo completo: IF -> ID -> PC+1 -> EX/MEM/WB"""
        if self.parado: return False
        
        # 1. Fetch [IF]
        self.buscar_instrucao()
        
        # 2. Decode [ID]
        dec = self.decodificar()
        
        # Incrementa PC [IF/ID]
        # (Feito aqui para garantir que Jumps tenham o PC base correto)
        pc_atual = self._pc_get()
        self._pc_set((pc_atual + 1) & 0xFFFFFFFF)
        
        # 3. Execute / Memory / WriteBack [EX/MEM/WB]
        self.executar_instrucao(dec)
        
        return dec

    def executar_programa(self):
        """Loop principal de controle da simulação."""
        print("\n=== Iniciando execução ===\n")
        
        ciclo = 0
        while not self.parado and ciclo < 1000:
            try:
                # Dispara um ciclo completo de clock
                res = self.executar_passo()
                
                # Verifica instrução de Parada (HALT)
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
        print("\n=== Estado Final ===")
        print(f"PC: {self._pc_get():08b}")
        print(f"IR: {self._ir_get():032b}")
