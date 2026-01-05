import textwrap
from abc import ABC, abstractmethod
from datetime import datetime


def menu():
    menu = """\n
    ================ MENU ================
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [nc]\tNova conta
    [lc]\tListar contas
    [nu]\tNovo usuário
    [q]\tSair
    => """
    return input(textwrap.dedent(menu))


class Historico:
    def __init__(self):
        self.transacoes = []

    def adicionar_transacao(self, transacao: str):
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.transacoes.append(f"{timestamp} - {transacao}")

    def __str__(self):
        if not self.transacoes:
            return "Não foram realizadas movimentações."
        return "\n".join(self.transacoes)


class Transacao(ABC):
    @abstractmethod
    def registrar(self, conta):
        pass


class Deposito(Transacao):
    def __init__(self, valor: float):
        self.valor = valor

    def registrar(self, conta):
        sucesso = conta.depositar(self.valor)
        if sucesso:
            conta.historico.adicionar_transacao(f"Depósito: R$ {self.valor:.2f}")
        return sucesso


class Saque(Transacao):
    def __init__(self, valor: float):
        self.valor = valor

    def registrar(self, conta):
        sucesso = conta.sacar(self.valor)
        if sucesso:
            conta.historico.adicionar_transacao(f"Saque: R$ {self.valor:.2f}")
        return sucesso


class Cliente:
    def __init__(self, nome: str, data_nascimento: str, cpf: str, endereco: str):
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao: Transacao):
        if conta not in self.contas:
            print("\n@@@ Operação falhou! Conta não pertence ao cliente. @@@")
            return False
        return transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome: str, data_nascimento: str, cpf: str, endereco: str):
        super().__init__(nome, data_nascimento, cpf, endereco)


class Conta:
    def __init__(self, agencia: str, numero: int, cliente: Cliente):
        self.saldo = 0.0
        self.numero = numero
        self.agencia = agencia
        self.cliente = cliente
        self.historico = Historico()

    @classmethod
    def nova_conta(cls, cliente: Cliente, numero: int, agencia: str = "0001"):
        conta = cls(agencia=agencia, numero=numero, cliente=cliente)
        cliente.adicionar_conta(conta)
        return conta

    def depositar(self, valor: float) -> bool:
        if valor <= 0:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False
        self.saldo += valor
        print("\n=== Depósito realizado com sucesso! ===")
        return True

    def sacar(self, valor: float) -> bool:
        if valor <= 0:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False
        if valor > self.saldo:
            print("\n@@@ Operação falhou! Você não tem saldo suficiente. @@@")
            return False
        self.saldo -= valor
        print("\n=== Saque realizado com sucesso! ===")
        return True

    def exibir_extrato(self):
        print("\n================ EXTRATO ================")
        print(str(self.historico))
        print(f"\nSaldo:\t\tR$ {self.saldo:.2f}")
        print("==========================================")


class ContaCorrente(Conta):
    def __init__(self, agencia: str, numero: int, cliente: Cliente, limite: float = 500.0, limite_saques: int = 3):
        super().__init__(agencia, numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques
        self.numero_saques = 0

    @classmethod
    def nova_conta(cls, cliente: Cliente, numero: int, agencia: str = "0001", limite: float = 500.0, limite_saques: int = 3):
        conta = cls(agencia=agencia, numero=numero, cliente=cliente, limite=limite, limite_saques=limite_saques)
        cliente.adicionar_conta(conta)
        return conta

    def sacar(self, valor: float) -> bool:
        if valor <= 0:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False
        if valor > self.saldo:
            print("\n@@@ Operação falhou! Você não tem saldo suficiente. @@@")
            return False
        if valor > self.limite:
            print("\n@@@ Operação falhou! O valor do saque excede o limite. @@@")
            return False
        if self.numero_saques >= self.limite_saques:
            print("\n@@@ Operação falhou! Número máximo de saques excedido. @@@")
            return False
        self.saldo -= valor
        self.numero_saques += 1
        print("\n=== Saque realizado com sucesso! ===")
        return True

def criar_usuario(usuarios):
    cpf = input("Informe o CPF (somente número): ")
    if filtrar_usuario(cpf, usuarios):
        print("\n@@@ Já existe usuário com esse CPF! @@@")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")

    usuario = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco)
    usuarios.append(usuario)
    print("=== Usuário criado com sucesso! ===")


