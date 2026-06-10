let cart = [];

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
        <p>R$ ${b.preco}</p>
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

async function checkoutWhatsApp(){

    if(!cart.length){

        alert('Carrinho vazio!');
        return;
    }

    const cliente =
    prompt('Nome do cliente:');

    if(!cliente) return;

    const telefone =
    prompt('Telefone:');

    if(!telefone) return;

    for(const item of cart){

        await fetch(

            '/salvar-pedido',

            {

                method:'POST',

                headers:{

                    'Content-Type':
                    'application/json'
                },

                body:JSON.stringify({

                    cliente:cliente,

                    telefone:telefone,

                    bolo:`${item.nome} - Qtd: ${item.qty}`

                })
            }
        );
    }

    alert('Pedido enviado com sucesso!');

    cart = [];

    updateCartUI();
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