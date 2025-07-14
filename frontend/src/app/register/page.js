"use client"; // Marca como Client Component para interatividade

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation'; // Para redirecionamento no Next.js
import { useSearchParams } from 'next/navigation'; // Para ler mensagens de erro da URL

export default function RegisterPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [errors, setErrors] = useState([]);
  const [successMessage, setSuccessMessage] = useState('');

  // Efeito para ler mensagens do Django após redirecionamento
  useEffect(() => {
    // Django messages são geralmente passados como parâmetros de query ou via cookies temporários.
    // Para simplificar, vamos assumir que você terá que adaptar isso se for via cookies ou URL params.
    // Exemplo básico:
    const djangoMessages = searchParams.get('messages'); // Isso é um exemplo, o Django não faz isso por padrão.
    if (djangoMessages) {
      // Você precisaria de uma forma de parsear as mensagens do Django aqui.
      // Poderia ser um JSON codificado em base64, ou um sistema de cookies.
      // Por enquanto, apenas para demonstração:
      if (djangoMessages.includes('registrado com sucesso')) {
        setSuccessMessage(djangoMessages);
      } else {
        setErrors([djangoMessages]); // Adaptar para mostrar múltiplos erros
      }
    }
  }, [searchParams]);


  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors([]); // Limpa erros anteriores
    setSuccessMessage('');

    // Construir FormData para enviar como um formulário POST tradicional (multipart/form-data)
    // Isso é importante para que o Django AuthenticationForm possa lê-lo.
    const formData = new FormData();
    formData.append('username', username);
    formData.append('email', email);
    formData.append('password1', password);
    formData.append('password2', confirmPassword); // Django UserCreationForm usa password2
    formData.append('first_name', firstName);
    formData.append('last_name', lastName);

    // Você precisará obter o CSRF token do Django.
    // A forma mais comum é ter um endpoint Django que retorna o token,
    // ou lê-lo de um cookie definido pelo Django na primeira requisição.
    // Para simplificar aqui, vamos assumir que o Django vai validar sem ele por enquanto
    // ou que você o adicionará de alguma forma (ex: via um API endpoint).
    // Para produção, o CSRF é OBRIGATÓRIO.
    // Exemplo: fetch('/get-csrf-token/').then(res => res.json()).then(data => data.csrfToken);
    // Mas para este exemplo, vamos pular a obtenção do token na requisição inicial Next.js.
    // Quando o Django redireciona, ele geralmente lida com isso.


    try {
      const response = await fetch('http://localhost:8000/api/v1/register', { // Use a URL completa do seu backend Django
        method: 'POST',
        body: formData, // Envia FormData diretamente
        // headers: {
        //   'X-CSRFToken': 'YOUR_CSRF_TOKEN_HERE' // Preencher com o token real
        // },
        redirect: 'follow', // Importante para que o fetch siga o redirecionamento do Django
      });

      // Se o Django redireciona, o fetch por padrão já segue.
      // O desafio é ler as mensagens do Django após o redirecionamento.
      // O Django geralmente usa o messages framework que é lido APÓS o redirect.
      // Uma forma seria o Django redirecionar para um URL do Next.js com query params:
      // Ex: http://localhost:3000/login?message=Usuário%20registrado%20com%20sucesso!

      // Se a resposta não for um redirect, e sim um 200 (com erros, por exemplo)
      // Ou se o Django retornar um JSON de erros (melhor para APIs)
      if (response.ok || response.status === 200) {
        // Se a resposta for 200, significa que o Django re-renderizou a página com erros.
        // O Next.js não tem acesso direto a esse HTML.
        // É por isso que o Django DEVE redirecionar de volta para o Next.js,
        // ou você deve usar uma API RESTful (retornando JSON).

        // Como as views Django redirecionam com mensagens, o ideal é o seguinte:
        // Se o sucesso, o Django já redireciona para login.
        // Se o erro, o Django já redireciona para register com a mensagem.
        // O `fetch` com `redirect: 'follow'` vai apenas te levar para a URL final.
        // Você precisaria de um listener para mensagens que venham via query params ou cookies.
        
        // Esta parte do código abaixo pode não ser executada se o Django redirecionar.
        // Ela seria mais para um cenário de API REST que retorna JSON.
        // const data = await response.json(); // Se o Django retornasse JSON
        // if (response.status === 400 && data.errors) {
        //   setErrors(data.errors);
        // }
        router.push('/login?registered=true')
      } else {
        // Lida com outros status de erro da rede/servidor
        setErrors(['Ocorreu um erro no servidor. Tente novamente.']);
      }

    } catch (error) {
      console.error('Erro ao enviar formulário:', error);
      setErrors(['Erro de conexão. Verifique sua rede.']);
    }
  };

  return (
    <div style={{ fontFamily: 'sans-serif', textAlign: 'center', marginTop: '50px' }}>
      <h2>Registro</h2>
      {successMessage && <p style={{ color: 'green' }}>{successMessage}</p>}
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
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="text"
          placeholder="Primeiro Nome"
          value={firstName}
          onChange={(e) => setFirstName(e.target.value)}
          required
        />
        <input
          type="text"
          placeholder="Último Nome"
          value={lastName}
          onChange={(e) => setLastName(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Senha"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Confirmar Senha"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required
        />
        <button type="submit" style={{ padding: '10px 20px', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}>Registrar</button>
      </form>
      <br />
      <p>Já tem uma conta? <a href="/login">Faça login.</a></p>
    </div>
  );
}