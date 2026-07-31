from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from supabase import create_client, Client
import datetime
import os

app = Flask(__name__)
app.secret_key = "sua_chave_secreta_super_segura" 

# --- CONFIGURAÇÃO DO SUPABASE ---
SUPABASE_URL = "https://gbupmlhrihhyirwnrjtz.supabase.co"
SUPABASE_KEY = "sb_publishable_opFBH512ka6va3taMRnUKg_ayugnLeF"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def index():
    return render_template('index.html')

# --- ROTA DE LOGIN ATUALIZADA (CONSULTA O BANCO) ---
@app.route('/login', methods=['POST'])
def login():
    dados = request.json
    identificacao = dados.get('identificacao') # Pode ser CPF ou E-mail
    senha_digitada = dados.get('senha')
    
    try:
        # Busca o usuário pelo CPF ou E-mail
        response = supabase.table("usuarios").select("*").or_(f"cpf.eq.{identificacao},email.eq.{identificacao}").execute()
        usuarios = response.data

        if len(usuarios) > 0:
            usuario = usuarios[0]
            if usuario['senha'] == senha_digitada:
                session['logado'] = True
                session['nome_usuario'] = usuario['nome']
                session['nivel_usuario'] = usuario['nivel']
                return jsonify({"sucesso": True})
            else:
                return jsonify({"sucesso": False, "erro": "Senha incorreta!"})
        else:
            return jsonify({"sucesso": False, "erro": "Usuário não encontrado!"})
    except Exception as e:
        print("Erro no login:", e)
        return jsonify({"sucesso": False, "erro": "Erro ao conectar com o banco."})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    if session.get('logado'):
        return render_template('admin.html')
    else:
        return redirect(url_for('index'))

# --- ROTAS DE GERENCIAMENTO DE USUÁRIOS (APENAS MASTER) ---
@app.route('/api/usuarios', methods=['GET'])
def api_listar_usuarios():
    try:
        response = supabase.table("usuarios").select("id, nome, cpf, email, nivel").execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify([])

@app.route('/api/usuarios', methods=['POST'])
def api_salvar_usuario():
    if session.get('nivel_usuario') != 'MASTER':
        return jsonify({"sucesso": False, "erro": "Acesso negado. Apenas o Master pode cadastrar."})
    
    dados = request.json
    try:
        payload = {
            "nome": dados.get('nome'),
            "cpf": dados.get('cpf'),
            "email": dados.get('email'),
            "senha": dados.get('senha'),
            "nivel": dados.get('nivel', 'COMUM')
        }
        supabase.table("usuarios").insert(payload).execute()
        return jsonify({"sucesso": True})
    except Exception as e:
        return jsonify({"sucesso": False, "erro": "Erro ao cadastrar (CPF já cadastrado?)."})

@app.route('/api/usuarios/<int:user_id>', methods=['DELETE'])
def api_excluir_usuario(user_id):
    if session.get('nivel_usuario') != 'MASTER':
        return jsonify({"sucesso": False, "erro": "Acesso negado."})
    try:
        supabase.table("usuarios").delete().eq("id", user_id).execute()
        return jsonify({"sucesso": True})
    except Exception as e:
        return jsonify({"sucesso": False})

# --- ROTAS DA API DE AGENDAMENTOS ---
@app.route('/api/agendamentos', methods=['GET'])
def api_listar():
    data_filtro = request.args.get('data', '')
    try:
        response = supabase.table("agendamentos").select("*").eq("data", data_filtro).execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify([])

@app.route('/api/agendamentos', methods=['POST'])
def api_salvar():
    if not session.get('logado'):
        return jsonify({"sucesso": False, "erro": "Usuário não autenticado."})
    
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
            "data": data, "hora": hora, "cem": cem,
            "falecido": dados.get('falecido'), "lote": dados.get('lote'),
            "resp": dados.get('resp'), "tel": dados.get('tel'),
            "funeraria": dados.get('funeraria'), "obito": dados.get('obito'),
            "taxa": dados.get('taxa'), "abert": dados.get('abert'),
            "sit_terreno": dados.get('sit_terreno'), "doc_compra": dados.get('doc_compra'),
            "cpf": dados.get('cpf'), "est_civil": dados.get('est_civil'),
            "parentesco": dados.get('parentesco'), "endereco": dados.get('endereco'),
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
        return jsonify({"sucesso": False, "erro": str(e)})

@app.route('/api/agendamentos/<int:reg_id>', methods=['DELETE'])
def api_excluir(reg_id):
    if not session.get('logado'):
        return jsonify({"sucesso": False})
    try:
        supabase.table("agendamentos").delete().eq("id", reg_id).execute()
        return jsonify({"sucesso": True})
    except Exception as e:
        return jsonify({"sucesso": False})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
