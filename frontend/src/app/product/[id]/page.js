// frontend/src/app/product/[id]/page.js
// Use Client Component se houver interatividade (como formulário de comentário)
"use client";

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation'; // Para navegação
// Se estiver usando o App Router, 'params' é passado como prop para o componente da página
// import { useParams } from 'next/navigation'; // Com o App Router, 'params' é uma prop

// Simular um carregamento de componente, caso o template seja grande
// import dynamic from 'next/dynamic';
// const Header = dynamic(() => import('../../components/Header'), { ssr: false });
// const Footer = dynamic(() => import('../../components/Footer'), { ssr: false });


export default function ProductDetailPage({ params }) {
  const { id } = params; // Captura o ID do produto da URL (App Router)
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const router = useRouter(); // Para o botão de voltar

  useEffect(() => {
    async function fetchProduct() {
      try {
        // Use a URL completa do seu backend Django ou configure o proxy no next.config.js
        // Se você configurou o proxy: const response = await fetch(`/api/django/produto/${id}/`);
        const response = await fetch(`http://localhost:8000/produto/${id}/`); 
        
        if (!response.ok) {
          if (response.status === 404) {
            setError("Produto não encontrado.");
          } else {
            setError("Erro ao carregar os detalhes do produto.");
          }
          setProduct(null); // Limpa o produto se houver erro
          return;
        }

        const data = await response.json();
        setProduct(data);
      } catch (err) {
        console.error("Failed to fetch product:", err);
        setError("Erro de rede ao carregar o produto.");
      } finally {
        setLoading(false);
      }
    }

    if (id) {
      fetchProduct();
    }
  }, [id]); // Roda o efeito novamente se o ID da URL mudar

  if (loading) {
    return (
      <div style={{ fontFamily: 'sans-serif', textAlign: 'center', marginTop: '50px' }}>
        <h2>Carregando Produto...</h2>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ fontFamily: 'sans-serif', textAlign: 'center', marginTop: '50px' }}>
        <h2>{error}</h2>
        <p><a href={reverse('product_catalog')}>Voltar ao Catálogo</a></p> {/* Se product_catalog for URL Django */}
        <p><a href="/product_catalog">Voltar ao Catálogo (Frontend)</a></p> {/* Se for URL do Frontend Next.js */}
      </div>
    );
  }

  if (!product) { // Caso não haja produto (e nenhum erro específico)
    return (
      <div style={{ fontFamily: 'sans-serif', textAlign: 'center', marginTop: '50px' }}>
        <h2>Produto não encontrado.</h2>
        <p><a href="/product_catalog">Voltar ao Catálogo</a></p>
      </div>
    );
  }

  // Geração do HTML para as ofertas
  const offersHtml = product.offers && product.offers.length > 0
    ? product.offers.map((offer, index) => (
        <div className="offer-item" key={index}>
          <span className="store-name">{offer.store}</span>
          <span className="offer-price">R$ {offer.price.toFixed(2).replace('.', ',')}</span>
        </div>
      ))
    : <p>Nenhuma oferta encontrada para este produto.</p>;

  return (
    // Utilize a estrutura do seu template Next.js aqui
    // Este é apenas um exemplo simplificado com estilos inline
    <div className="container" style={{ maxWidth: '800px', margin: '0 auto', padding: '20px', backgroundColor: '#fff', boxShadow: '0 0 10px rgba(0, 0, 0, 0.1)', borderRadius: '8px', textAlign: 'center' }}>
      <div className="product-detail-card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '20px' }}>
        <img src={product.imageUrl} alt={`${product.name} Imagem`} style={{ maxWidth: '250px', height: 'auto', borderRadius: '8px' }} />
        <div className="product-info" style={{ textAlign: 'left' }}>
          <h2>{product.name}</h2>
          <p><strong>ID:</strong> {product.id}</p>
          <p><strong>Descrição:</strong> {product.description}</p>
          <p><strong>Categoria:</strong> {product.category || 'N/A'}</p>
          <p style={{ fontSize: '1.5em', fontWeight: 'bold', color: '#28a745', marginTop: '15px' }}>Menor Preço: R$ {product.min_price ? product.min_price.toFixed(2).replace('.', ',') : 'N/A'}</p>
        </div>

        <div className="offers-section" style={{ marginTop: '30px', textAlign: 'left', width: '100%' }}>
          <h3>Ofertas Encontradas</h3>
          <div id="offersList">
            {offersHtml}
          </div>
        </div>

        <div className="comment-section" style={{ marginTop: '40px', textAlign: 'left', width: '100%' }}>
          <h3>Deixe seu Comentário</h3>
          <textarea placeholder="Escreva seu comentário sobre o produto, loja ou ambos..." style={{ width: 'calc(100% - 22px)', padding: '10px', border: '1px solid #ccc', borderRadius: '5px', minHeight: '80px', marginBottom: '10px' }}></textarea>
          <button style={{ padding: '10px 20px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}>Enviar Comentário</button>
        </div>

      </div>
      <br />
      <a href="/product_catalog" style={{ color: '#007bff', textDecoration: 'none' }}>Voltar ao Catálogo</a>
    </div>
  );
}