import csv
import io
import os
import uuid
from datetime import datetime

from flask import (
    Flask,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    session,
)
from models import Avaliacao, Bolo, Chefe, ItemPedido, Pedido, Usuario, database
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.secret_key = 'luar_rubro_admin'  # Dica: Em produção, use variável de ambiente (os.getenv)

# ==========================
# CONFIG BANCO
# ==========================

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

database.init_app(app)

# ==========================
# CONSTANTES DE PEDIDO
# ==========================

ETAPAS_PEDIDO = [
    "Pedido Recebido",
    "Em Produção",
    "Pronto / Finalizando",
    "Saiu para Entrega",
    "Entregue",
]

ETAPAS_QUE_PERMITEM_CANCELAMENTO = ["Pedido Recebido", "Em Produção", "Pronto / Finalizando"]


# ==========================
# AUXILIARES (HELPERS)
# ==========================


def salvar_imagem_upload(imagem_file):
    """Salva a imagem enviada no diretório /static/imagens/ com UUID único."""
    nome_seguro = secure_filename(imagem_file.filename)
    extensao = os.path.splitext(nome_seguro)[1]
    nome_arquivo = f"{uuid.uuid4()}{extensao}"

    caminho = os.path.join(app.root_path, "static", "imagens", nome_arquivo)
    imagem_file.save(caminho)
    return nome_arquivo


def remover_imagem_antiga(nome_arquivo):
    """Remove a imagem do disco caso ela exista."""
    if nome_arquivo:
        caminho = os.path.join(app.root_path, "static", "imagens", nome_arquivo)
        if os.path.exists(caminho):
            try:
                os.remove(caminho)
            except OSError:
                pass


# ==========================
# HOME
# ==========================


@app.route("/")
def homepage():
    bolos = Bolo.query.order_by(Bolo.id.desc()).all()

    bolos_json = []
    for b in bolos:
        avaliacoes = Avaliacao.query.filter_by(bolo_id=b.id).all()
        total_avaliacoes = len(avaliacoes)
        media_avaliacao = round(sum(a.nota for a in avaliacoes) / total_avaliacoes, 1) if total_avaliacoes else 0

        bolos_json.append({
            "id": b.id,
            "nome": b.nome,
            "preco": b.preco,
            "descricao": b.descricao,
            "img": f"/static/imagens/{b.imagem}",
            "tag": b.tag or "Especial",
            "ingredientes": [i.strip() for i in (b.ingredientes or "Artesanal, Premium").split(",") if i.strip()],
            "media_avaliacao": media_avaliacao,
            "total_avaliacoes": total_avaliacoes,
        })

    usuario_logado = session.get("usuario_nome")

    return render_template("index.html", bolos_json=bolos_json, usuario_logado=usuario_logado)


# ==========================
# CHEFES
# ==========================


@app.route("/chefes")
def chefes():
    lista_chefes = Chefe.query.all()
    return render_template("chefes.html", chefes=lista_chefes)


# ==========================
# CADASTRO DO CLIENTE
# ==========================


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    mensagem = None

    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")

        existe = Usuario.query.filter_by(email=email).first()

        if existe:
            mensagem = "E-mail já cadastrado!"
        else:
            novo = Usuario(nome=nome, email=email)
            novo.set_senha(senha)

            database.session.add(novo)
            database.session.commit()

            session["usuario_id"] = novo.id
            session["usuario_nome"] = novo.nome
            return redirect("/")

    return render_template("cadastro.html", mensagem=mensagem)


# ==========================
# LOGIN DO CLIENTE
# ==========================


@app.route("/login", methods=["GET", "POST"])
def login():
    mensagem = None

    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and usuario.checar_senha(senha):
            session["usuario_id"] = usuario.id
            session["usuario_nome"] = usuario.nome
            return redirect("/")
        else:
            mensagem = "E-mail ou senha incorretos."

    return render_template("login.html", mensagem=mensagem)


# ==========================
# LOGOUT DO CLIENTE E ADMIN (DESLOGA E RECARREGA HOMEPAGE)
# ==========================


@app.route("/logout")
@app.route("/logout-usuario")
def logout():
    session.clear()
    return redirect("/")


# ==========================
# PERFIL E RECUPERAÇÃO DE SENHA
# ==========================


