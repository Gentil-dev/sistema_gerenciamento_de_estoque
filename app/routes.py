from flask import Blueprint, render_template, request, redirect, url_for, session
from app import db
from app.models import Produto
from dotenv import load_dotenv
import os

bp = Blueprint('routes', __name__)
load_dotenv()

@bp.route('/')
def home():
    return render_template('index.html')



#rota login gerente
@bp.route('/gerente', methods=['GET', 'POST'])
def gerente():
    if request.method == 'POST':
        senha_digitada = request.form['senha']
        senha_correta = os.getenv('GERENTE_SENHA')
        
        
        if senha_digitada == senha_correta:
            session['gerente_logado'] = True
            return redirect(url_for('routes.painel_gerente'))
        else:
            return render_template('login.html', erro='Senha incorreta. Tente novamente.') 
    return render_template('login.html')    

#painel gerente(protegido)
@bp.route('/painel')
def painel_gerente():
    if not session.get('gerente_logado'):
        return redirect(url_for('routes.gerente'))
    return render_template('painel.html')

@bp.route('/logout')
def logout():
    session.pop('gerente_logado', None)
    return redirect(url_for('routes.home'))

 
@bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if not session.get('gerente_logado'):
        return redirect(url_for('routes.gerente'))

    if request.method == 'POST':
        nome = request.form['nome']
        quantidade = request.form['quantidade']
        preco_unitario = request.form['preco_unitario']
        observacao = request.form['observacao']

        novo_produto = Produto(
            nome=nome,
            quantidade=int(quantidade),
            preco_unitario=float(preco_unitario),
            observacao=observacao
        )

        db.session.add(novo_produto)
        db.session.commit()
        registrar_historico("Cadastro de Produto", nome, quantidade)

        return redirect(url_for('routes.estoque'))

    return render_template('cadastro.html')

@bp.route('/entrada', methods=['GET', 'POST'])
def entrada():
    if not session.get('gerente_logado'):
        return redirect(url_for('routes.gerente'))

    produtos = Produto.query.all()

    if request.method == 'POST':
        produto_id = request.form['produto_id']
        quantidade_adicionada = int(request.form['quantidade'])

        produto = Produto.query.get(produto_id)
        if produto:
            produto.quantidade += quantidade_adicionada
            db.session.commit()
            registrar_historico("Entrada de Produto", produto.nome, quantidade_adicionada)  

        return redirect(url_for('routes.estoque'))

    return render_template('entrada.html', produtos=produtos)

@bp.route('/saida', methods=['GET', 'POST'])
def saida():
    if not session.get('gerente_logado'):
        return redirect(url_for('routes.gerente'))

    produtos = Produto.query.all()

    if request.method == 'POST':
        produto_id = request.form['produto_id']
        quantidade_removida = int(request.form['quantidade'])

        produto = Produto.query.get(produto_id)
        if produto:
            if produto.quantidade >= quantidade_removida:
                produto.quantidade -= quantidade_removida
                db.session.commit()
                registrar_historico("Saída de Produto", produto.nome, quantidade_removida)  
            else:
                return "<h3>Erro: quantidade solicitada maior que o estoque disponível!</h3>"

        return redirect(url_for('routes.estoque'))

    return render_template('saida.html', produtos=produtos)

@bp.route('/excluir', methods=['GET', 'POST'])
def excluir():
    if not session.get('gerente_logado'):
        return redirect(url_for('routes.gerente'))

    produtos = Produto.query.all()

    if request.method == 'POST':
        produto_id = request.form['produto_id']
        produto = Produto.query.get(produto_id)

        if produto:
            db.session.delete(produto)
            db.session.commit()
            registrar_historico("Exclusão de Produto", produto.nome)    

        return redirect(url_for('routes.estoque'))

    return render_template('excluir.html', produtos=produtos)

from datetime import datetime

def registrar_historico(acao, produto_nome, quantidade=0):
    caminho = 'historico.txt'
    data_hora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    linha = f"[{data_hora}] - {acao}: {produto_nome}"
    if quantidade:
        linha += f" | Quantidade: {quantidade}"
    linha += "\n"

    with open(caminho, 'a', encoding='utf-8') as arquivo:
        arquivo.write(linha)


@bp.route('/historico')
def historico():
    if not session.get('gerente_logado'):
        return redirect(url_for('routes.gerente'))

    try:
        with open('historico.txt', 'r', encoding='utf-8') as arquivo:
            conteudo = arquivo.read()
    except FileNotFoundError:
        conteudo = ""

    return render_template('historico.html', conteudo=conteudo)

 
@bp.route('/estoque')
def estoque():
    gerente_logado = session.get('gerente_logado', False)
    
    produto_id = request.args.get('produto_id')

    if produto_id and produto_id.isdigit():
        produtos = Produto.query.filter_by(id=int(produto_id)).all()
    else:
        produtos = Produto.query.all()

    total_geral = 0
    for p in produtos:
        try:
            total_geral += float(p.preco_unitario or 0) * int(p.quantidade or 0)
        except (ValueError, TypeError):
            continue
    gerente_logado = session.get('gerente_logado', False)    
    return render_template('estoque.html', produtos=produtos, total_geral=total_geral, gerente_logado=gerente_logado)
