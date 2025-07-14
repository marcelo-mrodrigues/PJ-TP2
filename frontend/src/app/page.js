// frontend/src/app/page.js
'use client'; // ESSENCIAL para componentes interativos como o Swiper

import Image from "next/image";

// 1. Importar os componentes Swiper e SwiperSlide
import { Swiper, SwiperSlide } from 'swiper/react';

// 2. Importar os módulos necessários (ex: Pagination)
import { Pagination } from 'swiper/modules';

// 3. Importar o CSS do Swiper
import 'swiper/css';
import 'swiper/css/pagination'; // Se você usar paginação
import { useEffect } from "react";

async function get_user_details() {
  
}

export default function Home() {
  useEffect(() => {
    const fetchUserDetails = async() => {
      const response = await fetch("http://localhost:8000/api/v1/me", {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
        }
      })
      const data = await response.json()
      console.log(data)
    }

    fetchUserDetails();
  }, []) 
  return (
    <section>
      <div className="grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]">
        <main className="flex flex-col gap-[32px] row-start-2 items-center sm:items-start">
          <section
            className="py-3"
            style={{
              backgroundImage: "url('/foodmart/images/background-pattern.jpg')",
              backgroundRepeat: "no-repeat",
              backgroundSize: "cover",
            }}
          >
            <div className="container-fluid">
              <div className="row">
                <div className="col-md-12">
                  <div className="banner-blocks">

                    <div className="banner-ad large bg-info block-1">
                      {/*
                        SUBSTITUIÇÃO DA ESTRUTURA HTML DO SWIPER POR COMPONENTES SWIPER:
                      */}
                      <Swiper
                        // Ativar os módulos necessários
                        modules={[Pagination]}
                        // Configurar paginação
                        pagination={{ clickable: true }}
                        // Adicionar classes CSS para estilização
                        className="main-swiper"
                        // Outras props do Swiper, como:
                        // spaceBetween={30}
                        // slidesPerView={1}
                        // navigation={true} // Se quiser botões de navegação
                      >
                        <SwiperSlide>
                          <div className="row banner-content p-5">
                            <div className="content-wrapper col-md-7">
                              <div className="categories my-3">100% natural</div>
                              <h3 className="display-4">Fresh Smoothie & Summer Juice</h3>
                              <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Dignissim massa diam elementum.</p>
                              <a href="#" className="btn btn-outline-dark btn-lg text-uppercase fs-6 rounded-1 px-4 py-3 mt-3">Shop Now</a>
                            </div>
                            <div className="img-wrapper col-md-5">
                              <Image src="/foodmart/images/product-thumb-1.png" alt="Product 1" width={500} height={500} className="img-fluid" />
                            </div>
                          </div>
                        </SwiperSlide>
                        
                        <SwiperSlide>
                          <div className="row banner-content p-5">
                            <div className="content-wrapper col-md-7">
                              <div className="categories mb-3 pb-3">100% natural</div>
                              <h3 className="banner-title">Fresh Smoothie & Summer Juice</h3>
                              <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Dignissim massa diam elementum.</p>
                              <a href="#" className="btn btn-outline-dark btn-lg text-uppercase fs-6 rounded-1">Shop Collection</a>
                            </div>
                            <div className="img-wrapper col-md-5">
                              <Image src="/foodmart/images/product-thumb-1.png" alt="Product 1" width={500} height={500} className="img-fluid" />
                            </div>
                          </div>
                        </SwiperSlide>
                        
                        <SwiperSlide>
                          <div className="row banner-content p-5">
                            <div className="content-wrapper col-md-7">
                              <div className="categories mb-3 pb-3">100% natural</div>
                              <h3 className="banner-title">Heinz Tomato Ketchup</h3>
                              <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Dignissim massa diam elementum.</p>
                              <a href="#" className="btn btn-outline-dark btn-lg text-uppercase fs-6 rounded-1">Shop Collection</a>
                            </div>
                            <div className="img-wrapper col-md-5">
                              <Image src="/foodmart/images/product-thumb-2.png" alt="Product 2" width={500} height={500} className="img-fluid" />
                            </div>
                          </div>
                        </SwiperSlide>
                      </Swiper>
                      
                      {/* O swiper-pagination é gerado automaticamente pelo componente Swiper com 'pagination={{ clickable: true }}' */}
                      
                    </div> {/* Fechamento da div .banner-ad.large.bg-info.block-1 */}
                  
                    <div className="banner-ad bg-success-subtle block-2" style={{ background: "url('/foodmart/images/ad-image-1.png') no-repeat", backgroundPosition: "right bottom" }}>
                      <div className="row banner-content p-5">
                        <div className="content-wrapper col-md-7">
                          <div className="categories sale mb-3 pb-3">20% off</div>
                          <h3 className="banner-title">Fruits & Vegetables</h3>
                          {/* Note que <use xlink:href="#arrow-right"></use> é para SVG sprites.
                              Você precisará de um componente SVG ou de um SVG inline aqui. */}
                          <a href="#" className="d-flex align-items-center nav-link">Shop Collection <svg width="24" height="24"><use xlinkHref="#arrow-right"></use></svg></a>
                        </div>
                      </div>
                    </div>

                    <div className="banner-ad bg-danger block-3" style={{ background: "url('/foodmart/images/ad-image-2.png') no-repeat", backgroundPosition: "right bottom" }}>
                      <div className="row banner-content p-5">
                        <div className="content-wrapper col-md-7">
                          <div className="categories sale mb-3 pb-3">15% off</div>
                          <h3 className="item-title">Baked Products</h3>
                          <a href="#" className="d-flex align-items-center nav-link">Shop Collection <svg width="24" height="24"><use xlinkHref="#arrow-right"></use></svg></a>
                        </div>
                      </div>
                    </div>

                  </div> {/* / Banner Blocks */}
                </div>
              </div>
            </div>
          </section>

        </main>
        {/* Adicionar o footer */}
        <footer className="row-start-3 flex gap-[24px] flex-wrap items-center justify-center">
          <a
            className="flex items-center gap-2 hover:underline hover:underline-offset-4"
            href="https://nextjs.org/learn?utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
            target="_blank"
            rel="noopener noreferrer"
          >
            <Image
              aria-hidden
              src="/file.svg"
              alt="File icon"
              width={16}
              height={16}
            />
            Learn
          </a>
          <a
            className="flex items-center gap-2 hover:underline hover:underline-offset-4"
            href="https://vercel.com/templates?framework=next.js&utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
            target="_blank"
            rel="noopener noreferrer"
          >
            <Image
              aria-hidden
              src="/window.svg"
              alt="Window icon"
              width={16}
              height={16}
            />
            Examples
          </a>
          <a
            className="flex items-center gap-2 hover:underline hover:underline-offset-4"
            href="https://nextjs.org?utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
            target="_blank"
            rel="noopener noreferrer"
          >
            <Image
              aria-hidden
              src="/globe.svg"
              alt="Globe icon"
              width={16}
              height={16}
            />
            Go to nextjs.org →
          </a>
        </footer>
      </div>
    </section>
  );
}