@app.route("/perfil", methods=["GET", "POST"])
def perfil():
    # Se não houver ID de usuário na sessão, vai para o login
    if not session.get("usuario_id"):
        return redirect("/login")

    # Busca o usuário no banco de dados
    usuario = Usuario.query.get(session["usuario_id"])

    # Se o usuário não existir mais no banco de dados (ex: conta apagada)
    if not usuario:
        session.clear()
        return redirect("/login")

    mensagem = None

    if request.method == "POST":
        novo_nome = request.form.get("nome")
        novo_email = request.form.get("email")
        nova_senha = request.form.get("senha")

        alterou_algo = False

        # Atualiza o NOME se preenchido e diferente do atual
        if novo_nome and novo_nome.strip() and novo_nome.strip() != usuario.nome:
            usuario.nome = novo_nome.strip()
            session["usuario_nome"] = usuario.nome
            alterou_algo = True

        # Atualiza o E-MAIL se preenchido e diferente do atual
        if novo_email and novo_email.strip() and novo_email.strip() != usuario.email:
            if Usuario.query.filter_by(email=novo_email.strip()).first():
                mensagem = "Este e-mail já está em uso por outra conta."
                return render_template("perfil.html", usuario=usuario, mensagem=mensagem)
            else:
                usuario.email = novo_email.strip()
                alterou_algo = True

        # Atualiza a SENHA se o usuário digitou algo
        if nova_senha and nova_senha.strip():
            usuario.set_senha(nova_senha)
            alterou_algo = True

        if alterou_algo:
            database.session.commit()
            mensagem = "Dados atualizados com sucesso!"
        elif not mensagem:
            mensagem = "Nenhuma alteração foi feita."

    return render_template("perfil.html", usuario=usuario, mensagem=mensagem)


@app.route("/deletar-conta", methods=["POST"])
def deletar_conta():
    usuario_id = session.get("usuario_id")

    if not usuario_id:
        return redirect("/login")

    usuario = Usuario.query.get(usuario_id)

    if usuario:
        database.session.delete(usuario)
        database.session.commit()

    # Limpa a sessão (desloga) e volta para a homepage
    session.clear()
    return redirect("/")


@app.route("/esqueci-senha", methods=["GET", "POST"])
def esqueci_senha():
    mensagem = None
    if request.method == "POST":
        email = request.form.get("email")
        nova_senha = request.form.get("senha")

        usuario = Usuario.query.filter_by(email=email).first()
        if usuario:
            usuario.set_senha(nova_senha)
            database.session.commit()
            return redirect("/login")
        else:
            mensagem = "E-mail não encontrado."

    return render_template("esqueci_senha.html", mensagem=mensagem)


# ==========================
# LISTA DE USUÁRIOS
# ==========================


@app.route("/usuarios")
def usuarios():
    if not session.get("admin"):
        return redirect("/login-admin")

    lista = Usuario.query.all()
    return render_template("usuarios.html", usuarios=lista)


# ==========================
# AVALIAÇÕES (REGRAS DE CONTA)
# ==========================


@app.route("/api/avaliacoes/<int:bolo_id>")
def api_avaliacoes(bolo_id):
    """Lê todas as avaliações registradas de um bolo no banco de dados."""
    avaliacoes = (
        Avaliacao.query
        .filter_by(bolo_id=bolo_id)
        .order_by(Avaliacao.data.desc())
        .all()
    )

    total = len(avaliacoes)
    media = round(sum(a.nota for a in avaliacoes) / total, 1) if total else 0

    return jsonify({
        "media": media,
        "total": total,
        "avaliacoes": [
            {
                "usuario_nome": a.usuario.nome if a.usuario else "Cliente",
                "nota": a.nota,
                "comentario": a.comentario,
                "data": a.data.strftime("%d/%m/%Y") if a.data else "",
            }
            for a in avaliacoes
        ],
    })


@app.route("/api/pode-avaliar/<int:bolo_id>")
def api_pode_avaliar(bolo_id):
    """
    Verifica se O USUÁRIO LOGADO pode avaliar este bolo especificamente.
    Retorna True apenas se o usuário tiver um pedido ENTREGUE e NÃO CANCELADO contendo este bolo.
    """
    usuario_id = session.get("usuario_id")

    if not usuario_id:
        return jsonify({"pode_avaliar": False, "motivo": "login"})

    comprou = (
        database.session.query(ItemPedido)
        .join(Pedido, ItemPedido.pedido_id == Pedido.id)
        .filter(
            Pedido.usuario_id == usuario_id,
            Pedido.status == "Entregue",
            Pedido.cancelado == False,
            ItemPedido.bolo_id == bolo_id,
        )
        .first()
    )

    if not comprou:
        return jsonify({"pode_avaliar": False, "motivo": "nao_comprou"})

    # Busca APENAS a avaliação existente deste usuário
    avaliacao_existente = Avaliacao.query.filter_by(
        bolo_id=bolo_id, usuario_id=usuario_id
    ).first()

    return jsonify({
        "pode_avaliar": True,
        "avaliacao_existente": {
            "nota": avaliacao_existente.nota,
            "comentario": avaliacao_existente.comentario,
        } if avaliacao_existente else None,
    })


