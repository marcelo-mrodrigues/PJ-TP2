/**
 * @fileoverview
 * Script responsável por controlar a interface do carrinho de compras (offcanvas).
 * Permite adicionar e remover produtos dinamicamente, usando requisições AJAX,
 * e atualiza o painel lateral do carrinho.
 * 
 * URLs da API são extraídas do atributo `data-*` do elemento `<body>`.
 * 
 * Requisitos:
 * - Bootstrap Offcanvas
 * - Elementos com classes `.add-to-cart-btn`, `.remove-from-cart-btn`
 * - Meta tag CSRF para Django
 * 
 */

document.addEventListener('DOMContentLoaded', function() {
    /** @type {HTMLElement} */
    const cartItemsList = document.getElementById('cart-items-list');
    /** @type {HTMLElement} */
    const cartTotalPrice = document.getElementById('cart-total-price');
    /** @type {HTMLElement} */
    const cartIconTotal = document.querySelector('.cart-total');
    /** @type {HTMLElement} */ 
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    // Pega todas as URLs da API a partir do body
    const getCartUrl = document.body.dataset.getCartUrl;
    const addToCartUrl = document.body.dataset.addToCartUrl;
    const removeFromCartUrl = document.body.dataset.removeFromCartUrl; // <-- Nova URL

    /**
     * Atualiza visualmente o conteúdo do carrinho (offcanvas).
     * @param {Object} cartData - Objeto retornado pela API contendo itens e total.
     * @param {Array<Object>} cartData.items - Lista de itens do carrinho.
     * @param {string|number} cartData.total - Valor total do carrinho.
     */
    function updateCartOffcanvas(cartData) {
        if (!cartItemsList || !cartTotalPrice) return;

        cartItemsList.innerHTML = '';

        if (cartData.items && cartData.items.length > 0) {
            cartData.items.forEach(item => {
                const li = document.createElement('li');
                li.className = 'list-group-item d-flex justify-content-between align-items-center';

                // --- HTML DO ITEM DO CARRINHO ATUALIZADO COM BOTÃO DE EXCLUIR ---
                li.innerHTML = `
                    <div class="flex-grow-1 me-3">
                        <h6 class="my-0">${item.nome}</h6>
                        <small class="text-muted">Qtd: ${item.quantity} x R$ ${item.preco}</small>
                    </div>
                    <span class="text-body-secondary fw-bold me-3">R$ ${item.total_item}</span>
                    <button class="btn btn-outline-danger btn-sm remove-from-cart-btn" data-product-id="${item.id}" title="Remover Item">
                        &times;
                    </button>
                `;
                cartItemsList.appendChild(li);
            });
        } else {
            cartItemsList.innerHTML = '<li class="list-group-item text-center text-muted">Seu carrinho está vazio.</li>';
        }

        cartTotalPrice.textContent = `R$ ${cartData.total}`;
        if(cartIconTotal) {
            cartIconTotal.textContent = `R$ ${cartData.total}`;
        }
    }

    /**
     * Busca os dados iniciais do carrinho ao carregar a página.
     */
    async function fetchInitialCart() {
        if (!getCartUrl) return;
        try {
            const response = await fetch(getCartUrl);
            if (!response.ok) return;
            const data = await response.json();
            updateCartOffcanvas(data);
        } catch (error) {
            console.error('Erro ao buscar carrinho inicial:', error);
        }
    }

    /**
     * Lida com cliques em botões de adicionar/remover itens do carrinho.
     */
    document.body.addEventListener('click', function(event) {

        // Lógica para ADICIONAR item
        const addToCartButton = event.target.closest('.add-to-cart-btn');
        if (addToCartButton) {
            event.preventDefault();
            const productId = addToCartButton.dataset.productId;

            const formData = new FormData();
            formData.append('product_id', productId);

            fetch(addToCartUrl, {
                method: 'POST', body: formData, headers: { 'X-CSRFToken': csrfToken }
            })
            .then(response => response.json())
            .then(data => {
                updateCartOffcanvas(data);
                const cartOffcanvas = new bootstrap.Offcanvas(document.getElementById('offcanvasCart'));
                cartOffcanvas.show();
            })
            .catch(error => console.error('Erro ao adicionar item:', error));
        }

        // --- NOVA LÓGICA PARA REMOVER ITEM ---
        const removeFromCartButton = event.target.closest('.remove-from-cart-btn');
        if (removeFromCartButton) {
            event.preventDefault();
            const productId = removeFromCartButton.dataset.productId;

            const formData = new FormData();
            formData.append('product_id', productId);

            fetch(removeFromCartUrl, {
                method: 'POST', body: formData, headers: { 'X-CSRFToken': csrfToken }
            })
            .then(response => response.json())
            .then(data => {
                updateCartOffcanvas(data); // Apenas atualiza o painel
            })
            .catch(error => console.error('Erro ao remover item:', error));
        }
    });

    fetchInitialCart();
});