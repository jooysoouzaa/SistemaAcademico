# ==============================================================================
# SISTEMA DE GERENCIAMENTO ACADÊMICO – VERSÃO FINAL
# Aluna: Joyce de Souza Araujo
# Curso: Big Data e Inteligência Analítica
# Disciplina: Raciocínio Computacional
# Data: 07/07/2025
# ------------------------------------------------------------------------------
"""
Funcionalidades:
• CRUD completo (incluir, listar, atualizar, excluir) para:
    – Estudantes      (codigo, nome)
    – Professores     (codigo, nome, cpf)
    – Disciplinas     (codigo, nome)
    – Turmas          (codigo, professor, disciplina)
    – Matrículas      (turma, estudante)

• Persistência de dados em arquivos JSON (um arquivo por módulo)
• Validação de códigos duplicados e chaves estrangeiras (turmas/matrículas)
• Tratamento de exceções (entrada de dados, leitura/gravação de arquivos)
• Menus navegáveis por while/if‑elif e funções reutilizáveis
"""
# ==============================================================================
import json
import os
from typing import List, Dict, Any, Tuple, Union

# ---------- Configuração dos Módulos ----------
ENTITIES: Dict[str, Dict[str, Any]] = {
    "Estudantes": {
        "filename": "estudantes.json",
        "fields": [
            ("codigo", int, "Código do estudante"),
            ("nome", str, "Nome do estudante")
        ],
        "primary": ("codigo",),
    },
    "Professores": {
        "filename": "professores.json",
        "fields": [
            ("codigo", int, "Código do professor"),
            ("nome", str, "Nome do professor"),
            ("cpf", str, "CPF do professor")
        ],
        "primary": ("codigo",),
    },
    "Disciplinas": {
        "filename": "disciplinas.json",
        "fields": [
            ("codigo", int, "Código da disciplina"),
            ("nome", str, "Nome da disciplina")
        ],
        "primary": ("codigo",),
    },
    "Turmas": {
        "filename": "turmas.json",
        "fields": [
            ("codigo", int, "Código da turma"),
            ("professor", int, "Código do professor"),
            ("disciplina", int, "Código da disciplina")
        ],
        "primary": ("codigo",),
    },
    "Matrículas": {
        "filename": "matriculas.json",
        "fields": [
            ("turma", int, "Código da turma"),
            ("estudante", int, "Código do estudante")
        ],
        "primary": ("turma", "estudante"),  # chave composta
    },
}

# ---------- Utilidades de Arquivo ----------

def load_data(filename: str) -> List[Dict[str, Any]]:
    """Carrega a lista de registros do arquivo JSON correspondente."""
    if not os.path.exists(filename):
        return []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        print(f"[Aviso] Falha ao ler {filename}. Iniciando lista vazia.")
        return []


