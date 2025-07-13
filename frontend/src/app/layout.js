import { Geist, Geist_Mono } from "next/font/google";
import '../styles/style.css'; // Seu CSS customizado
import 'bootstrap/dist/css/bootstrap.min.css'; // <--- IMPORTAÇÃO DO CSS DO BOOTSTRAP AQUI
import Header from '../components/Header';
import Footer from '../components/Footer';
import BootstrapClient from '../components/BootstrapClient'; // <--- IMPORTAR O NOVO COMPONENTE

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata = {
  title: "MEU PROJETO - FOODMART?", // escolher titulo
  description: "DEscricao generica - Seu mercado online de produtos frescos!",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
        style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }} 
      >
        <Header />
        
        <main style={{ flexGrow: 1 }}> {}
          {children} {/* page.js, login/page.js, etc. */}
        </main>
        
        <Footer />
        <BootstrapClient /> {/* <--- ADICIONE ESTE COMPONENTE AQUI, GERALMENTE ANTES DO FECHAMENTO DO </body> */}
      </body>
    </html>
  );
}