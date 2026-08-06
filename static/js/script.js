let cart = [];

function renderEstrelas(media, tamanho){
    tamanho = tamanho || '0.85rem';
    let html = '';

    for(let i = 1; i <= 5; i++){
        if(media >= i){
            html += `<i class="fa-solid fa-star" style="color:var(--gold); font-size:${tamanho};"></i>`;
        }else if(media >= i - 0.5){
            html += `<i class="fa-solid fa-star-half-stroke" style="color:var(--gold); font-size:${tamanho};"></i>`;
        }else{
            html += `<i class="fa-regular fa-star" style="color:rgba(201,168,76,0.4); font-size:${tamanho};"></i>`;
        }
    }

    return html;
}

function renderCards(data){

    const c = document.getElementById('bolo-cards');

    if(!c) return;

    if(!data.length){

        c.innerHTML = `
        <div class="no-results col-12">
            Nenhum bolo encontrado.
        </div>
        `;

        return;
    }

    c.innerHTML = data.map((b,i)=>`

    <div class="col">

        <div class="bolo-card" style="animation-delay:${i*.1}s">

            <div class="card-img-wrapper">

                <img
                src="${b.img || 'https://placehold.co/500x350'}"
                alt="${b.nome}">

                <span class="badge-tag">
                    ${b.tag}
                </span>

            </div>

            <div class="card-body">

                <div class="card-title">
                    ${b.nome}
                </div>

                <div class="card-price">
                    R$ ${b.preco.toFixed(2).replace('.',',')}
                </div>

                <div style="margin-bottom:0.6rem; font-family:'Josefin Sans',sans-serif; font-size:0.75rem; color:rgba(250,243,232,0.5);">
                    ${renderEstrelas(b.media_avaliacao)}
                    <span style="margin-left:4px;">${b.total_avaliacoes > 0 ? `${b.media_avaliacao} (${b.total_avaliacoes})` : 'Sem avaliações'}</span>
                </div>

                <p class="card-desc">
                    ${b.descricao}
                </p>

                <div class="card-tags">
                    ${b.ingredientes.map(i =>
                    `<span class="ingredient-tag">${i}</span>`
                    ).join('')}
                </div>

                <div class="card-actions">

                    <button
                    class="btn-ingredient"
                    onclick="openIngredientes(${b.id})">

                    Detalhes

                    </button>

                    <button
                    class="btn-add-cart"
                    onclick="addToCart(${b.id})">

                    + Carrinho

                    </button>

                </div>

            </div>

        </div>

    </div>

    `).join('');
}

function filterCakes(){

    const q =
    document.getElementById('ingredient-search')
    ?.value
    .toLowerCase()
    .trim();

    if(!q){

        renderCards(bolos);
        return;
    }

    renderCards(

        bolos.filter(

            b =>

            b.nome.toLowerCase().includes(q)

            ||

            b.descricao.toLowerCase().includes(q)

            ||

            b.ingredientes.some(

                i => i.toLowerCase().includes(q)

            )

        )

    );
}

function openIngredientes(id){

    const b = bolos.find(x => x.id === id);

    if(!b) return;

    const detalhes =
    document.getElementById('ingredientes-detalhes');

    if(!detalhes) return;

    detalhes.innerHTML = `
        <h3>${b.nome}</h3>
        <p>${b.descricao}</p>
        <p class="price-tag">R$ ${b.preco.toFixed(2).replace('.',',')}</p>
    `;

    const img =
    document.getElementById('ingredientes-img');

    if(img){

        img.src =
        b.img ||
        'https://placehold.co/500x350';
    }

    document
    .getElementById('ingredientes-modal')
    ?.classList.add('active');

    carregarAvaliacoes(id);
    carregarFormAvaliacao(id);
}

function montarEstrelasInput(container, notaAtual){

    notaAtual = notaAtual || 0;

    container.innerHTML = '';

    for(let i = 1; i <= 5; i++){

        const estrela = document.createElement('i');
        estrela.className = i <= notaAtual ? 'fa-solid fa-star' : 'fa-regular fa-star';
        estrela.style.color = 'var(--crimson)';
        estrela.style.fontSize = '1.4rem';
        estrela.style.cursor = 'pointer';
        estrela.style.marginRight = '4px';
        estrela.dataset.valor = i;

        estrela.addEventListener('click', () => {
            container.dataset.notaSelecionada = i;
            Array.from(container.children).forEach((el, idx) => {
                el.className = (idx + 1) <= i ? 'fa-solid fa-star' : 'fa-regular fa-star';
            });
        });

        container.appendChild(estrela);
    }

    container.dataset.notaSelecionada = notaAtual;
}