@app.route("/api/avaliar/<int:bolo_id>", methods=["POST"])
def api_avaliar(bolo_id):
    """
    Registra ou atualiza A AVALIAÇÃO DO USUÁRIO LOGADO para este bolo.
    Nenhum usuário consegue alterar avaliações alheias.
    """
    usuario_id = session.get("usuario_id")

    if not usuario_id:
        return jsonify({"sucesso": False, "erro": "Você precisa estar logado para avaliar."}), 401

    comprou = (
        database.session.query(ItemPedido)
        .join(Pedido, ItemPedido.pedido_id == Pedido.id)
        .filter(
            Pedido.usuario_id == usuario_id,
            Pedido.status == "Entregue",
            Pedido.cancelado == False,
            ItemPedido.bolo_id == bolo_id,
        )
        .first()
    )

    if not comprou:
        return jsonify({"sucesso": False, "erro": "Você só pode avaliar bolos que já recebeu."}), 403

    dados = request.json or {}
    nota = dados.get("nota")

    try:
        nota = int(nota)
    except (TypeError, ValueError):
        nota = 0

    if nota < 1 or nota > 5:
        return jsonify({"sucesso": False, "erro": "A nota deve ser de 1 a 5."}), 400

    comentario = (dados.get("comentario") or "").strip()[:1000]

    # Busca a avaliação feita estritamente por ESTE usuário
    avaliacao = Avaliacao.query.filter_by(bolo_id=bolo_id, usuario_id=usuario_id).first()

    if avaliacao:
        # Atualiza a avaliação própria do usuário logado
        avaliacao.nota = nota
        avaliacao.comentario = comentario
        avaliacao.data = datetime.utcnow()
    else:
        # Cria uma nova avaliação vinculada exclusivamente à conta deste usuário
        avaliacao = Avaliacao(
            bolo_id=bolo_id,
            usuario_id=usuario_id,
            nota=nota,
            comentario=comentario,
        )
        database.session.add(avaliacao)

    database.session.commit()

    return jsonify({"sucesso": True})


# ==========================
# LOGIN ADMIN
# ==========================


@app.route("/login-admin", methods=["GET", "POST"])
def login_admin():
    mensagem = None

    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")

        if usuario == "admin" and senha == "123456":
            session["admin"] = True
            return redirect("/admin/bolos")
        else:
            mensagem = "Usuário ou senha inválidos"

    return render_template("login_admin.html", mensagem=mensagem)


# ==========================
# ADMIN - BOLOS
# ==========================


@app.route("/admin/bolos", methods=["GET", "POST"])
def admin_bolos():
    if not session.get("admin"):
        return redirect("/login-admin")

    mensagem = None

    if request.method == "POST":
        nome = request.form.get("nome")
        preco = float(request.form.get("preco", 0))
        descricao = request.form.get("descricao")
        tag = request.form.get("tag") or "Especial"
        ingredientes = request.form.get("ingredientes") or "Artesanal, Premium"
        imagem = request.files.get("imagem")

        nome_arquivo = None
        if imagem and imagem.filename != "":
            nome_arquivo = salvar_imagem_upload(imagem)

        novo_bolo = Bolo(
            nome=nome, preco=preco, descricao=descricao, imagem=nome_arquivo,
            tag=tag, ingredientes=ingredientes
        )

        database.session.add(novo_bolo)
        database.session.commit()
        mensagem = "Bolo cadastrado com sucesso"

    lista_bolos = Bolo.query.all()
    total_bolos = len(lista_bolos)

    return render_template(
        "admin_bolos.html",
        mensagem=mensagem,
        bolos=lista_bolos,
        total_bolos=total_bolos,
    )


# ==========================
# EDITAR BOLO
# ==========================


