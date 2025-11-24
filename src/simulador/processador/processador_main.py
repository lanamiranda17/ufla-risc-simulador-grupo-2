from .memoria import Memoria
from .registradores import Registradores
from .pc import PC
from .ir import IR
from .flags import Flags
from interpretador.interpretador import decode_instruction_int

class Processador:
    def __init__(self):
        self.memoria = Memoria()
        self.regs = Registradores()
        self.pc = PC()
        self.ir = IR()
        self.flags = Flags()

    def fetch(self):
        """
        IF - Instruction Fetch
        - Busca a instrução apontada pelo PC na memória
        - Carrega a instrução no IR
        - Incrementa o PC (próxima instrução)
        Retorna a instrução (int) lida.
        """
        endereco = self.pc.load()
        instrucao = self.memoria.load(endereco)
        # Carrega a instrução no registrador de instrução
        self.ir.carregar(instrucao)
        # Incrementa o PC para a próxima palavra
        self.pc.read(endereco + 1)
        return instrucao

    def decode(self):
        """
        ID - Instruction Decode
        - Decodifica a instrução presente no IR usando `decode_instruction_int`
        - Extrai opcode, registradores, imediato e endereço
        - Prepara operandos lendo os registradores (valores)
        Retorna o dicionário de decodificação.
        """
        instr = self.ir.instrucao
        decoded = decode_instruction_int(instr)
        # guarda decodificação para acesso posterior
        self.decoded = decoded

        # campos básicos
        self.opcode = decoded.get('opcode')
        self.mnemonic = decoded.get('mnemonic')
        self.ra = decoded.get('ra')
        self.rb = decoded.get('rb')
        self.rc = decoded.get('rc')

        # imediato (const16) e endereço (end24)
        self.imediato = decoded.get('const16')
        self.endereco = decoded.get('end24')

        # preparar operandos (valores lidos dos registradores)
        try:
            self.op_ra_val = self.regs.load(self.ra)
        except Exception:
            self.op_ra_val = None
        try:
            self.op_rb_val = self.regs.load(self.rb)
        except Exception:
            self.op_rb_val = None

        return decoded
