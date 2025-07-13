"use client"; // Esta diretiva é crucial para que o Next.js o trate como um Client Component

import { useEffect } from "react";

export default function BootstrapClient() {
  useEffect(() => {
    // Importa o pacote JavaScript completo do Bootstrap
    require("bootstrap/dist/js/bootstrap.bundle.min.js");
  }, []); // O array vazio garante que o efeito roda apenas uma vez no mount

  return null; // Este componente não renderiza nada no DOM
}