def filtrar_usuario(cpf, usuarios):
    usuarios_filtrados = [usuario for usuario in usuarios if usuario.cpf == cpf]
    return usuarios_filtrados[0] if usuarios_filtrados else None


def criar_conta(agencia, numero_conta, usuarios, contas):
    cpf = input("Informe o CPF do usuário: ")
    usuario = filtrar_usuario(cpf, usuarios)

    if usuario:
        conta = ContaCorrente.nova_conta(cliente=usuario, numero=numero_conta, agencia=agencia)
        contas.append(conta)
        print("\n=== Conta criada com sucesso! ===")
        return conta

    print("\n@@@ Usuário não encontrado, fluxo de criação de conta encerrado! @@@")


def listar_contas(contas):
    if not contas:
        print("\n@@@ Nenhuma conta cadastrada. @@@")
        return
    for conta in contas:
        linha = f"""\
            Agência:\t{conta.agencia}
            C/C:\t\t{conta.numero}
            Titular:\t{conta.cliente.nome}
        """
        print("=" * 100)
        print(textwrap.dedent(linha))


def buscar_conta_por_numero(numero, contas):
    contas_filtradas = [conta for conta in contas if conta.numero == numero]
    return contas_filtradas[0] if contas_filtradas else None


def selecionar_conta_do_cliente(usuario):
    if not usuario.contas:
        print("\n@@@ Usuário não possui contas. @@@")
        return None

    print("\nContas do usuário:")
    for conta in usuario.contas:
        print(f"- Número: {conta.numero} | Agência: {conta.agencia} | Saldo: R$ {conta.saldo:.2f}")

    try:
        numero = int(input("Informe o número da conta (C/C) desejada: "))
    except ValueError:
        print("\n@@@ Número de conta inválido. @@@")
        return None

    contas_filtradas = [c for c in usuario.contas if c.numero == numero]
    if not contas_filtradas:
        print("\n@@@ Conta não encontrada entre as contas do usuário. @@@")
        return None
    return contas_filtradas[0]


def main():
    AGENCIA = "0001"

    usuarios = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "d":
            cpf = input("Informe o CPF do titular: ")
            usuario = filtrar_usuario(cpf, usuarios)
            if not usuario:
                print("\n@@@ Usuário não encontrado. @@@")
                continue

            conta = selecionar_conta_do_cliente(usuario)
            if not conta:
                continue

            try:
                valor = float(input("Informe o valor do depósito: "))
            except ValueError:
                print("\n@@@ Valor inválido. @@@")
                continue

            deposito = Deposito(valor)
            usuario.realizar_transacao(conta, deposito)

        elif opcao == "s":
            cpf = input("Informe o CPF do titular: ")
            usuario = filtrar_usuario(cpf, usuarios)
            if not usuario:
                print("\n@@@ Usuário não encontrado. @@@")
                continue

            conta = selecionar_conta_do_cliente(usuario)
            if not conta:
                continue

            try:
                valor = float(input("Informe o valor do saque: "))
            except ValueError:
                print("\n@@@ Valor inválido. @@@")
                continue

            saque = Saque(valor)
            usuario.realizar_transacao(conta, saque)

        elif opcao == "e":
            cpf = input("Informe o CPF do titular: ")
            usuario = filtrar_usuario(cpf, usuarios)
            if not usuario:
                print("\n@@@ Usuário não encontrado. @@@")
                continue

            conta = selecionar_conta_do_cliente(usuario)
            if not conta:
                continue

            conta.exibir_extrato()

        elif opcao == "nu":
            criar_usuario(usuarios)

        elif opcao == "nc":
            numero_conta = len(contas) + 1
            criar_conta(AGENCIA, numero_conta, usuarios, contas)

        elif opcao == "lc":
            listar_contas(contas)

        elif opcao == "q":
            break

        else:
            print("Operação inválida, por favor selecione novamente a operação desejada.")


if __name__ == "__main__":
    main()