def save_data(filename: str, data: List[Dict[str, Any]]):
    """Salva a lista de registros no arquivo JSON correspondente."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f"[Erro] Não foi possível salvar em {filename}: {e}")


# ---------- Carregamento Inicial ----------
DB: Dict[str, List[Dict[str, Any]]] = {
    entity: load_data(cfg["filename"]) for entity, cfg in ENTITIES.items()
}

# ---------- Funções Genericas de CRUD ----------

def input_int(prompt: str) -> int:
    """Lê um inteiro com validação."""
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Por favor, digite um número inteiro válido.")


def registro_existe(entity: str, keys: Tuple[Any, ...]) -> bool:
    """Verifica se já existe um registro com a(s) chave(s) primária(s)."""
    cfg = ENTITIES[entity]
    primaries = cfg["primary"]
    for reg in DB[entity]:
        if all(reg[p] == key for p, key in zip(primaries, keys)):
            return True
    return False


def obter_registro(entity: str, keys: Tuple[Any, ...]) -> Tuple[int, Dict[str, Any]]:
    """Retorna o índice e o registro que possui as chaves fornecidas (ou -1, None)."""
    cfg = ENTITIES[entity]
    primaries = cfg["primary"]
    for idx, reg in enumerate(DB[entity]):
        if all(reg[p] == key for p, key in zip(primaries, keys)):
            return idx, reg
    return -1, None


def solicitar_campos(entity: str, atualizar=False, existente: Dict[str, Any] = None) -> Dict[str, Any]:
    """Solicita ao usuário o preenchimento dos campos definidos para a entidade."""
    dados = {}
    for nome, tipo, label in ENTITIES[entity]["fields"]:

        while True:
            valor_bruto = input(f"{label}" + (f" [{existente[nome]}]" if atualizar else "") + ": ")
            if atualizar and valor_bruto.strip() == "":
                dados[nome] = existente[nome]
                break
            # Conversão para tipo correto
            try:
                valor = tipo(valor_bruto) if tipo is int else valor_bruto.strip()
                dados[nome] = valor
                break
            except ValueError:
                print(f"Valor inválido para {label}. Tente novamente.")
    return dados


def incluir(entity: str):
    cfg = ENTITIES[entity]
    primaries = cfg["primary"]
    # Solicitar campos
    dados = solicitar_campos(entity)

    # Verificar duplicidade
    chave = tuple(dados[p] for p in primaries)
    if registro_existe(entity, chave):
        print("[Erro] Registro com a mesma chave já existe.")
        return


    if entity == "Turmas":
        if not registro_existe("Professores", (dados["professor"],)):
            print("[Erro] Professor não encontrado.")
            return
        if not registro_existe("Disciplinas", (dados["disciplina"],)):
            print("[Erro] Disciplina não encontrada.")
            return
    if entity == "Matrículas":
        if not registro_existe("Turmas", (dados["turma"],)):
            print("[Erro] Turma não encontrada.")
            return
        if not registro_existe("Estudantes", (dados["estudante"],)):
            print("[Erro] Estudante não encontrado.")
            return

    DB[entity].append(dados)
    save_data(cfg["filename"], DB[entity])
    print("Registro incluído com sucesso!")


def listar(entity: str):
    registros = DB[entity]
    if not registros:
        print("Nenhum registro cadastrado.")
        return
    print(f"\n--- Lista de {entity} ---")
    primaries = ENTITIES[entity]["primary"]
    for reg in registros:
  
        detalhes = ", ".join(f"{k}={v}" for k, v in reg.items())
        print(detalhes)
    print("----------------------------")


def atualizar(entity: str):
    cfg = ENTITIES[entity]
    primaries = cfg["primary"]
  
    chaves = []
    for p in primaries:
        chaves.append(input_int(f"Informe {p}: "))
    idx, reg_encontrado = obter_registro(entity, tuple(chaves))
    if idx == -1:
        print("Registro não encontrado.")
        return

    print("Preencha novos valores (Enter para manter o atual)")
    novos_dados = solicitar_campos(entity, atualizar=True, existente=reg_encontrado)

    # Se chave primária alterar, validar duplicidade ou relacionamentos
    nova_chave = tuple(novos_dados[p] for p in primaries)
    if nova_chave != tuple(chaves) and registro_existe(entity, nova_chave):
        print("[Erro] Já existe registro com a nova chave informada.")
        return

    # Atualizar lista e salvar
    DB[entity][idx] = novos_dados
    save_data(cfg["filename"], DB[entity])
    print("Registro atualizado com sucesso!")


def excluir(entity: str):
    cfg = ENTITIES[entity]
    primaries = cfg["primary"]
    chaves = []
    for p in primaries:
        chaves.append(input_int(f"Informe {p}: "))
    idx, _ = obter_registro(entity, tuple(chaves))
    if idx == -1:
        print("Registro não encontrado.")
        return

  
    if entity in ("Professores", "Disciplinas"):
        # Verifica se existe alguma turma com esse professor/disciplina
        depend_field = "professor" if entity == "Professores" else "disciplina"
        if any(t[depend_field] == chaves[0] for t in DB["Turmas"]):
            print(f"[Erro] Não é possível excluir: existem turmas vinculadas a este {entity[:-1].lower()}.")
            return
    if entity == "Estudantes":
        if any(m["estudante"] == chaves[0] for m in DB["Matrículas"]):
            print("[Erro] Não é possível excluir: existem matrículas para este estudante.")
            return
    if entity == "Turmas":
        if any(m["turma"] == chaves[0] for m in DB["Matrículas"]):
            print("[Erro] Não é possível excluir: existem matrículas nesta turma.")
            return

    DB[entity].pop(idx)
    save_data(cfg["filename"], DB[entity])
    print("Registro excluído com sucesso!")


# ---------- Menus ----------

def menu_operacoes(entity: str):
    while True:
        print(f"\n--- MENU DE {entity.upper()} ---")
        print("1. Incluir")
        print("2. Listar")
        print("3. Atualizar")
        print("4. Excluir")
        print("5. Voltar ao menu principal")
        opcao = input("Escolha uma opção: ")
        if opcao == "1":
            incluir(entity)
        elif opcao == "2":
            listar(entity)
        elif opcao == "3":
            atualizar(entity)
        elif opcao == "4":
            excluir(entity)
        elif opcao == "5":
            break
        else:
            print("Opção inválida.")


def menu_principal():
    opcoes = list(ENTITIES.keys())
    while True:
        print("\n=== MENU PRINCIPAL ===")
        for idx, ent in enumerate(opcoes, 1):
            print(f"{idx}. {ent}")
        print("9. Sair")
        escolha = input("Escolha uma opção: ")
        if escolha == "9":
            print("Saindo do sistema... Até mais!")
            break
        try:
            escolha_int = int(escolha)
            if 1 <= escolha_int <= len(opcoes):
                menu_operacoes(opcoes[escolha_int - 1])
            else:
                print("Opção inválida.")
        except ValueError:
            print("Por favor, digite um número válido.")


# ---------- Execução ----------
if __name__ == "__main__":
    menu_principal()
