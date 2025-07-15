'use client';

import { useState } from 'react';
import axios from 'axios';

export default function SolicitarProdutoPage() {
  const [form, setForm] = useState({
    nome: '',
    descricao: '',
    imagem_url: '',
    categoria: '',
    marca: '',
  });

  const [mensagem, setMensagem] = useState('');

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post('/api/solicitar-produto/', form);
      setMensagem('Produto solicitado com sucesso!');
      setForm({ nome: '', descricao: '', imagem_url: '', categoria: '', marca: '' });
    } catch (err) {
      setMensagem('Erro ao solicitar produto. Verifique os dados.');
    }
  };

  return (
    <div className="max-w-2xl mx-auto py-8 px-4">
      <h1 className="text-2xl font-bold mb-4">Solicitar Novo Produto</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="text"
          name="nome"
          placeholder="Nome do Produto"
          value={form.nome}
          onChange={handleChange}
          className="w-full border p-2 rounded"
          required
        />
        <textarea
          name="descricao"
          placeholder="Descrição"
          value={form.descricao}
          onChange={handleChange}
          className="w-full border p-2 rounded"
          rows={4}
        />
        <input
          type="url"
          name="imagem_url"
          placeholder="URL da Imagem"
          value={form.imagem_url}
          onChange={handleChange}
          className="w-full border p-2 rounded"
        />
        <input
          type="text"
          name="categoria"
          placeholder="Categoria"
          value={form.categoria}
          onChange={handleChange}
          className="w-full border p-2 rounded"
        />
        <input
          type="text"
          name="marca"
          placeholder="Marca"
          value={form.marca}
          onChange={handleChange}
          className="w-full border p-2 rounded"
        />
        <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded">
          Enviar Solicitação
        </button>
      </form>
      {mensagem && <p className="mt-4 text-sm text-center">{mensagem}</p>}
    </div>
  );
}