@app.route("/editar-bolo/<int:id>", methods=["GET", "POST"])
def editar_bolo(id):
    if not session.get("admin"):
        return redirect("/login-admin")

    bolo = Bolo.query.get_or_404(id)

    if request.method == "POST":
        bolo.nome = request.form.get("nome")
        bolo.preco = float(request.form.get("preco", 0))
        bolo.descricao = request.form.get("descricao")
        bolo.tag = request.form.get("tag") or "Especial"
        bolo.ingredientes = request.form.get("ingredientes") or "Artesanal, Premium"

        imagem = request.files.get("imagem")

        if imagem and imagem.filename != "":
            remover_imagem_antiga(bolo.imagem)
            bolo.imagem = salvar_imagem_upload(imagem)

        database.session.commit()
        return redirect("/admin/bolos")

    return render_template("editar_bolo.html", bolo=bolo)


# ==========================
# EXCLUIR BOLO
# ==========================


@app.route("/deletar-bolo/<int:id>")
def deletar_bolo(id):
    if not session.get("admin"):
        return redirect("/login-admin")

    bolo = Bolo.query.get_or_404(id)

    remover_imagem_antiga(bolo.imagem)

    database.session.delete(bolo)
    database.session.commit()

    return redirect("/admin/bolos")


# ==========================
# ADMIN - CHEFES
# ==========================


@app.route("/admin/chefes", methods=["GET", "POST"])
def admin_chefes():
    if not session.get("admin"):
        return redirect("/login-admin")

    mensagem = None

    if request.method == "POST":
        nome = request.form.get("nome")
        cargo = request.form.get("cargo")
        imagem = request.files.get("imagem")

        nome_arquivo = None
        if imagem and imagem.filename != "":
            nome_arquivo = salvar_imagem_upload(imagem)

        novo_chefe = Chefe(nome=nome, cargo=cargo, imagem=nome_arquivo)

        database.session.add(novo_chefe)
        database.session.commit()
        mensagem = "Chefe cadastrado com sucesso"

    lista_chefes = Chefe.query.all()
    total_chefes = len(lista_chefes)

    return render_template(
        "admin_chefes.html",
        mensagem=mensagem,
        chefes=lista_chefes,
        total_chefes=total_chefes,
    )


# ==========================
# EDITAR CHEFE
# ==========================


@app.route("/editar-chefe/<int:id>", methods=["GET", "POST"])
def editar_chefe(id):
    if not session.get("admin"):
        return redirect("/login-admin")

    chefe = Chefe.query.get_or_404(id)

    if request.method == "POST":
        chefe.nome = request.form.get("nome")
        chefe.cargo = request.form.get("cargo")

        imagem = request.files.get("imagem")

        if imagem and imagem.filename != "":
            remover_imagem_antiga(chefe.imagem)
            chefe.imagem = salvar_imagem_upload(imagem)

        database.session.commit()
        return redirect("/admin/chefes")

    return render_template("editar_chefe.html", chefe=chefe)


# ==========================
# EXCLUIR CHEFE
# ==========================


@app.route("/deletar-chefe/<int:id>")
def deletar_chefe(id):
    if not session.get("admin"):
        return redirect("/login-admin")

    chefe = Chefe.query.get_or_404(id)

    remover_imagem_antiga(chefe.imagem)

    database.session.delete(chefe)
    database.session.commit()

    return redirect("/admin/chefes")


# ==========================
# SALVAR PEDIDO
# ==========================


@app.route("/salvar-pedido", methods=["POST"])
def salvar_pedido():
    dados = request.json or {}

    itens_recebidos = dados.get("itens") or []

    if not itens_recebidos:
        return jsonify({"sucesso": False, "erro": "Carrinho vazio."}), 400

    if not dados.get("cliente") or not dados.get("telefone") or not dados.get("endereco"):
        return jsonify({"sucesso": False, "erro": "Preencha todos os campos obrigatórios."}), 400

    codigo = uuid.uuid4().hex

    pedido = Pedido(
        codigo_acompanhamento=codigo,
        nome_cliente=dados.get("cliente"),
        usuario_id=session.get("usuario_id"),
        telefone=dados.get("telefone"),
        endereco=dados.get("endereco"),
        complemento=dados.get("complemento"),
        forma_pagamento=dados.get("forma_pagamento"),
        status=ETAPAS_PEDIDO[0],
    )

    database.session.add(pedido)
    database.session.flush()

    for item in itens_recebidos:
        novo_item = ItemPedido(
            pedido_id=pedido.id,
            nome_bolo=item.get("nome", "Bolo"),
            bolo_id=item.get("bolo_id"),
            quantidade=int(item.get("quantidade", 1)),
        )
        database.session.add(novo_item)

    database.session.commit()

    return jsonify({"sucesso": True, "codigo": codigo})


