# Importa a classe responsável por carregar o programa binário para a memória
from .loader import ProgramLoader
# Importa a classe que simula a Memória RAM do processador
from .memoria import Memoria
# Importa a classe que gerencia o banco de registradores (R0 a R31)
from .registradores import Registradores
# Importa a classe do Contador de Programa (PC - Program Counter)
from .pc import PC
# Importa a classe do Registrador de Instrução (IR - Instruction Register)
from .ir import IR
# Importa a classe que gerencia as Flags de status (Zero, Negativo, Carry, Overflow)
from .flags import Flags

class Processador:
    def __init__(self, caminho_programa_bin: str = None):
        # Inicializa a estrutura física do processador simulado
        
        # Instancia a memória principal (RAM) onde dados e instruções serão armazenados
        self.memoria = Memoria()             
        # Instancia o banco de 32 registradores de uso geral
        self.registradores = Registradores() 
        # Instancia o Program Counter, responsável por guardar o endereço da próxima instrução
        self.pc = PC()                       
        # Instancia o Instruction Register, que guarda a instrução atual sendo executada
        self.ir = IR()                       
        # Instancia o registrador de Flags para controle de estado das operações aritméticas
        self.flags = Flags()                 
        
        # Verifica se um caminho de arquivo binário foi fornecido na inicialização
        if caminho_programa_bin:
            # Se sim, chama o método para carregar o programa na memória imediatamente
            self.carregar_programa(caminho_programa_bin)
        
        # Define a flag de controle de execução como Falso (o processador não está parado)
        self.parado = False 

    # ------------------------------------------------------------------
    # HELPERS (Camada de compatibilidade para abstrair métodos de PC e IR)
    # ------------------------------------------------------------------
    def _pc_get(self):
        # Tenta obter o valor atual do PC verificando qual método está disponível na classe PC
        if hasattr(self.pc, "load"): return self.pc.load()
        if hasattr(self.pc, "obter"): return self.pc.obter()
        if hasattr(self.pc, "get"): return self.pc.get()
        # Se nenhum método for encontrado, tenta acessar o atributo 'valor' diretamente; retorna 0 se falhar
        return getattr(self.pc, "valor", 0) 

    def _pc_set(self, valor):
        # Tenta definir um novo valor para o PC verificando qual método de escrita está disponível
        if hasattr(self.pc, "read"): return self.pc.read(valor)
        if hasattr(self.pc, "definir"): return self.pc.definir(valor)
        if hasattr(self.pc, "set"): return self.pc.set(valor)
        if hasattr(self.pc, "write"): return self.pc.write(valor)
        # Se nenhum método for encontrado, define o atributo 'valor' diretamente
        setattr(self.pc, "valor", valor) 

    def _ir_set(self, valor):
        # Define o valor do IR (instrução atual) verificando o método disponível na classe IR
        if hasattr(self.ir, "carregar"): return self.ir.carregar(valor)
        if hasattr(self.ir, "definir"): return self.ir.definir(valor)
        if hasattr(self.ir, "load"): return self.ir.load(valor)
        # Se nenhum método for encontrado, define o atributo 'valor' diretamente
        setattr(self.ir, "valor", valor) 

    def _ir_get(self):
        # Obtém o valor atual do IR verificando o atributo ou método disponível
        if hasattr(self.ir, "instrucao"): return self.ir.instrucao
        if hasattr(self.ir, "obter"): return self.ir.obter()
        if hasattr(self.ir, "load"): return self.ir.load()
        # Se falhar, retorna o atributo 'valor' ou 0 como padrão
        return getattr(self.ir, "valor", 0) 

    # ------------------------------------------------------------------
    # LÓGICA DO PROCESSADOR (Ciclo de Instrução)
    # ------------------------------------------------------------------

    def carregar_programa(self, caminho_programa_bin: str):
        """Carrega o conteúdo de um arquivo binário para a memória do simulador."""
        # Cria uma instância do loader responsável por ler o arquivo binário
        loader = ProgramLoader(caminho_programa_bin)
        # Carrega as instruções na memória e recebe o endereço da primeira instrução
        endereco_inicio = loader.carregar_na_memoria(self.memoria)
        
        # Define o PC para apontar para o endereço inicial do programa carregado
        self._pc_set(endereco_inicio) 
        
        # Exibe mensagem de confirmação de carregamento
        print(f"✓ Programa carregado na memória")
        # Exibe o endereço inicial em binário
        print(f"✓ Endereço inicial (PC): {endereco_inicio:08b}")
        # Exibe a contagem total de instruções carregadas
        print(f"✓ Total de instruções: {len(loader.instrucoes)}")

    def _atualizar_flags(self, resultado, op1, op2, operacao):
        """Atualiza as flags de estado (Zero, Neg, Carry, Overflow) após operações da ALU."""
        # Aplica uma máscara de 32 bits para garantir que o resultado simule um registrador real
        res_32 = resultado & 0xFFFFFFFF 
        
        # Flag ZERO: Define como 1 se o resultado truncado for exatamente 0
        self.flags.zero = 1 if res_32 == 0 else 0
        
        # Flag NEG: Verifica o bit mais significativo (bit 31); se for 1, o número é negativo
        self.flags.neg = 1 if (res_32 >> 31) & 1 else 0
        
        # Reseta as flags Carry e Overflow antes de recalculá-las
        self.flags.carry = 0
        self.flags.overflow = 0
        
        # Lógica específica para operações de SOMA
        if operacao == 'add':
            # Carry: Ativa se o resultado real ultrapassar o limite de 32 bits (unsigned)
            if resultado > 0xFFFFFFFF:
                self.flags.carry = 1
            # Extrai o bit de sinal dos operandos e do resultado para verificar Overflow
            s_op1 = (op1 >> 31) & 1
            s_op2 = (op2 >> 31) & 1
            s_res = (res_32 >> 31) & 1
            # Overflow na soma ocorre se somamos dois números com mesmo sinal e o resultado tem sinal oposto
            if s_op1 == s_op2 and s_res != s_op1:
                self.flags.overflow = 1
                
        # Lógica específica para operações de SUBTRAÇÃO
        elif operacao == 'sub':
            # Carry (Borrow): Ativa se tentarmos subtrair um número maior de um menor (em unsigned)
            if op2 > op1:
                self.flags.carry = 1
            # Extrai os bits de sinal novamente para Overflow na subtração
            s_op1 = (op1 >> 31) & 1
            s_op2 = (op2 >> 31) & 1
            s_res = (res_32 >> 31) & 1
            # Overflow na subtração ocorre se sinais dos operandos são diferentes e o resultado difere do primeiro
            if s_op1 != s_op2 and s_res != s_op1:
                self.flags.overflow = 1

    def buscar_instrucao(self):
        """Etapa IF (Instruction Fetch): Busca a próxima instrução na memória."""
        # Obtém o endereço da instrução atual apontado pelo PC
        endereco = self._pc_get()               
        # Acessa a memória neste endereço e recupera a instrução (palavra de 32 bits)
        instrucao = self.memoria.load(endereco) 
        # Armazena a instrução recuperada no Registrador de Instrução (IR) para processamento
        self._ir_set(instrucao)                 
        # Retorna a instrução buscada
        return instrucao

    def decodificar(self):
        """Etapa ID (Instruction Decode): Interpreta a instrução e busca os valores dos operandos."""
        # Lê a instrução que está armazenada no IR
        instrucao = self._ir_get() 
        
        # Extrai os bits 31-24 para obter o Opcode (código da operação)
        opcode = (instrucao >> 24) & 0xFF
        # Extrai os bits 23-16 para obter o índice do registrador RA (destino ou operando 1)
        ra_idx = (instrucao >> 16) & 0xFF
        # Extrai os bits 15-8 para obter o índice do registrador RB (operando 2)
        rb_idx = (instrucao >> 8) & 0xFF
        # Extrai os bits 7-0 para obter o índice do registrador RC (ou parte de endereço/imediato)
        rc_idx = instrucao & 0xFF
        # Extrai os 24 bits menos significativos para saltos longos (Jumps)
        end24 = instrucao & 0xFFFFFF        
        # Extrai os 16 bits menos significativos para constantes (imediato de 16 bits)
        const16 = (instrucao >> 8) & 0xFFFF 
        
        # Inicializa variáveis para os valores dos registradores RA e RB
        val_ra = 0
        val_rb = 0
        # Se o índice RA for válido (menor que 32), busca seu valor no banco de registradores
        if ra_idx < 32: val_ra = self.registradores.load(ra_idx) 
        # Se o índice RB for válido (menor que 32), busca seu valor no banco de registradores
        if rb_idx < 32: val_rb = self.registradores.load(rb_idx) 

        # Retorna um dicionário contendo todas as informações decodificadas necessárias para a execução
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
        """Etapa EX/MEM/WB: Executa a operação, acessa memória e grava resultados."""
        # Recupera o opcode do dicionário decodificado
        op = dec['opcode']
        # Recupera o valor do registrador RA
        val_ra = dec['val_ra']
        # Recupera o valor do registrador RB
        val_rb = dec['val_rb']
        # Recupera o índice RC (usado como destino ou endereço de salto condicional)
        rc = dec['rc_idx'] 
        # Recupera a constante de 16 bits
        const16 = dec['const16']
        # Recupera o endereço de 24 bits para saltos incondicionais
        end24 = dec['end24']
        
        # Inicializa variável para o resultado a ser gravado (Write Back)
        wb_result = None
        # Define flag para controlar se haverá gravação em registrador ao final
        realizar_wb = False
        # Define o registrador de destino padrão como sendo RC
        wb_destino = rc

        # --- OPERAÇÕES ARITMÉTICAS E LÓGICAS (ALU) ---
        if op == 1: # Instrução ADD (Soma)
            # Calcula a soma de RA e RB
            res = val_ra + val_rb
            # Ajusta o resultado para 32 bits
            wb_result = res & 0xFFFFFFFF
            # Atualiza flags de estado (Zero, Neg, Carry, Overflow)
            self._atualizar_flags(res, val_ra, val_rb, 'add')
            # Marca para gravar o resultado
            realizar_wb = True
        elif op == 2: # Instrução SUB (Subtração)
            # Calcula a subtração RA - RB
            res = val_ra - val_rb
            # Ajusta para 32 bits
            wb_result = res & 0xFFFFFFFF
            # Atualiza flags de estado para subtração
            self._atualizar_flags(res, val_ra, val_rb, 'sub')
            # Marca para gravar
            realizar_wb = True
        elif op == 3: # Instrução ZEROS (Zera registrador)
            # Define resultado como 0
            wb_result = 0
            # Atualiza flags (Zero será 1)
            self._atualizar_flags(0, 0, 0, 'logic')
            # Marca para gravar
            realizar_wb = True
        elif op == 4: # Instrução XOR (Ou Exclusivo Bit a Bit)
            # Calcula XOR entre RA e RB
            wb_result = val_ra ^ val_rb
            # Atualiza flags lógicas
            self._atualizar_flags(wb_result, 0, 0, 'logic')
            # Marca para gravar
            realizar_wb = True
        elif op == 5: # Instrução OR (Ou Lógico Bit a Bit)
            # Calcula OR entre RA e RB
            wb_result = val_ra | val_rb
            # Atualiza flags lógicas
            self._atualizar_flags(wb_result, 0, 0, 'logic')
            # Marca para gravar
            realizar_wb = True
        elif op == 6: # Instrução NOT (Inversão Bit a Bit)
            # Inverte os bits de RA e aplica máscara de 32 bits
            wb_result = (~val_ra) & 0xFFFFFFFF
            # Atualiza flags lógicas
            self._atualizar_flags(wb_result, 0, 0, 'logic')
            # Marca para gravar
            realizar_wb = True
        elif op == 7: # Instrução AND (E Lógico Bit a Bit)
            # Calcula AND entre RA e RB
            wb_result = val_ra & val_rb
            # Atualiza flags lógicas
            self._atualizar_flags(wb_result, 0, 0, 'logic')
            # Marca para gravar
            realizar_wb = True
            
        # --- OPERAÇÕES DE DESLOCAMENTO (SHIFTS) ---
        elif op == 8 or op == 10: # Instruções ASL/LSL (Shift à Esquerda)
            # Define a quantidade de shift (apenas os 5 bits menos significativos de RB)
            shift = val_rb & 0x1F
            # Realiza o shift à esquerda e mascara para 32 bits
            wb_result = (val_ra << shift) & 0xFFFFFFFF
            # Atualiza flags lógicas
            self._atualizar_flags(wb_result, 0, 0, 'logic')
            # Marca para gravar
            realizar_wb = True
        elif op == 9: # Instrução ASR (Shift Aritmético à Direita - preserva sinal)
            # Define quantidade de shift
            shift = val_rb & 0x1F
            # Se o bit de sinal for 1 (negativo), preenche os bits superiores com 1
            if (val_ra >> 31) & 1:
                mask = (0xFFFFFFFF << (32 - shift)) & 0xFFFFFFFF
                wb_result = (val_ra >> shift) | mask
            else:
                # Se positivo, faz shift normal
                wb_result = (val_ra >> shift)
            # Atualiza flags lógicas
            self._atualizar_flags(wb_result, 0, 0, 'logic')
            # Marca para gravar
            realizar_wb = True
        elif op == 11: # Instrução LSR (Shift Lógico à Direita - preenche com 0)
            # Define quantidade de shift
            shift = val_rb & 0x1F
            # Realiza shift lógico (sem preservar sinal)
            wb_result = (val_ra >> shift)
            # Atualiza flags lógicas
            self._atualizar_flags(wb_result, 0, 0, 'logic')
            # Marca para gravar
            realizar_wb = True
        elif op == 12: # Instrução PASSA (Move valor de RA para destino)
            # Apenas copia o valor de RA
            wb_result = val_ra
            # Atualiza flags lógicas
            self._atualizar_flags(wb_result, 0, 0, 'logic')
            # Marca para gravar
            realizar_wb = True

        # --- OPERAÇÕES COM CONSTANTES E MEMÓRIA ---
        elif op == 14: # Instrução LCL_MSB (Carrega constante nos 16 bits superiores)
            # Lê o valor atual do registrador de destino
            rc_atual = self.registradores.load(rc)
            # Combina a constante (shiftada) com a parte inferior do valor atual
            wb_result = ((const16 << 16) & 0xFFFF0000) | (rc_atual & 0xFFFF)
            # Marca para gravar
            realizar_wb = True
        elif op == 15: # Instrução LCL_LSB (Carrega constante nos 16 bits inferiores)
            # Lê o valor atual do registrador de destino
            rc_atual = self.registradores.load(rc)
            # Combina a parte superior atual com a constante nova
            wb_result = (rc_atual & 0xFFFF0000) | (const16 & 0xFFFF)
            # Marca para gravar
            realizar_wb = True
        elif op == 16: # Instrução LOAD (Carrega da memória para registrador)
            # Lê da memória no endereço contido em RA
            wb_result = self.memoria.load(val_ra)
            # Marca para gravar no registrador destino
            realizar_wb = True
        elif op == 17: # Instrução STORE (Grava de registrador para memória)
            # Escreve o valor de RA na memória, no endereço indicado por RC (registrador)
            self.memoria.store(self.registradores.load(rc), val_ra)
            # Imprime log da operação de memória
            print(f"    > [MEM] Mem[{self.registradores.load(rc)}] <- {val_ra}")

        # --- CONTROLE DE FLUXO (BRANCHES E JUMPS) ---
        elif op == 18: # Instrução JAL (Jump And Link - Salto com retorno)
            # Salva o PC atual (endereço de retorno)
            pc_ret = self._pc_get()
            # Grava o endereço de retorno no registrador R31
            self.registradores.read(31, pc_ret)
            # Imprime log da operação JAL
            print(f"    > [WB] JAL: R31 <- {pc_ret}")
            # Atualiza o PC para o endereço de salto (24 bits)
            self._pc_set(end24)
        elif op == 19: # Instrução JR (Jump Register - Retorno de função)
            # Atualiza o PC com o endereço contido no registrador RC
            self._pc_set(self.registradores.load(rc))
        
        # Saltos condicionais: verificam condição entre RA e RB e saltam para endereço em RC
        elif op == 20: # Instrução BEQ (Branch if Equal)
            # Se RA for igual a RB, salta para endereço em RC
            if val_ra == val_rb: self._pc_set(rc)
        elif op == 21: # Instrução BNE (Branch if Not Equal)
            # Se RA for diferente de RB, salta para endereço em RC
            if val_ra != val_rb: self._pc_set(rc)
        elif op == 22: # Instrução J (Jump Incondicional)
            # Salta incondicionalmente para o endereço de 24 bits
            self._pc_set(end24) 

        # --- NOVAS INSTRUÇÕES EXTRAS ---
        elif op == 23: # Instrução MUL (Multiplicação)
            # Multiplica RA por RB e trunca para 32 bits
            wb_result = (val_ra * val_rb) & 0xFFFFFFFF
            # Atualiza flags lógicas
            self._atualizar_flags(val_ra * val_rb, val_ra, val_rb, 'logic')
            # Marca para gravar
            realizar_wb = True
        elif op == 24: # Instrução DIV (Divisão Inteira)
            # Verifica divisão por zero antes de calcular
            if val_rb != 0: wb_result = (val_ra // val_rb) & 0xFFFFFFFF
            else: wb_result = 0 # Define 0 se divisão por zero (tratamento simples)
            # Atualiza flags lógicas
            self._atualizar_flags(wb_result, 0, 0, 'logic')
            # Marca para gravar
            realizar_wb = True
        elif op == 25: # Instrução MOD (Módulo/Resto)
            # Verifica divisão por zero
            if val_rb != 0: wb_result = (val_ra % val_rb) & 0xFFFFFFFF
            else: wb_result = 0
            # Atualiza flags lógicas
            self._atualizar_flags(wb_result, 0, 0, 'logic')
            # Marca para gravar
            realizar_wb = True
        elif op == 26: # Instrução NEG (Negação Aritmética)
            # Inverte o sinal do valor em RA
            res = -val_ra
            wb_result = res & 0xFFFFFFFF
            # Atualiza flags de subtração
            self._atualizar_flags(res, val_ra, 0, 'sub')
            # Marca para gravar
            realizar_wb = True
        elif op == 27: # Instrução INC (Incremento)
            # Adiciona 1 ao valor de RA
            res = val_ra + 1
            wb_result = res & 0xFFFFFFFF
            # Atualiza flags de soma
            self._atualizar_flags(res, val_ra, 1, 'add')
            # Marca para gravar
            realizar_wb = True
        elif op == 28: # Instrução DEC (Decremento)
            # Subtrai 1 do valor de RA
            res = val_ra - 1
            wb_result = res & 0xFFFFFFFF
            # Atualiza flags de subtração
            self._atualizar_flags(res, val_ra, 1, 'sub')
            # Marca para gravar
            realizar_wb = True
        
        # Condicionais extras
        elif op == 29: # Instrução BGT (Branch if Greater Than)
            # Se RA > RB, salta para endereço em RC
            if val_ra > val_rb: self._pc_set(rc)
        elif op == 30: # Instrução BLT (Branch if Less Than)
            # Se RA < RB, salta para endereço em RC
            if val_ra < val_rb: self._pc_set(rc)

        # --- ESTÁGIO DE WRITE BACK (WB) ---
        # Verifica se deve gravar e se o registrador de destino é válido (R0-R31)
        if realizar_wb and wb_destino < 32:
            # Escreve o resultado calculado no registrador de destino
            self.registradores.read(wb_destino, wb_result)
            # Exibe log da gravação
            print(f"    > [WB] R{wb_destino} <- {wb_result}")

    def executar_passo(self):
        """Gerencia o ciclo completo de uma instrução: Busca -> Decodifica -> Executa."""
        # Se o processador estiver marcado como parado (HALT), interrompe o passo
        if self.parado: return False
        
        # 1. Fetch: Busca a instrução na memória e coloca no IR
        self.buscar_instrucao()
        
        # 2. Decode: Decodifica o IR para entender a operação e operandos
        dec = self.decodificar()
        
        # Incrementa o PC para a próxima instrução
        # Realizado antes da execução para que saltos (Jumps) possam sobrescrever o PC se necessário
        pc_atual = self._pc_get()
        self._pc_set((pc_atual + 1) & 0xFFFFFFFF)
        
        # 3. Execute: Realiza a operação da ALU, acesso à memória ou salto
        self.executar_instrucao(dec)
        
        # Retorna os dados da instrução processada para logs ou verificações
        return dec

    def executar_programa(self):
        """Loop principal que executa o simulador até encontrar HALT ou limite de ciclos."""
        # Exibe cabeçalho de início de execução
        print("\n=== Iniciando execução ===\n")
        
        # Inicializa contador de ciclos para evitar loops infinitos
        ciclo = 0
        # Executa enquanto não estiver parado e não atingir 1000 ciclos
        while not self.parado and ciclo < 1000:
            try:
                # Executa um ciclo completo de instrução
                res = self.executar_passo()
                
                # Verifica se a instrução foi HALT (Opcode 255)
                if res and res['opcode'] == 255: 
                    # Exibe mensagem de parada e marca flag parado
                    print(f"Ciclo {ciclo}: HALT encontrado.")
                    self.parado = True
                    break
                elif res:
                    # Exibe log do ciclo atual com Opcode e valor do PC
                    print(f"Ciclo {ciclo}: Opcode={res['opcode']:02x} PC={self._pc_get():04x}")
                
                # Incrementa contador de ciclos
                ciclo += 1
            except Exception as e:
                # Captura e exibe qualquer erro de execução, interrompendo o loop
                print(f"✗ Erro na execução: {e}")
                break
        
        # Se atingiu o limite de ciclos, avisa o usuário
        if ciclo >= 1000:
            print("⚠ Limite de ciclos atingido!")
        
        # Ao final, exibe o estado dos registradores e PC
        self.estado()

    def estado(self):
        # Exibe cabeçalho do estado final
        print("\n=== Estado Final ===")
        # Mostra valor final do PC em binário e decimal
        print(f"PC: {self._pc_get():08b} (Dec: {self._pc_get()})")
        # Mostra valor final do IR em binário
        print(f"IR: {self._ir_get():032b}")

        # Exibe cabeçalho dos registradores
        print("\n--- Registradores ---")
        # Itera sobre o banco de registradores para exibição
        tem_valor = False
        for i, valor in enumerate(self.registradores.regs):
            # Filtra apenas registradores com valor diferente de zero para limpeza visual
            if valor != 0:
                # Exibe índice do registrador, valor decimal e valor hexadecimal
                print(f"R{i:<2}: {valor:<10} (Hex: 0x{valor:X})")
                tem_valor = True
        
        # Caso nenhum registrador tenha valor, informa o usuário
        if not tem_valor:
            print("(Todos os registradores estão zerados)")