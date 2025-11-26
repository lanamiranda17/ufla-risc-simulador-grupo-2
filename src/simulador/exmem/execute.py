"""
Arquivo basicamente so pra testar se a estrutura da EX/MEM tá funcionando direito.
O QUE ESSE CÓDIGO FAZ:
Basicamente, esse é o cérebro matemático (ALU) do processador.
Ele pega a instrução e faz a conta que precisa: soma, subtração, operações lógicas (AND/OR) ou shifts.

Onde tá o "pulo do gato":
1. Garanti que todas as contas fiquem limitadas a 32 bits (usando & 0xFFFFFFFF), senão o Python deixa o número crescer infinitamente.
2. Arrumei o 'Shift Right' (ASR). Se o número for negativo, ele preenche com 1s à esquerda pra manter o sinal. Se não tivesse isso, o número negativo viraria positivo errado.
"""
def execute_instruction(instruction, registers):

    opcode = instruction['opcode']
    

    val_rs1 = registers.get(instruction.get('rs1'), 0)
    val_rs2 = registers.get(instruction.get('rs2'), 0)
    
    val_rs1 &= 0xFFFFFFFF
    val_rs2 &= 0xFFFFFFFF
    
    result = 0
    is_sub = False
    
    if opcode == 'add':
        result = val_rs1 + val_rs2
        is_sub = False
        
    elif opcode == 'sub':
        result = val_rs1 - val_rs2
        is_sub = True
        
    elif opcode == 'and':
        result = val_rs1 & val_rs2
        
    elif opcode == 'or':
        result = val_rs1 | val_rs2
        
    elif opcode == 'xor':
        result = val_rs1 ^ val_rs2
        
    elif opcode == 'not': 
        result = ~val_rs1
        
    elif opcode == 'shift_left':
        shift_amt = val_rs2 & 0x1F
        result = (val_rs1 << shift_amt)
        
    elif opcode == 'shift_right':
        shift_amt = val_rs2 & 0x1F
        

        if val_rs1 & 0x80000000:
            mask_padding = 0xFFFFFFFF << (32 - shift_amt)
            result = (val_rs1 >> shift_amt) | mask_padding
        else:
            result = val_rs1 >> shift_amt

    elif opcode == 'load' or opcode == 'store':
        result = val_rs1 

    return result, val_rs1, val_rs2, is_sub