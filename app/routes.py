from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import db
from app.models import Lote, Produto, Historico, DespesasMensais
import os
import pytz
from werkzeug.security import check_password_hash 
from functools import wraps
from app.db_utils import transactional
from sqlalchemy import text
from datetime import datetime



bp = Blueprint('routes', __name__)


@bp.route('/healthcheck-db')
def healthcheck_db():
    db.session.execute(text("SELECT 1"))
    return {'status': 'ok'}


def agora_sp():
    return datetime.now(pytz.timezone("America/Sao_Paulo"))



def gerente_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('gerente_logado'):
            return redirect(url_for('routes.gerente'))
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/')
def home():
    return render_template('index.html')


@bp.route('/gerente', methods=['GET', 'POST'])
def gerente():
    senha_correta = os.getenv('GERENTE_SENHA')
 
    if request.method == 'POST':
        senha_digitada = request.form.get('senha')
           
        if senha_correta and check_password_hash(senha_correta, senha_digitada):
            session['gerente_logado'] = True
            session.permanent = True
            return redirect(url_for('routes.painel_gerente'))
        else:
            return render_template('login.html', erro='Senha incorreta. Tente novamente.')

    return render_template('login.html')

    
#painel gerente(protegido)
@bp.route('/painel')
@gerente_required
def painel_gerente():
     
    return render_template('painel.html')

@bp.route('/logout')
def logout():
    session.clear()  #limpa a sessão
    return redirect(url_for('routes.home'))

 
@bp.route('/cadastro', methods=['GET', 'POST'])
@gerente_required
@transactional
def cadastro():
    if not session.get('gerente_logado'):
        return redirect(url_for('routes.gerente'))

    if request.method == 'POST':
        nome = request.form.get('nome') 
        tipo = request.form.get('tipo', 'madeira')        
        observacao = request.form.get('observacao')

        if not nome:
            flash("informe o nome do produto", "erro")
            return redirect(url_for('routes.cadastro'))
        
        novo_produto = Produto(
            nome=nome.strip(), 
            quantidade=0,            
            observacao=observacao.strip() if observacao else None,
            tipo=tipo
        )

        db.session.add(novo_produto)
         
        registrar_historico(
            "Cadastro de Produto",
            nome
        )
 
        return redirect(url_for('routes.estoque'))

    return render_template('cadastro.html')

@bp.route('/produto/<int:produto_id>/editar-nome', methods=['POST'])
@gerente_required
@transactional
def editar_nome_produto(produto_id):
    produto = Produto.query.get_or_404(produto_id)

    novo_nome = request.form.get('nome', '').strip()
    if not novo_nome:
        flash("Nome inválido.", "erro")
        return redirect(url_for('routes.detalhe_produto', produto_id=produto.id))

    nome_antigo = produto.nome
    produto.nome = novo_nome

    registrar_historico(
        acao="Edição de Produto",
        produto_nome=f"{nome_antigo} → {novo_nome}"
    )

    flash("Nome do produto atualizado com sucesso.", "sucesso")
    return redirect(url_for('routes.detalhe_produto', produto_id=produto.id))


@bp.route('/entrada', methods=['GET', 'POST'])
@gerente_required
@transactional
def entrada():
    if not session.get('gerente_logado'):
        return redirect(url_for('routes.gerente'))

    produtos = Produto.query.all()

    if request.method == 'POST':                
        produto_id = request.form.get('produto_id')
        quantidade_str = request.form.get('quantidade')
        valor_str = request.form.get('valor')
        nota_fiscal = request.form.get('nota_fiscal')

        if not produto_id or not quantidade_str or not valor_str:
            flash("Preencha todos os campos obrigatórios.", "erro")
            return redirect(url_for('routes.entrada'))

        try:
            quantidade_adicionada = int(quantidade_str)
            novo_preco = float(valor_str.replace(',', '.'))
        except ValueError:
            flash("Quantidade ou valor inválido.", "erro")
            return redirect(url_for('routes.entrada'))
        
        produto = Produto.query.get(produto_id)
        if produto: 
            #a cada remessa,atualiza preço unitário e quantidade
            produto.preco_unitario = novo_preco
            
            produto.quantidade += quantidade_adicionada
             #Registro do Lote(FIFO)
            lote = Lote(
                produto_id=produto.id,
                quantidade_inicial=quantidade_adicionada,
                quantidade_atual=quantidade_adicionada,
                custo_unitario=novo_preco,
                nota_fiscal=nota_fiscal,
                data_entrada=agora_sp()
            )
            db.session.add(lote)
             
            registrar_historico(
                "Entrada de Produto", 
                produto.nome, 
                quantidade_adicionada,
                valor=None,
                nota_fiscal=nota_fiscal
            )  
 
        return redirect(url_for('routes.estoque'))

    return render_template('entrada.html', produtos=produtos)

