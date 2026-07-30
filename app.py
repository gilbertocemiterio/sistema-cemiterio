from flask import Flask, render_template, request, jsonify
from supabase import create_client, Client
import datetime
import os

app = Flask(__name__)

# --- CONFIGURAÇÃO DO SUPABASE ---
SUPABASE_URL = "https://gbupmlhrihhyirwnrjtz.supabase.co"
SUPABASE_KEY = "sb_publishable_opFBH512ka6va3taMRnUKg_ayugnLeF"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def index():
    return render_template('agendaonline.html')

@app.route('/api/agendamentos', methods=['GET'])
def api_listar():
    data_filtro = request.args.get('data', '')
    try:
        response = supabase.table("agendamentos").select("*").eq("data", data_filtro).execute()
        return jsonify(response.data)
    except Exception as e:
        print("Erro ao buscar:", e)
        return jsonify([])

@app.route('/api/agendamentos', methods=['POST'])
def api_salvar():
    dados = request.json
    try:
        modo = dados.get('modo')
        reg_id = dados.get('id')
        data = dados.get('data')
        hora = dados.get('hora')
        cem = dados.get('cem')

        verificacao = supabase.table("agendamentos").select("*").eq("data", data).eq("hora", hora).eq("cem", cem).execute()
        registros_existentes = verificacao.data

        if modo == 'sim' and reg_id:
            registros_existentes = [r for r in registros_existentes if str(r['id']) != str(reg_id)]

        if len(registros_existentes) > 0:
            return jsonify({"sucesso": False, "erro": f"O horario {hora} no Cemiterio {cem} ja esta ocupado!"})

        payload = {
            "data": data,
            "hora": hora,
            "cem": cem,
            "falecido": dados.get('falecido'),
            "lote": dados.get('lote'),
            "resp": dados.get('resp'),
            "tel": dados.get('tel'),
            "funeraria": dados.get('funeraria'),
            "obito": dados.get('obito'),
            "taxa": dados.get('taxa'),
            "abert": dados.get('abert'),
            "sit_terreno": dados.get('sit_terreno'),
            "doc_compra": dados.get('doc_compra'),
            "cpf": dados.get('cpf'),
            "est_civil": dados.get('est_civil'),
            "parentesco": dados.get('parentesco'),
            "endereco": dados.get('endereco'),
            "social": dados.get('social')
        }

        if modo == 'sim' and reg_id:
            supabase.table("agendamentos").update(payload).eq("id", reg_id).execute()
        else:
            agora = datetime.datetime.now()
            payload["data_criacao"] = agora.strftime("%d/%m/%Y as %H:%M:%S")
            supabase.table("agendamentos").insert(payload).execute()

        return jsonify({"sucesso": True})
    except Exception as e:
        print("Erro ao salvar no Supabase:", e)
        return jsonify({"sucesso": False, "erro": str(e)})

@app.route('/api/agendamentos/<int:reg_id>', methods=['DELETE'])
def api_excluir(reg_id):
    try:
        supabase.table("agendamentos").delete().eq("id", reg_id).execute()
        return jsonify({"sucesso": True})
    except Exception as e:
        print("Erro ao excluir:", e)
        return jsonify({"sucesso": False})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
