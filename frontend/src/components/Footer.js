import React from 'react';
import Image from 'next/image';

export default function Footer() {
  return (
    <footer className="bg-[#f8f9fa] py-4 w-full">
      <div className="w-full flex flex-col md:flex-row justify-between items-center px-4 sm:px-10">
        <div className="flex items-center gap-2">
          <Image src="/foodmart/images/logo.png" alt="Foodmart logo" width={120} height={40} />
          <p className="text-sm text-muted-foreground mt-2">© 2025 Foodmart. Todos os direitos reservados.</p>
        </div>
        <p className="text-sm text-muted-foreground mt-2 md:mt-0">
          Desenvolvido pelo <a href="#" className="underline hover:text-black">Grupo X</a>
        </p>
      </div>
    </footer>
  );
}