def processar_saida_produto(produto, quantidade_removida, valor_total_saida):
    lotes = (
        Lote.query
        .filter_by(produto_id=produto.id)   
        .filter(Lote.quantidade_atual > 0)
        .order_by(Lote.data_entrada.asc())
        .all()
    )
    quantidade_necessaria = quantidade_removida
    custo_total = 0
        
    for lote in lotes:
        if quantidade_necessaria == 0:
            break
        
        consumir = min(lote.quantidade_atual, quantidade_necessaria) 
        #atualiza saldo do lote
        lote.quantidade_atual -= consumir
        #soma custo real da saída
        custo_total += float(lote.custo_unitario)*consumir        
        quantidade_necessaria -= consumir
        
    if quantidade_necessaria > 0:
        raise ValueError("Erro: estoque inconsistente nos lotes FIFO.")
 
    produto.quantidade -= quantidade_removida
    lucro_real = valor_total_saida - custo_total                   
    #atualiza estoque do produto  
    nota_fiscal = lotes[0].nota_fiscal if lotes else None
    #Registra histórico com NF ou lote                
    registrar_historico(
        "Saída de Produto",
        produto.nome, 
        quantidade_removida, 
        valor_total_saida,   #valor total saída
        nota_fiscal=nota_fiscal,
        lucro_real=lucro_real             
    )

@bp.route('/saida', methods=['GET', 'POST'])
@gerente_required
@transactional
def saida():
    if not session.get('gerente_logado'):
        return redirect(url_for('routes.gerente'))

    produtos = Produto.query.all()

    if request.method == 'POST':
        produto_id = request.form.get('produto_id')
        quantidade_str = request.form.get('quantidade')
        valor_str = request.form.get('valor')

        if not produto_id or not quantidade_str or not valor_str:
            flash("Preencha todos os campos.", "erro")
            return redirect(url_for('routes.saida'))

        try:
            quantidade_removida = int(quantidade_str)
            valor_total_saida = float(valor_str.replace(',', '.'))

            
            produto = Produto.query.get(produto_id)                
            if not produto:
                raise ValueError(" Produto não encontrado!")
            #verificar estoque
            if produto.quantidade < quantidade_removida:
                flash("Quantidade solicitada maior que o estoque disponível.", "erro")
                return redirect(url_for('routes.saida'))
            
            processar_saida_produto(
                produto=produto, 
                quantidade_removida=quantidade_removida,                       
                valor_total_saida=valor_total_saida
            )
            return redirect(url_for('routes.estoque'))  
        except ValueError as e: 
            flash(str(e), "erro")
            raise
    return render_template('saida.html', produtos=produtos  )
    
  
@bp.route('/excluir', methods=['GET', 'POST'])
@gerente_required
@transactional
def excluir():
    if not session.get('gerente_logado'):
        return redirect(url_for('routes.gerente'))

    from app.models import Lote
        
    produtos = Produto.query.all()

    if request.method == 'POST':
        produto_id = request.form['produto_id']
        produto = Produto.query.get(produto_id)

        if produto:
            lotes = Lote.query.filter_by(produto_id=produto.id).count()
            if lotes > 0:
                flash("Erro: produto possui lotes registrados e não pode ser excluído.", "erro")
                return redirect(url_for('routes.excluir'))
             
            db.session.delete(produto)            
            registrar_historico("Exclusão de Produto", produto.nome)    
             
        return redirect(url_for('routes.estoque'))

    return render_template('excluir.html', produtos=produtos)

