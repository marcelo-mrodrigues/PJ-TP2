/** @type {import('next').NextConfig} */
const nextConfig = {
    async rewrites() {
      return [
        {
          source: '/api/django/:path*',
          destination: 'http://localhost:8000/:path*',
        },
      ];
    },
  };
  
  export default nextConfig;