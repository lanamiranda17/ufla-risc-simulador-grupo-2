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