def registrar_historico(
    acao, 
    produto_nome, 
    quantidade=None, 
    valor=None, 
    nota_fiscal=None,
    lucro_real=None
    ):    
               
    historico = Historico(
        acao=acao,
        produto_nome=produto_nome,
        quantidade=quantidade,
        valor=valor,
        nota_fiscal=nota_fiscal,
        lucro_real=lucro_real,
        data_hora=agora_sp()        
    )

    db.session.add(historico)
     
@bp.route('/historico')
def historico():
    if not session.get('gerente_logado'):
        return redirect(url_for('routes.gerente'))

    tipo = request.args.get("tipo", "todos")
    query = Historico.query
    if tipo == 'entrada':
        query = query.filter(Historico.acao == 'Entrada de Produto')
    elif tipo == 'saida':
        query = query.filter(Historico.acao == 'Saída de Produto')
    
    registros = query.order_by(Historico.data_hora.desc()).all() 
    return render_template('historico.html', registros=registros, pytz=pytz)

 
@bp.route('/faturamento', methods=['GET', 'POST'])
@gerente_required
@transactional
def faturamento():    
    from sqlalchemy import text          

    from sqlalchemy import extract, func
 
    ano_atual = agora_sp().year

     # 1. SALVAR IMPOSTO (POST)
    if request.method == 'POST':
        anos_selecionados = request.args.getlist("anos", type=int)
        if len(anos_selecionados) > 1:
            return redirect(url_for('routes.faturamento', anos=anos_selecionados))
        
        ano_str = request.form.get('ano')
        mes_str = request.form.get('mes')
        valor_str = request.form.get('valor_despesa')
        
        if not ano_str or not mes_str or not valor_str:
            flash("Preencha todos os campos da despesa.", "erro")
            return redirect(url_for('routes.faturamento'))
        try:
            ano = int(ano_str)
            mes = int(mes_str)
            valor = float(valor_str.replace(',', '.'))
        except ValueError:
            flash("Dados de despesa inválidos.", "erro")
            return redirect(url_for('routes.faturamento'))

        despesa = DespesasMensais.query.filter_by(ano=ano, mes=mes).first()

        if despesa:
            despesa.valor_despesa = valor
        else:
            despesa = DespesasMensais(
                ano=ano,
                mes=mes,
                valor_despesa=valor,
                data_registro=agora_sp()
            )
            db.session.add(despesa)
                     
        return redirect(url_for('routes.faturamento', ano=ano))

     # 2. ANO SELECIONADO (GET)
    anos_selecionados = request.args.getlist("anos", type=int)
    if not anos_selecionados:   
        anos_selecionados = [ano_atual]

    ano_selecionado = anos_selecionados[0]
    
    # Capturar meses selecionados:
    meses_selecionados = request.args.getlist("meses", type=int)

    # Se nenhum mês for escolhido, usar todos os 12 meses
    if len(meses_selecionados) == 0:
        meses_selecionados = list(range(1, 13))


    # 3. LISTA DE ANOS DISPONÍVEIS
 
    anos_disponiveis = (
        db.session.query(func.date_part('year', Historico.data_hora))
        .filter(Historico.valor.isnot(None))
        .distinct()
        .order_by(func.date_part('year', Historico.data_hora).desc())
        .all()
    )

    anos_disponiveis = [int(a[0]) for a in anos_disponiveis]

    if ano_atual not in anos_disponiveis:
        anos_disponiveis.insert(0, ano_atual)

    # 4. GERAR LISTA DE 12 MESES
    meses_nomes = [
        "Janeiro", "Fevereiro", "Março", "Abril",
        "Maio", "Junho", "Julho", "Agosto",
        "Setembro", "Outubro", "Novembro", "Dezembro"
    ]

    meses_do_ano = []
    for i in meses_selecionados:
        if len(anos_selecionados) > 1:
            chave = f"acumulado-{i:02d}"
        else:
            chave = f"{ano_selecionado}-{i:02d}"
            
        meses_do_ano.append({
            "numero": i,
            "nome": meses_nomes[i - 1],
            "ano": ano_selecionado,
            "chave": chave
        })


    # 5. FATURAMENTO BRUTO
    dados_historico = (
        db.session.query(
            extract('year', Historico.data_hora).label('ano'),
            extract('month', Historico.data_hora).label('mes'),
            func.sum(Historico.valor).label('bruto'),
            func.sum(Historico.lucro_real).label('lucro_real')
        )
        .filter(
            Historico.acao == "Saída de Produto",
            extract('year', Historico.data_hora).in_(anos_selecionados),
            extract('month', Historico.data_hora).in_(meses_selecionados)
        )
        .group_by(
            extract('year', Historico.data_hora),
            extract('month', Historico.data_hora)
        )
        .all()
    )

    resumo = {}
    for row in dados_historico:
        chave = (
            f"acumulado-{int(row.mes):02d}"
            if len(anos_selecionados) > 1
            else f"{int(row.ano)}-{int(row.mes):02d}"
        )
        resumo[chave] = {
            "bruto": float(row.bruto or 0),
            "lucro_real": float(row.lucro_real or 0)
        }
        
    for mes in meses_do_ano:
        dados = resumo.get(mes["chave"], {})
        mes["faturamento_bruto"] = dados.get("bruto", 0.0)
        mes["lucro_real"] = dados.get("lucro_real", 0.0)


        
    # 6. CARREGAR DESPESAS DO ANO
    despesas = DespesasMensais.query.filter(
        DespesasMensais.ano.in_(anos_selecionados),
        DespesasMensais.mes.in_(meses_selecionados) 
    ).all()

    despesas_dict = {}
    for d in despesas:
        if len(anos_selecionados) > 1:
            chave = f"acumulado-{d.mes:02d}"
            despesas_dict[chave] = despesas_dict.get(chave, 0.0) + float(d.valor_despesa)
            
        else:
            chave = f"{d.ano}-{d.mes:02d}"
            despesas_dict[chave] = float(d.valor_despesa)

    #IMPOSTO E LÍQUIDO
    for mes in meses_do_ano:
        imposto = despesas_dict.get(mes["chave"], 0.0)
        mes["imposto"] = float(imposto)        
        mes["liquido"] = mes["lucro_real"] - mes["imposto"]

     #TOTAIS DO ANO
    total_bruto = sum(m["faturamento_bruto"] for m in meses_do_ano)
    total_lucro_real = sum(m["lucro_real"] for m in meses_do_ano)
    total_imposto = sum(m["imposto"] for m in meses_do_ano)
    total_liquido = total_lucro_real - total_imposto  
    
    #RENDERIZAÇÃO
 
    return render_template(
        'faturamento.html',
        anos_selecionados=anos_selecionados,
        anos_disponiveis=anos_disponiveis,
        meses_do_ano=meses_do_ano,
        total_bruto=total_bruto,
        total_lucro_real=total_lucro_real,
        total_imposto=total_imposto,
        total_liquido=total_liquido   
    )
    
