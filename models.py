from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

database = SQLAlchemy()


# ==========================
# USUÁRIO
# ==========================

class Usuario(database.Model):

    id = database.Column(
        database.Integer,
        primary_key=True
    )

    nome = database.Column(
        database.String(100),
        nullable=False
    )

    email = database.Column(
        database.String(120),
        nullable=False,
        unique=True
    )

    # NOVO: Coluna para guardar a senha criptografada
    senha_hash = database.Column(
        database.String(255),
        nullable=False
    )

    # NOVO: Transforma a senha digitada em um código seguro
    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    # NOVO: Verifica se a senha digitada no login bate com a do banco
    def checar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)


# ==========================
# BOLO
# ==========================

class Bolo(database.Model):

    id = database.Column(
        database.Integer,
        primary_key=True
    )

    nome = database.Column(
        database.String(100),
        nullable=False
    )

    preco = database.Column(
        database.Float,
        nullable=False
    )

    descricao = database.Column(
        database.Text,
        nullable=False
    )

    imagem = database.Column(
        database.String(500)
    )

    # NOVO: Selo que aparece no canto da imagem (ex: "Especial", "Novidade")
    tag = database.Column(
        database.String(50),
        nullable=True,
        default='Especial'
    )

    # NOVO: Lista de características, separadas por vírgula (ex: "Artesanal, Premium")
    ingredientes = database.Column(
        database.String(300),
        nullable=True,
        default='Artesanal, Premium'
    )

# ==========================
# CHEFE
# ==========================

class Chefe(database.Model):

    id = database.Column(
        database.Integer,
        primary_key=True
    )

    nome = database.Column(
        database.String(100),
        nullable=False
    )

    cargo = database.Column(
        database.String(100),
        nullable=False
    )

    imagem = database.Column(
        database.String(500)
    )

# ==========================
# PEDIDO (a encomenda inteira)
# ==========================

class Pedido(database.Model):

    id = database.Column(
        database.Integer,
        primary_key=True
    )

    # Código público e aleatório usado na URL de acompanhamento.
    # Não usamos o "id" na URL para ninguém conseguir ver o pedido de
    # outra pessoa só trocando o número.
    codigo_acompanhamento = database.Column(
        database.String(36),
        nullable=False,
        unique=True
    )

    data = database.Column(
        database.DateTime,
        default=datetime.utcnow
    )

    nome_cliente = database.Column(
        database.String(100),
        nullable=False
    )

    # NOVO: Se o cliente estava logado ao fazer o pedido, guarda o vínculo com a conta
    usuario_id = database.Column(
        database.Integer,
        database.ForeignKey('usuario.id'),
        nullable=True
    )

    telefone = database.Column(
        database.String(30),
        nullable=False
    )

    endereco = database.Column(
        database.String(300),
        nullable=False
    )

    complemento = database.Column(
        database.String(150),
        nullable=True
    )

    forma_pagamento = database.Column(
        database.String(50),
        nullable=True
    )

    # Etapas possíveis: "Pedido Recebido", "Em Produção",
    # "Pronto / Finalizando", "Saiu para Entrega", "Entregue"
    status = database.Column(
        database.String(30),
        default='Pedido Recebido'
    )

    # NOVO: Indica se o cliente cancelou o pedido
    cancelado = database.Column(
        database.Boolean,
        default=False,
        nullable=False
    )

    # Um pedido tem vários itens (bolos + quantidades)
    itens = database.relationship(
        'ItemPedido',
        backref='pedido',
        cascade='all, delete-orphan'
    )


# ==========================
# ITEM DO PEDIDO (cada bolo dentro da encomenda)
# ==========================

class ItemPedido(database.Model):

    id = database.Column(
        database.Integer,
        primary_key=True
    )

    pedido_id = database.Column(
        database.Integer,
        database.ForeignKey('pedido.id'),
        nullable=False
    )

    nome_bolo = database.Column(
        database.String(100),
        nullable=False
    )

    # NOVO: Vínculo com o bolo real, usado para verificar se o cliente
    # realmente comprou esse bolo na hora de liberar a avaliação.
    bolo_id = database.Column(
        database.Integer,
        database.ForeignKey('bolo.id'),
        nullable=True
    )

    quantidade = database.Column(
        database.Integer,
        nullable=False,
        default=1
    )


# ==========================
# AVALIAÇÃO (nota + comentário de um bolo)
# ==========================

class Avaliacao(database.Model):

    id = database.Column(
        database.Integer,
        primary_key=True
    )

    bolo_id = database.Column(
        database.Integer,
        database.ForeignKey('bolo.id'),
        nullable=False
    )

    usuario_id = database.Column(
        database.Integer,
        database.ForeignKey('usuario.id'),
        nullable=False
    )

    nota = database.Column(
        database.Integer,
        nullable=False
    )

    comentario = database.Column(
        database.Text,
        nullable=True
    )

    data = database.Column(
        database.DateTime,
        default=datetime.utcnow
    )

    bolo = database.relationship('Bolo', backref='avaliacoes')
    usuario = database.relationship('Usuario')