async function carregarAvaliacoes(boloId){

    const mediaEl = document.getElementById('avaliacao-media');
    const listaEl = document.getElementById('avaliacao-lista');

    if(!mediaEl || !listaEl) return;

    mediaEl.innerHTML = '<small class="text-secondary">Carregando avaliações...</small>';
    listaEl.innerHTML = '';

    try{

        const resposta = await fetch(`/api/avaliacoes/${boloId}`);
        const dados = await resposta.json();

        mediaEl.innerHTML = `
            <strong style="font-family:'Josefin Sans',sans-serif; font-size:0.7rem; letter-spacing:0.1em; text-transform:uppercase; color:#3a2020;">
                Avaliações
            </strong>
            <div style="margin-top:4px;">
                ${renderEstrelas(dados.media, '1.1rem')}
                <span style="margin-left:6px; font-family:'Cormorant Garamond',serif; color:#3a2020;">
                    ${dados.total > 0 ? `${dados.media} de 5 (${dados.total} avaliação${dados.total === 1 ? '' : 'ões'})` : 'Ainda sem avaliações'}
                </span>
            </div>
        `;

        if(dados.avaliacoes.length){
            listaEl.innerHTML = dados.avaliacoes.map(a => `
                <div style="padding:0.6rem 0; border-bottom:1px solid rgba(0,0,0,0.06);">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <strong style="font-family:'Cormorant Garamond',serif; color:#3a2020;">${a.usuario_nome}</strong>
                        <span>${renderEstrelas(a.nota, '0.75rem')}</span>
                    </div>
                    ${a.comentario ? `<p style="font-family:'Cormorant Garamond',serif; font-style:italic; color:#5a4040; margin:4px 0 0; font-size:0.9rem;">"${a.comentario}"</p>` : ''}
                    <small class="text-secondary">${a.data}</small>
                </div>
            `).join('');
        }

    }catch(e){
        console.log('Erro ao carregar avaliações:', e);
        mediaEl.innerHTML = '<small class="text-secondary">Não foi possível carregar as avaliações.</small>';
    }
}

async function carregarFormAvaliacao(boloId){

    const container = document.getElementById('avaliacao-form-container');

    if(!container) return;

    container.innerHTML = '';

    try{

        const resposta = await fetch(`/api/pode-avaliar/${boloId}`);
        const dados = await resposta.json();

        if(!dados.pode_avaliar){

            if(dados.motivo === 'login'){
                container.innerHTML = `<small class="text-secondary"><a href="/login">Entre na sua conta</a> para avaliar este bolo depois de recebê-lo.</small>`;
            }else{
                container.innerHTML = `<small class="text-secondary">Você poderá avaliar este bolo depois que seu pedido for marcado como "Entregue".</small>`;
            }

            return;
        }

        const notaAtual = dados.avaliacao_existente ? dados.avaliacao_existente.nota : 0;
        const comentarioAtual = dados.avaliacao_existente ? (dados.avaliacao_existente.comentario || '') : '';

        container.innerHTML = `
            <strong style="font-family:'Josefin Sans',sans-serif; font-size:0.7rem; letter-spacing:0.1em; text-transform:uppercase; color:#3a2020;">
                ${dados.avaliacao_existente ? 'Editar sua avaliação' : 'Avalie este bolo'}
            </strong>
            <div id="estrelas-input" class="mt-2 mb-2"></div>
            <textarea id="comentario-avaliacao" class="form-control mb-2" rows="2" placeholder="Conte como foi sua experiência (opcional)">${comentarioAtual}</textarea>
            <p class="checkout-erro" id="avaliacao-erro"></p>
            <button class="btn-add-modal" style="font-size:0.62rem; padding:0.55rem 1.5rem;" onclick="enviarAvaliacao(${boloId})">
                ${dados.avaliacao_existente ? 'Atualizar Avaliação' : 'Enviar Avaliação'}
            </button>
        `;

        montarEstrelasInput(document.getElementById('estrelas-input'), notaAtual);

    }catch(e){
        console.log('Erro ao verificar elegibilidade de avaliação:', e);
    }
}

