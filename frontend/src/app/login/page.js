// frontend/src/app/login/page.js
"use client";

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useSearchParams } from 'next/navigation';

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState([]);
  const [successMessage, setSuccessMessage] = useState('');
  const [infoMessage, setInfoMessage] = useState('');

  // Efeito para ler mensagens do Django após redirecionamento
  useEffect(() => {
    const djangoMessages = searchParams.get('messages');
    if (djangoMessages) {
      // Adapte como as mensagens do Django são passadas.
      if (djangoMessages.includes('registrado com sucesso')) {
        setInfoMessage(djangoMessages); // Mensagem informativa de registro bem-sucedido
      } else if (djangoMessages.includes('Login realizado com sucesso')) {
        setSuccessMessage(djangoMessages); // Mensagem de sucesso no login (se o Django redirecionar para a mesma página com sucesso)
      } else {
        setErrors([djangoMessages]); // Assume que são erros
      }
    }
  }, [searchParams]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors([]);
    setSuccessMessage('');
    setInfoMessage('');

    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    try {
      const response = await fetch('http://localhost:8000/login/', { // URL completa do backend Django
        method: 'POST',
        body: formData,
        redirect: 'follow', // Importante para que o fetch siga o redirecionamento do Django
      });

      // Se o Django redirecionar com sucesso, o navegador já estará na página final.
      // Se redirecionar com erros, o Next.js precisará ler os query params ou cookies.
      // Esta parte abaixo é mais para quando o backend NÃO redireciona, mas retorna JSON.
      // Como o Django está redirecionando, a lógica de `useEffect` é mais relevante.

      // Se por algum motivo o Django não redirecionar e retornar um erro HTTP (ex: 400)
      if (!response.ok && response.status !== 302) { // 302 é redirect
          setErrors(['Credenciais inválidas ou erro no servidor.']);
      }

    } catch (error) {
      console.error('Erro ao enviar formulário:', error);
      setErrors(['Erro de conexão. Verifique sua rede.']);
    }
  };

  return (
    <div style={{ fontFamily: 'sans-serif', textAlign: 'center', marginTop: '50px' }}>
      <h2>Login</h2>
      {successMessage && <p style={{ color: 'green' }}>{successMessage}</p>}
      {infoMessage && <p style={{ color: 'blue' }}>{infoMessage}</p>}
      {errors.map((error, index) => (
        <p key={index} style={{ color: 'red' }}>{error}</p>
      ))}
      <form onSubmit={handleSubmit} style={{ margin: '0 auto', maxWidth: '400px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
        <input
          type="text"
          placeholder="Nome de Usuário"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Senha"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit" style={{ padding: '10px 20px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}>Entrar</button>
      </form>
      <br />
      <p>Ainda não tem uma conta? <a href="/register">Registre-se.</a></p>
    </div>
  );
}