@bp.route('/produto/<int:produto_id>')
@gerente_required
def detalhe_produto(produto_id):
    produto = Produto.query.get_or_404(produto_id)

    lotes = (
        Lote.query
        .filter_by(produto_id=produto.id)
        .order_by(Lote.data_entrada.asc())
        .all()
    )

    return render_template(
        'produto_detalhe.html',
        produto=produto,
        lotes=lotes,
        pytz=pytz
    )
@bp.route('/lote/<int:lote_id>/nota-fiscal', methods=['POST'])
@gerente_required
@transactional
def atualizar_nota_fiscal(lote_id):
    lote = Lote.query.get_or_404(lote_id)

    nota_fiscal = request.form.get('nota_fiscal', '').strip()
    
    if nota_fiscal == '':
        lote.nota_fiscal = None
    else:
        lote.nota_fiscal = nota_fiscal[:50] 

    registrar_historico(
        acao="Atualização de Nota Fiscal",
        produto_nome=lote.produto.nome,
        nota_fiscal=lote.nota_fiscal
    )
    flash("Nota fiscal atualizada com sucesso.", "sucesso")
    return redirect(url_for('routes.detalhe_produto', produto_id=lote.produto_id))

@bp.route('/lote/<int:lote_id>/quantidade', methods=['POST'])
@gerente_required
@transactional
def atualizar_quantidade_lote(lote_id):
    lote = Lote.query.get_or_404(lote_id)

    if lote.quantidade_atual == 0:
        flash("Lote já consumido. Não é possível editar.", "erro")
        return redirect(url_for('routes.detalhe_produto', produto_id=lote.produto_id))

    try:
        nova_qtd = int(request.form.get('quantidade_atual'))
    except (TypeError, ValueError):
        flash("Quantidade inválida.", "erro")
        return redirect(url_for('routes.detalhe_produto', produto_id=lote.produto_id))

    if nova_qtd < 0 or nova_qtd > lote.quantidade_inicial:
        flash("Quantidade fora do limite do lote.", "erro")
        return redirect(url_for('routes.detalhe_produto', produto_id=lote.produto_id))

    delta = nova_qtd - lote.quantidade_atual

    lote.quantidade_atual = nova_qtd
    lote.produto.quantidade += delta

    registrar_historico(
        acao="Ajuste Manual de Lote",
        produto_nome=lote.produto.nome,
        quantidade=delta,
        nota_fiscal="Lote {}:\n{} → {}".format(
            lote.id,
            lote.quantidade_atual - delta,
            lote.quantidade_atual
        )
    )


    flash("Quantidade do lote atualizada com sucesso.", "sucesso")
    return redirect(url_for('routes.detalhe_produto', produto_id=lote.produto_id))

