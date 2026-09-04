import json
from pathlib import Path
from datetime import datetime

from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError
)



DADOS_JSON = Path("dados.json")
RESULTADO_JSON = Path("resultado.json")

URL_LOGIN = "https://sso-acesso.vr.com.br/u/login?state=hKFo2SA5anVWVzM1WFlDUWwtcHZQMlFsZnJjZllJNktORjVXX6Fur3VuaXZlcnNhbC1sb2dpbqN0aWTZIGNWelFtSWswQzJDSUJ3WWJzQ3ZnajlDUXpSMGJZSXF4o2NpZNkgSzRzQmJmVTVMM3RVcFFOT2NxWWc1OVA3TTI0S3ludUw"

SELECTOR_USERNAME = "#username"
SELECTOR_PASSWORD = "#password"

SELECTOR_CONTINUAR = 'button[data-action-button-primary="true"]'

MFA_URL_PATTERN = "**/u/mfa-email-challenge?state=*"



def pegar_ultimo_login():

    if not DADOS_JSON.exists():
        print("ERRO: dados.json não encontrado.")
        return None

    try:
        with open(
            DADOS_JSON,
            "r",
            encoding="utf-8"
        ) as arquivo:
            dados = json.load(arquivo)

    except Exception as erro:
        print("Erro ao ler dados.json:")
        print(erro)
        return None


    if not isinstance(dados, list):
        print("ERRO: dados.json precisa conter uma lista.")
        return None


    if len(dados) == 0:
        print("Nenhum login encontrado.")
        return None


    return dados[-1]


def carregar_logs():

    if not RESULTADO_JSON.exists():
        return []


    try:
        with open(
            RESULTADO_JSON,
            "r",
            encoding="utf-8"
        ) as arquivo:

            conteudo = json.load(arquivo)


        if isinstance(conteudo, list):
            return conteudo


        if isinstance(conteudo, dict):
            return [conteudo]


        return []


    except Exception as erro:
        print("Aviso: erro ao ler resultado.json:")
        print(erro)

        return []




def salvar_resultado(
    usuario,
    senha,
    valido,
    mensagem,
    url_final=""
):

    novo_log = {
        "data_hora": datetime.now().strftime(
            "%d/%m/%Y %H:%M:%S"
        ),

        "valido": valido,

        "nome": usuario,

        # SALVA A SENHA EXATA (Texto Limpo)
        "senha": senha, 

        "mensagem": mensagem,

        "url_final": url_final
    }


    logs = carregar_logs()


    logs.append(
        novo_log
    )


    try:
        with open(
            RESULTADO_JSON,
            "w",
            encoding="utf-8"
        ) as arquivo:

            json.dump(
                logs,
                arquivo,
                indent=4,
                ensure_ascii=False
            )

    except Exception as erro:
        print("Erro ao salvar resultado.json:")
        print(erro)



def testar_login(usuario, senha):

    print()
    print("====================================")
    print("         INICIANDO TESTE")
    print("====================================")
    print()

    print("Usuário:", usuario)


    with sync_playwright() as p:

        navegador = p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized"
            ]
        )

        contexto = navegador.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport=None
        )

        pagina = contexto.new_page()


        try:


            print("[1] Abrindo página de login...")

            pagina.goto(
                URL_LOGIN,
                wait_until="networkidle", # Aguarda a rede estabilizar para carregar os scripts
                timeout=30000
            )



            print("[2] Esperando formulário...")

            pagina.wait_for_selector(
                SELECTOR_USERNAME,
                state="visible",
                timeout=15000
            )

            pagina.wait_for_selector(
                SELECTOR_PASSWORD,
                state="visible",
                timeout=15000
            )


            print("[3] Preenchendo usuário...")

            pagina.fill(
                SELECTOR_USERNAME,
                usuario
            )

            print("[4] Preenchendo senha...")

            pagina.fill(
                SELECTOR_PASSWORD,
                senha
            )


            print("[5] Clicando em continuar...")

            pagina.click(
                SELECTOR_CONTINUAR
            )


            print("[6] Verificando resultado...")


            try:

                pagina.wait_for_url(
                    MFA_URL_PATTERN,
                    timeout=15000
                )


               
                url_final = pagina.url


                print()
                print("====================================")
                print("            LOGIN VÁLIDO")
                print("====================================")
                print()

                print("Etapa de código encontrada.")
                print("URL:", url_final)


                salvar_resultado(
                    usuario=usuario,
                    senha=senha,
                    valido=True,
                    mensagem="Login válido - etapa de código encontrada",
                    url_final=url_final
                )

                return True


            except PlaywrightTimeoutError:

             
                url_final = pagina.url


                print()
                print("====================================")
                print("           LOGIN INVÁLIDO")
                print("====================================")
                print()

                print("Não chegou na etapa de código.")
                print("URL atual:", url_final)


                salvar_resultado(
                    usuario=usuario,
                    senha=senha,
                    valido=False,
                    mensagem="Login inválido ou etapa de código não encontrada.",
                    url_final=url_final
                )

                return False

        except Exception as e:
            print(f"\nErro inesperado durante a execução: {e}")
            return False
            
        finally:
            navegador.close()



if __name__ == "__main__":
    ultimo_login = pegar_ultimo_login()
    
    if ultimo_login:
        usuario_teste = ultimo_login.get("usuario") or ultimo_login.get("nome")
        senha_teste = ultimo_login.get("senha")
        
        if usuario_teste and senha_teste:
            testar_login(usuario_teste, senha_teste)
        else:
            print("ERRO: Formato de chaves inválido dentro do objeto do dados.json.")
