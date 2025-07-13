// frontend/src/app/product_catalog/page.js
"use client"; // Marca como Client Component para usar useState, useEffect, etc.

import React, { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

export default function ProductCatalogPage() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const router = useRouter();
  const searchParams = useSearchParams();

  // Função para buscar os produtos da API Django
  const fetchProducts = async (query = '') => {
    setLoading(true);
    setError(null);
    try {
      // Usa o proxy configurado em next.config.js para chamar a URL Django
      // A URL aqui é a mesma definida no Django, mas acessada via proxy do Next.js
      const response = await fetch(`/api/django/product_cata    log/?q=${encodeURIComponent(query)}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setProducts(data.products); // 'products' porque sua view Django retorna {"products": produtos_data}
    } catch (e) {
      setError('Falha ao carregar produtos. ' + e.message);
      console.error('Erro ao buscar produtos:', e);
    } finally {
      setLoading(false);
    }
  };

  // Carregar produtos na primeira renderização e quando a query muda na URL
  useEffect(() => {
    const query = searchParams.get('q') || '';
    setSearchQuery(query); // Atualiza o estado da query para o input
    fetchProducts(query);
  }, [searchParams]); // Re-executa quando os parâmetros de busca mudam

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    router.push(`/product_catalog?q=${encodeURIComponent(searchQuery)}`);
  };

  const handleProductClick = (productId) => {
    // Redireciona para a página de detalhes do produto no Next.js
    // A URL aqui é a do Next.js, que corresponderá a um arquivo como
    // frontend/src/app/produto/[productId]/page.js (se seguir o padrão dinâmico)
    router.push(`/produto/${productId}`);
  };

  if (loading) return <p style={{ textAlign: 'center', marginTop: '50px' }}>Carregando produtos...</p>;
  if (error) return <p style={{ textAlign: 'center', marginTop: '50px', color: 'red' }}>Erro: {error}</p>;

  return (
    <div style={{ fontFamily: 'sans-serif', textAlign: 'center', marginTop: '50px' }}>
      <h1>Catálogo de Produtos</h1>
      <p className="welcome">Bem-vindo ao catálogo!</p>
      <div style={{ marginBottom: '20px', display: 'flex', gap: '10px', maxWidth: '600px', margin: '20px auto' }}>
        <input
          type="text"
          id="searchInput"
          placeholder="Pesquisar produtos..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={{ flexGrow: 1, padding: '10px', border: '1px solid #ccc', borderRadius: '5px' }}
        />
        <button onClick={handleSearchSubmit} style={{ padding: '10px 15px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}>Pesquisar</button>
      </div>
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
        gap: '25px',
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '20px',
        backgroundColor: '#fff',
        boxShadow: '0 0 10px rgba(0, 0, 0, 0.1)',
        borderRadius: '8px',
      }}>
        {products.length > 0 ? (
          products.map(product => (
            <div
              key={product.id}
              className="product-card"
              onClick={() => handleProductClick(product.id)}
              style={{
                padding: '20px',
                textAlign: 'center',
                border: '1px solid #ddd',
                borderRadius: '8px',
                cursor: 'pointer',
                transition: 'transform 0.2s ease-in-out',
              }}
            >
              <img src={product.imageUrl || 'https://placehold.co/150x150/E0E0E0/333333?text=Sem+Imagem'} alt={product.name} style={{ maxWidth: '100%', height: 'auto', borderRadius: '4px', marginBottom: '10px' }} />
              <h3>{product.name}</h3>
              <p style={{ fontWeight: 'bold', color: '#28a745' }}>R$ {product.min_price !== null ? product.min_price.toFixed(2).replace('.', ',') : 'N/A'}</p>
            </div>
          ))
        ) : (
          <p style={{ gridColumn: '1 / -1' }}>Nenhum produto encontrado.</p>
        )}
      </div>
    </div>
  );
}