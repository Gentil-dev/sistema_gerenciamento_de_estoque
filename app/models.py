from app import db


class Produto(db.Model):
    __tablename__ = 'produtos'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False, default=0)
    preco_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    observacao = db.Column(db.Text, nullable=True)


    def __repr__(self):
        return f'<Produto {self.nome}>'