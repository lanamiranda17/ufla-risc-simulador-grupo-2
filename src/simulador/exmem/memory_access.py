"""
O QUE ESSE CÓDIGO FAZ:
Aqui eu controlo quem entra e quem sai da memória (RAM).
- Se for LOAD: Eu busco o valor na memória e devolvo.
- Se for STORE: Eu pego o valor do registrador e salvo na memória.

Segurança:
Coloquei uma proteção pra garantir que o endereço esteja dentro do limite (0 a 65535). Se tentar acessar fora disso, ele avisa que deu erro (Segmentation Fault) em vez de travar o programa todo.
"""
def memory_access(execution_result, instruction, memory, registers):
    mem_op = instruction.get('mem_access')
    
    if not mem_op:
        return execution_result
    
    address = execution_result
    
    if not (0 <= address < 65536):
        print(f"ERRO DE EXECUÇÃO: Segmentation Fault no endereço {address}")
        return 0 

    if mem_op == 'load':
        return memory.get(address, 0)
        
    elif mem_op == 'store':
        val_to_store = registers.get(instruction.get('rs1'), 0)
        memory[address] = val_to_store & 0xFFFFFFFF
        return None 

    return execution_result