@bp.route('/lote/<int:lote_id>/custo', methods=['POST'])
@gerente_required
@transactional
def atualizar_custo_lote(lote_id):
    lote = Lote.query.get_or_404(lote_id)

    try:
        novo_custo = float(request.form.get('custo_unitario', '').replace(',', '.'))
    except (ValueError, AttributeError):
        flash("Custo inválido.", "erro")
        return redirect(url_for('routes.detalhe_produto', produto_id=lote.produto_id))

    custo_antigo = float(lote.custo_unitario)
    lote.custo_unitario = novo_custo

    registrar_historico(
        acao="Ajuste de Custo de Lote",
        produto_nome=lote.produto.nome,
        valor=custo_antigo - novo_custo,
        nota_fiscal="Lote {}:\n{} → {}".format(
            lote.id,
            custo_antigo,
            novo_custo
        )
    )

    flash("Custo do lote atualizado com sucesso.", "sucesso")
    return redirect(url_for('routes.detalhe_produto', produto_id=lote.produto_id))

@bp.route('/estoque')
def estoque():
        
    from app.models import Lote
    gerente_logado = session.get('gerente_logado', False)
    
    produto_id = request.args.get('produto_id')

    if produto_id and produto_id.isdigit():
        produtos = Produto.query.filter_by(id=int(produto_id)).all()
    else:
        produtos = Produto.query.all()
        
    produtos_madeira = [p for p in produtos if p.tipo == 'madeira']
    produtos_wpc = [p for p in produtos if p.tipo == 'wpc']

    total_quantidade_wpc = sum(int(p.quantidade or 0) for p in produtos_wpc)
    
    #carrega todos lotes de uma vez
    lotes = Lote.query.all()
    #agrupa lotes por produto
    lotes_por_produto = {}
    for lote in lotes:
        lotes_por_produto.setdefault(lote.produto_id, []).append(lote)
        
    total_geral = 0
    total_lotes = 0
    
    for p in produtos_madeira:
        for lote in lotes_por_produto.get(p.id, []):
            try:
                total_geral += float(lote.custo_unitario or 0) * int(lote.quantidade_atual)
                total_lotes += int(lote.quantidade_atual or 0)                
            except (ValueError, TypeError):
                continue
            
    total_quantidade = sum(int(p.quantidade or 0) for p in produtos_madeira)
    
    if total_lotes != total_quantidade:
        return "<h3>Erro: divergência entre estoque consolidado e lotes (FIFO).<h3>"
    valor_formatado = "{:,.2f}".format(total_geral).replace(",", "X").replace(".", ",").replace("X", ".")
    
    return render_template(
        'estoque.html',
        produtos=produtos, 
        produtos_madeira=produtos_madeira, 
        produtos_wpc=produtos_wpc, 
        total_geral=total_geral, 
        total_quantidade=total_quantidade,
        total_quantidade_wpc=total_quantidade_wpc,
        valor_formatado=valor_formatado,
        gerente_logado=gerente_logado
    )

     