# ==========================
# ACOMPANHAMENTO DO PEDIDO (CLIENTE)
# ==========================


@app.route("/acompanhar/<codigo>")
def acompanhar_pedido(codigo):
    pedido = Pedido.query.filter_by(codigo_acompanhamento=codigo).first_or_404()

    etapa_atual = ETAPAS_PEDIDO.index(pedido.status) if pedido.status in ETAPAS_PEDIDO else 0
    pode_cancelar = (not pedido.cancelado) and (pedido.status in ETAPAS_QUE_PERMITEM_CANCELAMENTO)

    return render_template(
        "acompanhar.html",
        pedido=pedido,
        etapas=ETAPAS_PEDIDO,
        etapa_atual=etapa_atual,
        pode_cancelar=pode_cancelar,
    )


@app.route("/api/status-pedido/<codigo>")
def api_status_pedido(codigo):
    pedido = Pedido.query.filter_by(codigo_acompanhamento=codigo).first_or_404()

    etapa_atual = ETAPAS_PEDIDO.index(pedido.status) if pedido.status in ETAPAS_PEDIDO else 0

    return jsonify({
        "status": pedido.status,
        "etapa_atual": etapa_atual,
        "total_etapas": len(ETAPAS_PEDIDO),
        "cancelado": pedido.cancelado,
    })


@app.route("/cancelar-pedido/<codigo>", methods=["POST"])
def cancelar_pedido(codigo):
    pedido = Pedido.query.filter_by(codigo_acompanhamento=codigo).first_or_404()

    if pedido.cancelado:
        return jsonify({"sucesso": False, "erro": "Este pedido já foi cancelado."}), 400

    if pedido.status not in ETAPAS_QUE_PERMITEM_CANCELAMENTO:
        return jsonify({
            "sucesso": False,
            "erro": "Não é mais possível cancelar: o pedido já saiu para entrega ou foi concluído."
        }), 400

    pedido.cancelado = True
    database.session.commit()

    return jsonify({"sucesso": True})


# ==========================
# CONFIRMAR RECEBIMENTO (CLIENTE)
# ==========================


@app.route("/api/concluir-pedido/<codigo>", methods=["POST"])
def concluir_pedido(codigo):
    """
    O cliente confirma que recebeu o pedido.
    Isso remove o pedido da visualização de pedidos ativos do cliente,
    mas mantém o histórico no banco para permitir a avaliação dos bolos.
    """
    pedido = Pedido.query.filter_by(codigo_acompanhamento=codigo).first_or_404()

    # Valida se o admin já havia marcado como entregue
    if pedido.status != "Entregue":
        return jsonify(
            {"sucesso": False, "erro": "O pedido ainda não foi marcado como entregue pelo estabelecimento."}
        ), 400

    # Registra o código na lista de pedidos concluídos na sessão
    concluidos = session.get("pedidos_concluidos", [])
    if codigo not in concluidos:
        concluidos.append(codigo)
        session["pedidos_concluidos"] = concluidos

    return jsonify({"sucesso": True})


# ==========================
# MEUS PEDIDOS (CLIENTE)
# ==========================


@app.route("/meus-pedidos")
def meus_pedidos():
    pedidos_conta = []

    usuario_id = session.get("usuario_id")
    if usuario_id:
        pedidos_conta = (
            Pedido.query
            .filter_by(usuario_id=usuario_id, cancelado=False)
            .order_by(Pedido.id.desc())
            .all()
        )

    return render_template(
        "meus_pedidos.html",
        pedidos_conta=pedidos_conta,
        usuario_logado=session.get("usuario_nome"),
    )


