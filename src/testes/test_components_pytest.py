import sys
import os
import pytest

# Garante que a pasta `src` esteja no caminho de import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulador.processador.memoria import Memoria
from simulador.processador.registradores import Registradores
from simulador.processador.pc import PC
from simulador.processador.flags import Flags
from simulador.processador.ir import IR


def test_memoria_store_load_and_mask():
    m = Memoria()
    m.store(0, 0)
    assert m.load(0) == 0

    # Testa máscara de 32 bits
    m.store(65535, 0x1FFFFFFFF)
    assert m.load(65535) == (0x1FFFFFFFF & 0xFFFFFFFF)

    # Valores negativos também são armazenados como 32 bits
    m.store(1, -1)
    assert m.load(1) == ((-1) & 0xFFFFFFFF)


def test_memoria_out_of_bounds_raises():
    m = Memoria()
    with pytest.raises(IndexError):
        m.load(65536)
    with pytest.raises(IndexError):
        m.store(65536, 0)


def test_registradores_mask_and_access():
    r = Registradores()
    r.read(0, 0)
    assert r.load(0) == 0

    r.read(31, 0x123456789)
    assert r.load(31) == (0x123456789 & 0xFFFFFFFF)


def test_pc_load_and_wrap():
    pc = PC()
    assert pc.load() == 0
    pc.read(0x1FFFFFFFF)
    assert pc.load() == (0x1FFFFFFFF & 0xFFFFFFFF)


def test_flags_default_and_reset():
    f = Flags()
    assert f.neg == f.zero == f.carry == f.overflow == 0
    f.neg = f.zero = f.carry = f.overflow = 1
    f.reset()
    assert f.neg == f.zero == f.carry == f.overflow == 0


def test_ir_carregar_mask():
    ir = IR()
    ir.carregar(0x1FFFFFFFF)
    assert ir.instrucao == (0x1FFFFFFFF & 0xFFFFFFFF)
