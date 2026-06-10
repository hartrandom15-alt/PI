from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

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

# ==========================
# PEDIDO
# ==========================

class Pedido(database.Model):

    id = database.Column(
        database.Integer,
        primary_key=True
    )

    data = database.Column(
        database.DateTime,
        default=datetime.utcnow
    )

    nome_cliente = database.Column(
        database.String(100),
        nullable=False
    )

    telefone = database.Column(
        database.String(30),
        nullable=False
    )

    bolo = database.Column(
        database.String(100),
        nullable=False
    )

    status = database.Column(
        database.String(30),
        default='Pendente'
    )