@app.route("/api/meus-pedidos", methods=["POST"])
def api_meus_pedidos():
    dados = request.json or {}
    codigos = dados.get("codigos") or []

    codigos = codigos[:50]

    if not codigos:
        return jsonify({"pedidos": []})

    # Pega a lista de pedidos que o usuário já clicou em 'Confirmar Recebimento'
    concluidos = session.get("pedidos_concluidos", [])

    # Filtra apenas os pedidos não cancelados e não finalizados/concluídos pelo cliente
    pedidos = Pedido.query.filter(
        Pedido.codigo_acompanhamento.in_(codigos),
        Pedido.cancelado == False
    ).all()

    resultado = []
    for p in pedidos:
        # Se o cliente já finalizou a tela do pedido, não exibe mais na lista ativa
        if p.codigo_acompanhamento in concluidos:
            continue

        etapa_atual = ETAPAS_PEDIDO.index(p.status) if p.status in ETAPAS_PEDIDO else 0
        resultado.append({
            "codigo": p.codigo_acompanhamento,
            "cliente": p.nome_cliente,
            "status": p.status,
            "etapa_atual": etapa_atual,
            "total_etapas": len(ETAPAS_PEDIDO),
            "data": p.data.strftime("%d/%m/%Y %H:%M") if p.data else "",
            "itens": [{"nome": i.nome_bolo, "quantidade": i.quantidade, "bolo_id": i.bolo_id} for i in p.itens],
        })

    return jsonify({"pedidos": resultado})


# ==========================
# ADMIN - PEDIDOS
# ==========================


@app.route("/admin/pedidos")
def admin_pedidos():
    if not session.get("admin"):
        return redirect("/login-admin")

    busca = request.args.get("busca")
    status = request.args.get("status")

    query = Pedido.query

    if busca:
        query = query.filter(Pedido.nome_cliente.contains(busca))

    if status:
        query = query.filter_by(status=status)

    pedidos = query.order_by(Pedido.id.desc()).all()

    total_pedidos = len(pedidos)
    entregues = sum(1 for p in pedidos if p.status == "Entregue")
    em_andamento = total_pedidos - entregues

    return render_template(
        "admin_pedidos.html",
        pedidos=pedidos,
        total_pedidos=total_pedidos,
        entregues=entregues,
        em_andamento=em_andamento,
        etapas=ETAPAS_PEDIDO,
    )


# ==========================
# EXPORTAR PEDIDOS CSV
# ==========================


@app.route("/exportar-pedidos")
def exportar_pedidos():
    if not session.get("admin"):
        return redirect("/login-admin")

    pedidos = Pedido.query.all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["ID", "Código", "Cliente", "Telefone", "Endereço", "Complemento", "Itens", "Data", "Status", "Forma de Pagamento"])

    for p in pedidos:
        data_formatada = p.data.strftime("%d/%m/%Y %H:%M") if p.data else ""
        itens_texto = "; ".join(f"{i.nome_bolo} (x{i.quantidade})" for i in p.itens)
        writer.writerow(
            [p.id, p.codigo_acompanhamento, p.nome_cliente, p.telefone, p.endereco, p.complemento or "", itens_texto, data_formatada, p.status, p.forma_pagamento or ""]
        )

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=pedidos.csv"
    response.headers["Content-Type"] = "text/csv; charset=utf-8"

    return response


# ==========================
# STATUS & DELETAR PEDIDO
# ==========================


@app.route("/alterar-status/<int:id>", methods=["POST"])
def alterar_status(id):
    if not session.get("admin"):
        return redirect("/login-admin")

    pedido = Pedido.query.get_or_404(id)

    novo_status = request.form.get("novo_status")

    if novo_status in ETAPAS_PEDIDO:
        pedido.status = novo_status
        database.session.commit()

    return redirect("/admin/pedidos")


@app.route("/deletar-pedido/<int:id>", methods=["POST"])
def deletar_pedido(id):
    if not session.get("admin"):
        return redirect("/login-admin")

    pedido = Pedido.query.get_or_404(id)
    database.session.delete(pedido)
    database.session.commit()

    return redirect("/admin/pedidos")


# ==========================
# PEDIDO
# ==========================


@app.route("/pedido", methods=["GET", "POST"])
def pedido():
    mensagem = None

    if request.method == "POST":
        nome = request.form.get("nome")
        mensagem = f"Pedido enviado com sucesso, {nome}!"

    return render_template("pedido.html", mensagem=mensagem)


# ==========================
# ERRO 404
# ==========================


@app.errorhandler(404)
def pagina_nao_encontrada(e):
    return render_template("404.html"), 404


# ==========================
# INICIALIZAÇÃO DO SERVIDOR (DEVE FICAR SEMPRE NO FINAL)
# ==========================

with app.app_context():
    database.create_all()

if __name__ == "__main__":
    app.run(debug=True)