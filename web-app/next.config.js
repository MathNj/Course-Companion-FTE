/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // output: 'standalone', // Commented out for local development
  eslint: {
    // Disable ESLint during production builds
    ignoreDuringBuilds: true,
  },
  typescript: {
    // Disable type checking during production builds for faster deployment
    ignoreBuildErrors: true,
  },
  images: {
    domains: ['localhost', '*.fly.dev'],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**.fly.dev',
      },
    ],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  // Add experimental configuration to help with Jest worker issues
  experimental: {
    // Optimize package imports
    optimizePackageImports: ['lucide-react', '@tanstack/react-query'],
  },
}

module.exports = nextConfig
