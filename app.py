import json
import csv

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    jsonify,
    make_response
)

from models import (
    database,
    Usuario,
    Bolo,
    Pedido
)
app = Flask(__name__)

app.secret_key = 'luar_rubro_admin'

# ==========================
# CONFIG BANCO
# ==========================

app.config[
    'SQLALCHEMY_DATABASE_URI'
] = 'sqlite:///site.db'

app.config[
    'SQLALCHEMY_TRACK_MODIFICATIONS'
] = False


database.init_app(
    app
)


# ==========================
# DADOS DOS CHEFES
# ==========================

chefes_lista = [

    {
        "nome": "Arthur Rubro",
        "cargo": "Chocolatier",
        "imagem": "confeiteiro1.jpg"
    },

    {
        "nome": "Helena Luar",
        "cargo": "Confeiteira Senior",
        "imagem": "confeiteiro2.jpg"
    },

    {
        "nome": "Claudio Noite",
        "cargo": "Master Chef",
        "imagem": "confeiteiro.jpg"
    }

]


# ==========================
# HOME
# ==========================

@app.route('/')

def homepage():

    bolos = Bolo.query.order_by(
        Bolo.id.desc()
    ).all()

    bolos_json = json.dumps([

        {

            "id": b.id,

            "nome": b.nome,

            "preco": b.preco,

            "descricao": b.descricao,

            "img": f"/static/imagens/{b.imagem}",

            "tag": "Especial",

            "ingredientes": [

                "Artesanal",

                "Premium"

            ]

        }

        for b in bolos

    ])

    return render_template(

        'index.html',

        bolos_json=bolos_json

    )


# ==========================
# CHEFES
# ==========================

@app.route('/chefes')

def chefes():

    return render_template(

        'chefes.html',

        chefes=chefes_lista

    )


# ==========================
# CADASTRO
# ==========================

@app.route(

    '/cadastro',

    methods=[

        'GET',

        'POST'

    ]

)

def cadastro():

    mensagem = None

    if request.method == 'POST':

        nome = request.form.get(
            'nome'
        )

        email = request.form.get(
            'email'
        )

        existe = Usuario.query.filter_by(

            email=email

        ).first()

        if existe:

            mensagem = (

                'Email já cadastrado'

            )

        else:

            novo = Usuario(

                nome=nome,

                email=email

            )

            database.session.add(

                novo

            )

            database.session.commit()

            mensagem = (

                'Cadastro realizado com sucesso'

            )

    return render_template(

        'cadastro.html',

        mensagem=mensagem

    )


# ==========================
# LISTA DE USUÁRIOS
# ==========================

@app.route('/usuarios')

def usuarios():

    lista = Usuario.query.all()

    return render_template(

        'usuarios.html',

        usuarios=lista

    )

# ==========================
# LOGIN ADMIN
# ==========================

@app.route(

    '/login-admin',

    methods=[

        'GET',

        'POST'

    ]

)

def login_admin():

    mensagem = None

    if request.method == 'POST':

        usuario = request.form.get(
            'usuario'
        )

        senha = request.form.get(
            'senha'
        )

        if (

            usuario == 'admin'

            and

            senha == '123456'

        ):

            session['admin'] = True

            return redirect(
                '/admin/bolos'
            )

        else:

            mensagem = (
                'Usuário ou senha inválidos'
            )

    return render_template(

        'login_admin.html',

        mensagem=mensagem

    )

# ==========================
# ADMIN - BOLOS
# ==========================

@app.route(

    '/admin/bolos',

    methods=[

        'GET',

        'POST'

    ]

)


def admin_bolos():
    if not session.get('admin'):

        return redirect(
            '/login-admin'
        )
    mensagem = None

    if request.method == 'POST':

        nome = request.form.get(
            'nome'
        )

        preco = float(

            request.form.get(
                'preco'
            )

        )

        descricao = request.form.get(
            'descricao'
        )

        imagem = request.form.get(
            'imagem'
        )

        novo_bolo = Bolo(

            nome=nome,

            preco=preco,

            descricao=descricao,

            imagem=imagem

        )

        database.session.add(

            novo_bolo

        )

        database.session.commit()

        mensagem = (

            'Bolo cadastrado com sucesso'

        )

    lista_bolos = Bolo.query.all()
    total_bolos = len(lista_bolos)
    return render_template(

        'admin_bolos.html',

        mensagem=mensagem,

        bolos=lista_bolos,

        total_bolos=total_bolos

    )

# ==========================
# EDITAR BOLO
# ==========================

@app.route(

    '/editar-bolo/<int:id>',

    methods=[

        'GET',

        'POST'

    ]

)

