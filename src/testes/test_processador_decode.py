import sys
import os

# adiciona a pasta pai (`src`) ao caminho para permitir import absoluto do pacote `simulador`
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulador.processador.processador_main import Processador


def test_decode_and_prepare_operands():
    cpu = Processador()

    # Monta instrução: opcode=00000001 (add), ra=1, rb=2, rc=3, resto zeros
    opcode = '00000001'
    ra = format(1, '05b')
    rb = format(2, '05b')
    rc = format(3, '05b')
    rest = '0' * 9
    bits = opcode + ra + rb + rc + rest
    instr_int = int(bits, 2)

    # Grava instrução na memória e prepara registradores com valores
    cpu.memoria.store(0, instr_int)
    cpu.regs.read(1, 10)
    cpu.regs.read(2, 20)

    # Fetch + Decode
    cpu.pc.read(0)
    cpu.fetch()
    decoded = cpu.decode()

    assert decoded['mnemonic'] == 'add'
    assert decoded['ra'] == 1
    assert decoded['rb'] == 2
    # operandos preparados
    assert cpu.op_ra_val == 10
    assert cpu.op_rb_val == 20
    # imediato e endereco devem corresponder aos campos decodificados
    assert cpu.imediato == decoded['const16']
    assert cpu.endereco == decoded['end24']
