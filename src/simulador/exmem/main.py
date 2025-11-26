"""
O QUE ESSE CÓDIGO FAZ:
Esse é o maestro que rege a orquestra. Ele inicializa o processador (cria os registradores e a memória zerada) e chama as funções na ordem certa do ciclo:
1. Executa (ALU)
2. Atualiza as Flags
3. Acessa a Memória
4. Escreve o resultado no registrador (Write Back)

Obs: Deixei um teste pronto aqui no final que faz um Shift Aritmético num número negativo. Se o resultado der '0xff...', significa que tudo funcionou
"""
from execute import execute_instruction
from memory_access import memory_access
from flags import update_flags


registers = {f'r{i}': 0 for i in range(32)}
memory = {i: 0 for i in range(65536)} 
flags = {'zero': False, 'overflow': False, 'carry': False, 'negative': False}


LOGICAL_OPS = ['and', 'or', 'xor', 'not', 'shift_left', 'shift_right', 'copy']


registers['r1'] = 0xF0000000
instruction = {
    'opcode': 'shift_right',
    'rs1': 'r1',
    'rs2': 'r2', 
    'rd': 'r3',
    'mem_access': None
}
registers['r2'] = 4 

print("--- Simulação Ciclo EX/MEM ---")


result_alu, op_a, op_b, is_sub = execute_instruction(instruction, registers)


is_logic_instruction = instruction['opcode'] in LOGICAL_OPS
flags = update_flags(result_alu, op_a, op_b, is_sub, is_logic=is_logic_instruction)


final_data = memory_access(result_alu, instruction, memory, registers)


if instruction.get('mem_access') != 'store' and instruction.get('rd'):
    reg_dest = instruction['rd']
    if reg_dest != 'r0':
        registers[reg_dest] = final_data & 0xFFFFFFFF

# --- RELATÓRIO ---
print(f"Instrução: {instruction['opcode']}")
print(f"Entrada (r1): {hex(op_a)}")
print(f"Resultado (r3): {hex(registers['r3'])}")
print(f"Flags: {flags}")