async function enviarAvaliacao(boloId){

    const estrelasContainer = document.getElementById('estrelas-input');
    const comentario = document.getElementById('comentario-avaliacao')?.value.trim();
    const erro = document.getElementById('avaliacao-erro');

    const nota = parseInt(estrelasContainer?.dataset.notaSelecionada || '0', 10);

    if(!nota){
        if(erro){
            erro.textContent = 'Selecione uma nota de 1 a 5 estrelas.';
            erro.classList.add('show');
        }
        return;
    }

    if(erro){
        erro.classList.remove('show');
        erro.textContent = '';
    }

    try{

        const resposta = await fetch(`/api/avaliar/${boloId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nota, comentario })
        });

        const dados = await resposta.json();

        if(!dados.sucesso){
            if(erro){
                erro.textContent = dados.erro || 'Não foi possível enviar sua avaliação.';
                erro.classList.add('show');
            }
            return;
        }

        carregarAvaliacoes(boloId);
        carregarFormAvaliacao(boloId);
        showToast();

    }catch(e){
        console.log('Erro ao enviar avaliação:', e);
        if(erro){
            erro.textContent = 'Erro de conexão. Tente novamente.';
            erro.classList.add('show');
        }
    }
}

function closeIngredientes(){

    document
    .getElementById('ingredientes-modal')
    ?.classList.remove('active');
}

const modal =
document.getElementById('ingredientes-modal');

if(modal){

    modal.addEventListener(

        'click',

        function(e){

            if(e.target === this){

                closeIngredientes();
            }
        }
    );
}

function addToCart(id){

    const b = bolos.find(x => x.id === id);

    if(!b) return;

    const ex =
    cart.find(i => i.id === id);

    if(ex){

        ex.qty++;

    }else{

        cart.push({

            ...b,

            qty:1

        });
    }

    updateCartUI();

    showToast();
}

function changeQty(id,delta){

    const item =
    cart.find(i => i.id === id);

    if(!item) return;

    item.qty += delta;

    if(item.qty <= 0){

        cart =
        cart.filter(i => i.id !== id);
    }

    updateCartUI();
}

function updateCartUI(){

    const total =
    cart.reduce(

        (s,i)=>

        s + i.preco * i.qty,

        0

    );

    const count =
    document.getElementById('cart-count');

    if(count){

        count.textContent =

        cart.reduce(

            (s,i)=>s+i.qty,

            0

        );
    }

    const cartItems =
    document.getElementById('cart-items');

    if(cartItems){

        if(!cart.length){

            cartItems.innerHTML = `
            <p style="text-align:center;padding:20px;">
                Carrinho vazio
            </p>
            `;

        }else{

cartItems.innerHTML =

cart.map(i => `

<div style="
padding:12px;
border-bottom:1px solid #333;
margin-bottom:10px;
">

    <strong>${i.nome}</strong>

    <br>

    Quantidade: ${i.qty}

    <br>

    Valor:
    R$ ${(i.preco * i.qty).toFixed(2)}

    <br><br>

    <button
    onclick="changeQty(${i.id}, -1)"
    class="btn btn-danger btn-sm">

        Remover

    </button>

</div>

`).join('');
        }
    }

    const cartTotal =
    document.getElementById('cart-total');

    if(cartTotal){

        cartTotal.textContent =
        'R$ ' + total.toFixed(2);
    }
}

function toggleCart(){

    document
    .getElementById('cart-modal')
    ?.classList.toggle('open');
}

function salvarPedidoLocal(codigo){

    const LIMITE_SALVOS = 20;

    let codigos = [];

    try{
        codigos = JSON.parse(localStorage.getItem('luarRubroPedidos') || '[]');
    }catch(e){
        codigos = [];
    }

    codigos = codigos.filter(c => c !== codigo);
    codigos.push(codigo);

    if(codigos.length > LIMITE_SALVOS){
        codigos = codigos.slice(codigos.length - LIMITE_SALVOS);
    }

    localStorage.setItem('luarRubroPedidos', JSON.stringify(codigos));
}

async function atualizarSeloMeusPedidos(){

    const badge = document.getElementById('meus-pedidos-count');

    if(!badge) return;

    let codigos = [];

    try{
        codigos = JSON.parse(localStorage.getItem('luarRubroPedidos') || '[]');
    }catch(e){
        codigos = [];
    }

    if(!codigos.length){
        badge.style.display = 'none';
        return;
    }

    try{

        const resposta = await fetch('/api/meus-pedidos', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ codigos })
        });

        const dados = await resposta.json();

        const emAndamento = (dados.pedidos || []).filter(p => p.status !== 'Entregue').length;

        if(emAndamento > 0){
            badge.textContent = emAndamento;
            badge.style.display = 'flex';
        }else{
            badge.style.display = 'none';
        }

    }catch(e){
        console.log('Erro ao verificar pedidos em andamento:', e);
    }
}

function checkoutWhatsApp(){

    if(!cart.length){

        alert('Carrinho vazio!');
        return;
    }

    openCheckout();
}

function openCheckout(){

    document
    .getElementById('checkout-modal')
    ?.classList.add('active');
}

function closeCheckout(){

    document
    .getElementById('checkout-modal')
    ?.classList.remove('active');

    const erro = document.getElementById('checkout-erro');

    if(erro){
        erro.classList.remove('show');
        erro.textContent = '';
    }
}

function confirmarCheckout(){

    const nome =
    document.getElementById('checkout-nome')?.value.trim();

    const telefone =
    document.getElementById('checkout-telefone')?.value.trim();

    const pagamento =
    document.getElementById('checkout-pagamento')?.value;

    const erro = document.getElementById('checkout-erro');

    if(!nome || !telefone || !pagamento){

        if(erro){
            erro.textContent = 'Preencha todos os campos antes de continuar.';
            erro.classList.add('show');
        }

        return;
    }

    if(erro){
        erro.classList.remove('show');
        erro.textContent = '';
    }

    // Avança para a etapa de endereço, mantendo os dados já preenchidos
    document.getElementById('checkout-modal')?.classList.remove('active');
    document.getElementById('endereco-modal')?.classList.add('active');
}

function voltarParaCheckout(){

    document.getElementById('endereco-modal')?.classList.remove('active');
    document.getElementById('checkout-modal')?.classList.add('active');
}

function closeEndereco(){

    document
    .getElementById('endereco-modal')
    ?.classList.remove('active');

    const erro = document.getElementById('endereco-erro');

    if(erro){
        erro.classList.remove('show');
        erro.textContent = '';
    }
}

async function confirmarEndereco(){

    const nome =
    document.getElementById('checkout-nome')?.value.trim();

    const telefone =
    document.getElementById('checkout-telefone')?.value.trim();

    const pagamento =
    document.getElementById('checkout-pagamento')?.value;

    const endereco =
    document.getElementById('endereco-completo')?.value.trim();

    const complemento =
    document.getElementById('endereco-complemento')?.value.trim();

    const erro = document.getElementById('endereco-erro');

    if(!endereco){

        if(erro){
            erro.textContent = 'Informe o endereço de entrega.';
            erro.classList.add('show');
        }

        return;
    }

    if(erro){
        erro.classList.remove('show');
        erro.textContent = '';
    }

    const botaoConfirmar = document.querySelector('#endereco-modal .checkout-confirm[onclick="confirmarEndereco()"]');
    if(botaoConfirmar){
        botaoConfirmar.disabled = true;
        botaoConfirmar.textContent = 'Enviando...';
    }

    try{

        const resposta = await fetch('/salvar-pedido', {

            method: 'POST',

            headers: { 'Content-Type': 'application/json' },

            body: JSON.stringify({
                cliente: nome,
                telefone: telefone,
                forma_pagamento: pagamento,
                endereco: endereco,
                complemento: complemento,
                itens: cart.map(item => ({
                    nome: item.nome,
                    quantidade: item.qty,
                    bolo_id: item.id
                }))
            })
        });

        const dados = await resposta.json();

        if(!dados.sucesso){

            if(erro){
                erro.textContent = dados.erro || 'Não foi possível enviar o pedido. Tente novamente.';
                erro.classList.add('show');
            }

            if(botaoConfirmar){
                botaoConfirmar.disabled = false;
                botaoConfirmar.textContent = 'Confirmar Pedido';
            }

            return;
        }

        // Sucesso: limpa o carrinho, mostra a tela de carregamento e depois leva
        // o cliente para a página de acompanhamento
        cart = [];
        updateCartUI();

        salvarPedidoLocal(dados.codigo);

        document.getElementById('endereco-modal')?.classList.remove('active');
        document.getElementById('pedido-processando-overlay')?.classList.add('active');

        setTimeout(() => {
            window.location.href = `/acompanhar/${dados.codigo}`;
        }, 1800);

    }catch(e){

        console.log('Erro ao enviar pedido:', e);

        if(erro){
            erro.textContent = 'Erro de conexão. Verifique sua internet e tente novamente.';
            erro.classList.add('show');
        }

        if(botaoConfirmar){
            botaoConfirmar.disabled = false;
            botaoConfirmar.textContent = 'Confirmar Pedido';
        }
    }
}

function showToast(){

    const t =
    document.getElementById(
        'toast-notification'
    );

    if(!t) return;

    t.classList.add('show');

    setTimeout(

        ()=>{

            t.classList.remove('show');

        },

        2000

    );
}

function hidePreloader(){

    const el =
    document.getElementById(
        'preloader-overlay'
    );

    if(!el) return;

    el.style.opacity='0';

    setTimeout(

        ()=>{

            el.style.display='none';

        },

        600

    );
}

document.addEventListener(

    'DOMContentLoaded',

    ()=>{

        try{

            renderCards(bolos);

            updateCartUI();

            atualizarSeloMeusPedidos();

        }catch(e){

            console.log(e);
        }

        setTimeout(

            hidePreloader,

            3000

        );
    }
);

hidePreloader();