def editar_bolo(id):

    bolo = Bolo.query.get_or_404(id)

    if request.method == 'POST':

        bolo.nome = request.form.get(
            'nome'
        )

        bolo.preco = float(

            request.form.get(
                'preco'
            )

        )

        bolo.descricao = request.form.get(
            'descricao'
        )

        bolo.imagem = request.form.get(
            'imagem'
        )

        database.session.commit()

        return redirect(
            '/admin/bolos'
        )

    return render_template(

        'editar_bolo.html',

        bolo=bolo

    )

# ==========================
# EXCLUIR BOLO
# ==========================

@app.route(

    '/deletar-bolo/<int:id>'

)

def deletar_bolo(id):

    bolo = Bolo.query.get_or_404(id)

    database.session.delete(

        bolo

    )

    database.session.commit()

    return redirect(

        '/admin/bolos'

    )
# ==========================
# LOGOUT ADMIN
# ==========================

@app.route('/logout')

def logout():

    session.pop(

        'admin',

        None

    )

    return redirect(

        '/login-admin'

    )

# ==========================
# SALVAR PEDIDO
# ==========================

@app.route(
    '/salvar-pedido',
    methods=['POST']
)
def salvar_pedido():

    print("ROTA CHAMADA")

    dados = request.json

    print(dados)

    pedido = Pedido(

        nome_cliente=dados['cliente'],

        telefone=dados['telefone'],

        bolo=dados['bolo']

    )

    database.session.add(
        pedido
    )

    database.session.commit()

    print("PEDIDO SALVO")

    return jsonify({

        'sucesso': True

    })

@app.route('/admin/pedidos')
def admin_pedidos():

    if not session.get('admin'):
        return redirect('/login-admin')

    busca = request.args.get('busca')
    status = request.args.get('status')

    query = Pedido.query

    if busca:
        query = query.filter(
            Pedido.nome_cliente.contains(busca)
        )

    if status:
        query = query.filter_by(
            status=status
        )

    pedidos = query.order_by(
        Pedido.id.desc()
    ).all()

    total_pedidos = len(pedidos)

    pendentes = len([
        p for p in pedidos
        if p.status == 'Pendente'
    ])

    concluidos = len([
        p for p in pedidos
        if p.status == 'Concluído'
    ])

    return render_template(

        'admin_pedidos.html',

        pedidos=pedidos,

        total_pedidos=total_pedidos,

        pendentes=pendentes,

        concluidos=concluidos

    )

# ==========================
# EXPORTAR PEDIDOS CSV
# ==========================

@app.route('/exportar-pedidos')
def exportar_pedidos():

    if not session.get('admin'):
        return redirect('/login-admin')

    pedidos = Pedido.query.all()

    csv_data = "ID,Cliente,Telefone,Bolo,Data,Status\n"

    for pedido in pedidos:
        data_formatada = pedido.data.strftime(
            "%d/%m/%Y %H:%M"
        )

        csv_data += (
            f"{pedido.id},"
            f"{pedido.nome_cliente},"
            f"{pedido.telefone},"
            f"{pedido.bolo},"
            f"{data_formatada},"
            f"{pedido.status}\n"
        )

    response = make_response(csv_data)

    response.headers[
        "Content-Disposition"
    ] = "attachment; filename=pedidos.csv"

    response.headers[
        "Content-Type"
    ] = "text/csv"

    return response

# ==========================
# PEDIDO
# ==========================

@app.route('/alterar-status/<int:id>')
def alterar_status(id):
    if not session.get('admin'):
        return redirect('/login-admin')
    pedido = Pedido.query.get_or_404(id)

    if pedido.status == 'Pendente':

        pedido.status = 'Concluído'

    else:

        pedido.status = 'Pendente'

    database.session.commit()

    return redirect('/admin/pedidos')

@app.route('/deletar-pedido/<int:id>')
def deletar_pedido(id):
    if not session.get('admin'):
        return redirect('/login-admin')
    pedido = Pedido.query.get_or_404(id)

    database.session.delete(pedido)

    database.session.commit()

    return redirect('/admin/pedidos')

@app.route(

    '/pedido',

    methods=[

        'GET',

        'POST'

    ]

)

def pedido():

    mensagem = None

    if request.method == 'POST':

        nome = request.form.get(
            'nome'
        )

        mensagem = (

            f'Pedido enviado com sucesso, {nome}!'

        )

    return render_template(

        'pedido.html',

        mensagem=mensagem

    )


# ==========================
# ERRO 404
# ==========================

@app.errorhandler(404)

def pagina_nao_encontrada(e):

    return render_template(

        '404.html'

    ), 404


# ==========================
# CRIAR TABELAS
# ==========================

print(Pedido)

with app.app_context():

    database.create_all()


# ==========================
# EXECUTAR
# ==========================

if __name__ == '__main__':

    app.run(

        debug=True

    )