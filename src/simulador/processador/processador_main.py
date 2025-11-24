import sys

from .memoria import Memoria
from .registradores import Registradores
from .pc import PC
from .ir import IR
from .flags import Flags

class Processador:
    def __init__(self):
        self.memoria = Memoria()
        self.regs = Registradores()
        self.pc = PC()
        self.ir = IR()
        self.flags = Flags()

        # Variáveis internas de controle (Pipeline registers fictícios)
        self.opcode = 0
        self.ra_idx = 0
        self.rb_idx = 0
        self.rc_idx = 0
        self.op1 = 0    # Valor do operando A
        self.op2 = 0    # Valor do operando B
        self.alu_res = 0 # Resultado da ALU
        self.wb_data = 0 # Dado para escrever no registrador (se houver)
        self.write_enable = False # Flag para permitir escrita no WB

    def executar(self):
        print("--- Iniciando Simulação ---")
        while True:
            # =================================================
            # 1. IF: Instruction Fetch (Busca)
            # =================================================
            pc_atual = self.pc.load()
            
            # Verifica limites da memória
            if pc_atual >= 65536:
                print("Erro: PC fora dos limites da memória.")
                break

            instrucao = self.memoria.load(pc_atual)
            self.ir.carregar(instrucao)
            
            # Verifica HALT (Todos os bits 1 = 0xFFFFFFFF ou -1 em signed)
            if self.ir.instrucao == 0xFFFFFFFF:
                print(f"HALT encontrado no endereço {pc_atual}. Fim da execução.")
                self.imprimir_estado_final()
                break

            # Incrementa PC
            self.pc.read(pc_atual + 1) # Nota: .read() da Lana funciona como SET

            # =================================================
            # 2. ID: Instruction Decode (Decodificação)
            # =================================================
            inst = self.ir.instrucao
            
            # Extração de campos (Bitwise Shift e Mask)
            self.opcode = (inst >> 24) & 0xFF
            self.ra_idx = (inst >> 16) & 0xFF
            self.rb_idx = (inst >> 8) & 0xFF
            self.rc_idx = inst & 0xFF

            # Busca de operandos nos registradores
            self.op1 = self.regs.load(self.ra_idx)
            self.op2 = self.regs.load(self.rb_idx)

            # Reset das variáveis de execução
            self.alu_res = 0
            self.write_enable = False
            
            # =================================================
            # 3. EX/MEM: Execute & Memory
            # =================================================
            self._executar_estagio_ex_mem()

            # =================================================
            # 4. WB: Write Back (Escrita)
            # =================================================
            if self.write_enable:
                # Nota: O método .read() da Lana GRAVA o valor no registrador
                self.regs.read(self.rc_idx, self.wb_data)
                
            # (Opcional) Debug por ciclo:
            # print(f"PC:{pc_atual} | OP:{self.opcode} | R[{self.rc_idx}]={self.wb_data}")

    def _executar_estagio_ex_mem(self):
        """Lógica separada para executar as instruções baseado no Opcode"""
        
        op = self.opcode
        
        # --- ALU Operations (0x01 a 0x0C) ---
        if 0x01 <= op <= 0x0C:
            self.write_enable = True
            res = 0
            
            if op == 0x01:   # ADD
                res = self.op1 + self.op2
                self._atualizar_flags_aritmetica(res, is_sub=False)
            elif op == 0x02: # SUB
                res = self.op1 - self.op2
                self._atualizar_flags_aritmetica(res, is_sub=True)
            elif op == 0x03: # ZERO
                res = 0
                self.flags.reset()
                self.flags.zero = 1
            elif op == 0x04: # XOR
                res = self.op1 ^ self.op2
                self._atualizar_flags_logica(res)
            elif op == 0x05: # OR
                res = self.op1 | self.op2
                self._atualizar_flags_logica(res)
            elif op == 0x06: # NOT
                res = ~self.op1
                self._atualizar_flags_logica(res)
            elif op == 0x07: # AND
                res = self.op1 & self.op2
                self._atualizar_flags_logica(res)
            elif op == 0x08: # ASL (Shift Aritmético Esq)
                res = self.op1 << self.op2
                self._atualizar_flags_logica(res)
            elif op == 0x09: # ASR (Shift Aritmético Dir)
                res = self.op1 >> self.op2
                self._atualizar_flags_logica(res)
            elif op == 0x0A: # LSL (Lógico Esq - igual ao ASL em Python positivo)
                res = self.op1 << self.op2
                self._atualizar_flags_logica(res)
            elif op == 0x0B: # LSR (Lógico Dir)
                res = (self.op1 & 0xFFFFFFFF) >> self.op2
                self._atualizar_flags_logica(res)
            elif op == 0x0C: # COPY
                res = self.op1
                self.flags.reset() # Copy geralmente não afeta flags ou afeta como lógica? PDF diz: Reset overflow/carry
            
            # Garante 32 bits
            self.alu_res = res & 0xFFFFFFFF
            self.wb_data = self.alu_res

        # --- Constantes e Memória (0x0E a 0x11) ---
        elif op == 0x0E: # LCL (Carrega Constante Alta 16 bits)
            # Formato especial: Constante está em Ra e Rb (bits 23-8)
            const16 = (self.ra_idx << 8) | self.rb_idx
            val_atual = self.regs.load(self.rc_idx)
            # (Const16 << 16) | (Parte Baixa atual)
            res = (const16 << 16) | (val_atual & 0xFFFF)
            self.wb_data = res & 0xFFFFFFFF
            self.write_enable = True

        elif op == 0x0F: # LCH (Carrega Constante Baixa 16 bits) - Assumindo Opcode
            const16 = (self.ra_idx << 8) | self.rb_idx
            val_atual = self.regs.load(self.rc_idx)
            # (Parte Alta atual) | Const16
            res = (val_atual & 0xFFFF0000) | const16
            self.wb_data = res & 0xFFFFFFFF
            self.write_enable = True

        elif op == 0x10: # LOAD Word
            endereco = self.op1 & 0xFFFF # Endereço está em RA
            val = self.memoria.load(endereco)
            self.wb_data = val
            self.write_enable = True
        
        elif op == 0x11: # STORE Word
            endereco = self.regs.load(self.rc_idx) & 0xFFFF # Destino (Endereço) está em RC
            valor = self.op1 # Valor está em RA
            self.memoria.store(endereco, valor)
            self.write_enable = False

        # --- Controle de Fluxo (0x12 a 0x16) ---
        # Nota: O PDF define Jumps com opcodes específicos, ajuste se necessário
        elif op == 0x12: # JAL (Jump And Link)
            # Salva PC atual no R31
            pc_atual = self.pc.load()
            self.regs.read(31, pc_atual) # .read é set
            
            # Endereço está nos 24 bits (Ra, Rb, Rc) -> Formato JUMP
            # Mas o PDF diz "jal end". Onde está end?
            # Assumindo formato Tipo J: Bits 23-0
            endereco_salto = (self.ir.instrucao & 0x00FFFFFF)
            self.pc.read(endereco_salto)

        elif op == 0x13: # JR (Jump Register)
            # Endereço está em RC
            novo_pc = self.regs.load(self.rc_idx)
            self.pc.read(novo_pc)

        elif op == 0x14: # BEQ (Branch if Equal)
            if self.op1 == self.op2:
                # Endereço de salto está no campo RC (apenas 8 bits segundo PDF?)
                # Se for offset, somamos. Se for absoluto, trocamos.
                # O PDF diz "PC <- end". Assumindo absoluto curto (0-255)
                self.pc.read(self.rc_idx)

        elif op == 0x15: # BNE (Branch if Not Equal)
            if self.op1 != self.op2:
                self.pc.read(self.rc_idx)

        elif op == 0x16: # JUMP (Incondicional)
             # Bits 23-0
            endereco_salto = (self.ir.instrucao & 0x00FFFFFF)
            self.pc.read(endereco_salto)

    def _atualizar_flags_aritmetica(self, res, is_sub):
        # Simula comportamento de 32 bits signed
        val_32 = res & 0xFFFFFFFF
        
        self.flags.zero = 1 if val_32 == 0 else 0
        self.flags.neg = 1 if (val_32 >> 31) else 0
        
        # Carry e Overflow (Simplificado para Python)
        # Em hardware real, isso verifica o bit de transporte do bit 31
        if not is_sub:
            self.flags.carry = 1 if res > 0xFFFFFFFF else 0
        else:
            self.flags.carry = 0 # Subtração é complexa de definir carry sem acesso aos bits crus
            
        # Overflow (Sinal errado)
        # Ex: Positivo + Positivo = Negativo
        sinal_op1 = (self.op1 >> 31) & 1
        sinal_op2 = (self.op2 >> 31) & 1
        sinal_res = (val_32 >> 31) & 1
        
        if not is_sub:
            if (sinal_op1 == sinal_op2) and (sinal_res != sinal_op1):
                self.flags.overflow = 1
            else:
                self.flags.overflow = 0

    def _atualizar_flags_logica(self, res):
        val_32 = res & 0xFFFFFFFF
        self.flags.zero = 1 if val_32 == 0 else 0
        self.flags.neg = 1 if (val_32 >> 31) else 0
        self.flags.carry = 0
        self.flags.overflow = 0

    def imprimir_estado_final(self):
        print("\n--- Estado Final ---")
        print(f"PC: {self.pc.load()}")
        print("Registradores (não nulos):")
        for i in range(32):
            val = self.regs.load(i)
            if val != 0:
                print(f"R{i}: {val} ({hex(val)})")
