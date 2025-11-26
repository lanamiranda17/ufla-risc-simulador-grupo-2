"""
O QUE ESSE CÓDIGO FAZ:
Esse arquivo calcula as "bandeiras" (flags) depois de cada operação:
- Zero (Z): Se o resultado deu 0.
- Negative (N): Se o resultado é negativo.
- Overflow (V) e Carry (C): Se a conta "estourou" o limite.

O detalhe importante:
Seguindo o PDF, eu adicionei uma verificação (is_logic). Se a operação for lógica (tipo AND, OR, SHIFT), eu forço o Overflow e o Carry a serem Falsos, pra não dar erro de leitura depois.
"""
def update_flags(result, op_a, op_b, is_sub, is_logic=False):
    res_32 = result & 0xFFFFFFFF
    
    z_flag = (res_32 == 0)
    
    n_flag = (res_32 & 0x80000000) != 0
    
    if is_logic:
        v_flag = False
        c_flag = False
    else:
        msb_a = (op_a >> 31) & 1
        msb_b = (op_b >> 31) & 1
        msb_r = (res_32 >> 31) & 1
        
        if is_sub:
            v_flag = (msb_a != msb_b) and (msb_a != msb_r)
            c_flag = (op_a >= op_b)
        else:
            v_flag = (msb_a == msb_b) and (msb_a != msb_r)
            c_flag = (result > 0xFFFFFFFF)

    return {
        'zero': z_flag,
        'overflow': v_flag,
        'carry': c_flag,
        'negative': n_flag
    }