from app import db


class Produto(db.Model):
    __tablename__ = 'produtos'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False, default=0)
    observacao = db.Column(db.Text, nullable=True)
    tipo = db.Column(db.String(20), nullable=False, default='madeira')


    def __repr__(self):
        return f'<Produto {self.nome}>'
    
class Lote(db.Model):
    __tablename__ = 'lotes'

    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    
    quantidade_inicial = db.Column(db.Integer, nullable=False)
    quantidade_atual = db.Column(db.Integer, nullable=False)
    
    custo_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    nota_fiscal = db.Column(db.String(50), nullable=True)
    
    data_entrada = db.Column(db.DateTime(timezone=True), nullable=False)
    
    produto = db.relationship('Produto', backref='lotes')
    
class Historico(db.Model):
    __tablename__ = 'historico'
       
    id = db.Column(db.Integer, primary_key=True)
    acao = db.Column(db.String(100), nullable=False)
    produto_nome = db.Column(db.String(100), nullable=False)
    quantidade = db.Column(db.Integer, nullable=True)
    valor = db.Column(db.Numeric(10, 2), nullable=True) 
    data_hora = db.Column(db.DateTime(timezone=True), nullable=False)
    lucro_real = db.Column(db.Numeric(10, 2), nullable=True)
    nota_fiscal = db.Column(db.String(50), nullable=True)
class DespesasMensais(db.Model):
    __tablename__ = 'despesas_mensais'

    id = db.Column(db.Integer, primary_key=True)
    ano = db.Column(db.Integer, nullable=False)
    mes = db.Column(db.Integer, nullable=False)
    valor_despesa = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    data_registro = db.Column(db.DateTime(timezone=True), nullable=False)
