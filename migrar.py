import os
from supabase import create_client, Client

# --- CONFIGURAÇÃO DO SUPABASE (Mesmas chaves do app.py) ---
SUPABASE_URL = "https://gbupmlhrihhyirwnrjtz.supabase.co"
SUPABASE_KEY = "sb_publishable_opFBH512ka6va3taMRnUKg_ayugnLeF"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Caminho provável do seu arquivo de texto antigo no Google Drive
caminho_antigo = r"C:\Users\gilbertosc\Meu Drive\BANCO AGENDA CEMITERIO\dados_agenda.txt"
# Se o seu arquivo estiver em outro caminho, basta alterar a linha acima entre as aspas.

def migrar_dados():
    if not os.path.exists(caminho_antigo):
        print(f"Arquivo antigo não encontrado no caminho: {caminho_antigo}")
        print("Verifique o caminho exato do seu 'dados_agenda.txt' e atualize no script.")
        return

    print("Lendo o arquivo antigo...")
    with open(caminho_antigo, "r", encoding="utf-8", errors="ignore") as f:
        conteudo = f.read()

    conteudo = conteudo.replace("\r\n", "\n").replace("\r", "\n")
    blocos = conteudo.split("---REGISTRO---")
    
    total_migrados = 0

    for bloco in blocos:
        bloco = bloco.strip()
        if bloco != "":
            linhas = bloco.split("\n")
            obj = {}
            for linha in linhas:
                idx = linha.find("=")
                if idx > 0:
                    chave = linha[:idx].strip()
                    valor = linha[idx+1:].strip()
                    obj[chave] = valor

            # Mapeia as chaves antigas para as colunas da tabela nova do Supabase
            payload = {
                "data": obj.get("data", ""),
                "hora": obj.get("hora", ""),
                "cem": obj.get("cem", ""),
                "falecido": obj.get("falecido", "-"),
                "lote": obj.get("lote", "-"),
                "resp": obj.get("resp", "-"),
                "tel": obj.get("tel", "-"),
                "funeraria": obj.get("funeraria", "-"),
                "obito": obj.get("obito", "N"),
                "taxa": obj.get("taxa", "N"),
                "abert": obj.get("abert", "PENDENTE"),
                "sit_terreno": obj.get("sitTerreno", "EXISTENTE"),
                "doc_compra": obj.get("docCompra", "N"),
                "cpf": obj.get("cpf", "-"),
                "est_civil": obj.get("estCivil", "SOLTEIRO(A)"),
                "parentesco": obj.get("parentesco", "-"),
                "endereco": obj.get("endereco", "-"),
                "social": obj.get("social", "N"),
                "data_criacao": obj.get("dataCriacao", "-")
            }

            if payload["data"] and payload["hora"] and payload["cem"]:
                try:
                    supabase.table("agendamentos").insert(payload).execute()
                    total_migrados += 1
                    print(f"Migrado com sucesso: {payload['data']} - {payload['hora']} ({payload['cem']}) - {payload['falecido']}")
                except Exception as e:
                    print(f"Erro ao migrar registro de {payload['data']} {payload['hora']}: {e}")

    print(f"\n--- MIGRAÇÃO CONCLUÍDA! Total de registros enviados: {total_migrados} ---")

if __name__ == "__main__":
    migrar_dados()