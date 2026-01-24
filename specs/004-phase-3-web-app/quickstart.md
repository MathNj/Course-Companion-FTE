# Quickstart Guide: Phase 3 - Web Application Course Companion

**Date**: 2026-01-24
**Feature**: Phase 3 - Web Application Course Companion
**Purpose**: Get development environment running in under 20 minutes

## Prerequisites

- Node.js 18.x or higher (LTS recommended)
- npm 9.x or higher (or pnpm 8.x, yarn 3.x)
- Git
- Code editor (VS Code recommended)
- Backend APIs running (Phase 1 + Phase 2) at `http://localhost:8000`

## Quick Start (6 Steps)

### 1. Clone Repository and Navigate to Frontend

```bash
git checkout 004-phase-3-web-app
cd Course-Companion-FTE/frontend
```

If `frontend/` directory doesn't exist yet (first time setup):
```bash
mkdir frontend
cd frontend
```

---

### 2. Initialize Next.js 14 Project

```bash
# Using create-next-app with TypeScript, TailwindCSS, and App Router
npx create-next-app@latest . --typescript --tailwind --app --src-dir --import-alias "@/*"

# Answer prompts:
# - TypeScript: Yes
# - ESLint: Yes
# - Tailwind CSS: Yes
# - src/ directory: No (use app/ directly)
# - App Router: Yes
# - Import alias: @/* (default)
```

Or if already initialized, install dependencies:
```bash
npm install
```

---

### 3. Install Additional Dependencies

```bash
# State management
npm install @tanstack/react-query@5 @tanstack/react-query-devtools@5
npm install @tanstack/react-query-persist-client@5 @tanstack/query-sync-storage-persister@5
npm install zustand@4

# Authentication
npm install next-auth@4

# Forms and validation
npm install react-hook-form@7 zod@3

# UI components (shadcn/ui will be initialized separately)
npm install clsx tailwind-merge
npm install class-variance-authority
npm install lucide-react  # Icon library

# Utilities
npm install date-fns  # Date formatting
npm install react-markdown remark-gfm rehype-highlight  # Markdown rendering
npm install axios  # HTTP client

# Development dependencies
npm install -D @types/node @types/react @types/react-dom
npm install -D eslint-plugin-jsx-a11y  # Accessibility linting
npm install -D prettier prettier-plugin-tailwindcss  # Code formatting
npm install -D vitest @vitejs/plugin-react @testing-library/react @testing-library/jest-dom
npm install -D @playwright/test  # E2E testing
npm install -D @axe-core/playwright  # Accessibility testing
```

---

### 4. Initialize shadcn/ui

```bash
# Initialize shadcn/ui (copy components into codebase)
npx shadcn-ui@latest init

# Answer prompts:
# - Style: Default
# - Base color: Slate
# - CSS variables: Yes
# - Tailwind config: Yes

# Install commonly used components
npx shadcn-ui@latest add button card dialog input textarea label skeleton progress badge toast radio-group checkbox select
```

---

### 5. Configure Environment Variables

Create `.env.local` in `frontend/` directory:

```bash
# Create .env.local from example
cp .env.example .env.local
```

Edit `.env.local` with your settings:

```env
# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000
# Production: NEXT_PUBLIC_API_URL=https://api.course-companion.example.com

# NextAuth.js
NEXTAUTH_URL=http://localhost:3000
# Production: NEXTAUTH_URL=https://app.course-companion.example.com
NEXTAUTH_SECRET=your-super-secret-key-change-in-production-min-32-chars

# Feature Flags (Optional - enable Phase 2 features)
NEXT_PUBLIC_ENABLE_ADAPTIVE_PATHS=true
NEXT_PUBLIC_ENABLE_ASSESSMENTS=true

# Analytics (Optional)
NEXT_PUBLIC_VERCEL_ANALYTICS=false  # Set to true in production

# Environment
NODE_ENV=development
```

Create `.env.example` for version control:

```env
# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000

# NextAuth.js
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=generate-a-random-secret-key-here

# Feature Flags
NEXT_PUBLIC_ENABLE_ADAPTIVE_PATHS=true
NEXT_PUBLIC_ENABLE_ASSESSMENTS=true

# Analytics
NEXT_PUBLIC_VERCEL_ANALYTICS=false

# Environment
NODE_ENV=development
```

---

### 6. Run Development Server

```bash
npm run dev
```

Frontend now running at: http://localhost:3000
- Homepage: http://localhost:3000
- Dashboard: http://localhost:3000/dashboard (requires auth)
- Login: http://localhost:3000/login

**Expected Initial State**:
- Homepage shows landing page (redirects to /dashboard if authenticated)
- /login shows login form
- API calls to `http://localhost:8000/api/v1/*` (backend must be running)

---

## Detailed Setup

### Project Structure Setup

Create the following directory structure:

```bash
cd frontend

# Create directories
mkdir -p app/\(auth\)/login
mkdir -p app/\(auth\)/register
mkdir -p app/\(app\)/dashboard
mkdir -p app/\(app\)/chapters/\[id\]
mkdir -p app/\(app\)/quizzes/\[id\]
mkdir -p app/\(app\)/progress
mkdir -p app/\(app\)/settings
mkdir -p app/api/auth/\[...nextauth\]

mkdir -p components/layouts
mkdir -p components/features/dashboard
mkdir -p components/features/chapters
mkdir -p components/features/quizzes
mkdir -p components/features/progress
mkdir -p components/features/adaptive
mkdir -p components/features/assessments
mkdir -p components/features/upgrade

mkdir -p lib/api
mkdir -p lib/hooks
mkdir -p lib/stores
mkdir -p lib/utils
mkdir -p lib/schemas
mkdir -p lib/types

mkdir -p tests/components
mkdir -p tests/e2e
mkdir -p tests/a11y

mkdir -p public/images/illustrations
mkdir -p public/images/badges
```

---

### TailwindCSS Configuration

Update `tailwind.config.ts`:

```typescript
import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: ['class'],
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Custom theme colors (adjust to match brand)
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
        },
        // shadcn/ui defaults (keep these)
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      spacing: {
        // 8px grid system
        '1': '0.5rem',  // 8px
        '2': '1rem',    // 16px
        '3': '1.5rem',  // 24px
        '4': '2rem',    // 32px
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
};

export default config;
```

---

### TypeScript Configuration

Update `tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

---

### Next.js Configuration

Update `next.config.js`:

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // Image optimization
  images: {
    domains: ['localhost', 'api.course-companion.example.com'],
    formats: ['image/webp', 'image/avif'],
  },

  // Environment variables validation
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },

  // Performance optimizations
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },

  // Experimental features
  experimental: {
    // Enable React Server Components
    serverActions: true,
  },

  // Webpack configuration (for bundle analysis)
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
      };
    }
    return config;
  },
};

module.exports = nextConfig;
```

---

### ESLint Configuration

Update `.eslintrc.json`:

```json
{
  "extends": [
    "next/core-web-vitals",
    "plugin:jsx-a11y/recommended"
  ],
  "plugins": ["jsx-a11y"],
  "rules": {
    "jsx-a11y/anchor-is-valid": "error",
    "jsx-a11y/aria-props": "error",
    "jsx-a11y/aria-proptypes": "error",
    "jsx-a11y/aria-unsupported-elements": "error",
    "jsx-a11y/role-has-required-aria-props": "error",
    "@next/next/no-html-link-for-pages": "off"
  }
}
```

---

### Prettier Configuration

Create `.prettierrc`:

```json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100,
  "plugins": ["prettier-plugin-tailwindcss"]
}
```

---

### NextAuth.js Setup

Create `app/api/auth/[...nextauth]/route.ts`:

```typescript
import NextAuth, { NextAuthOptions } from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';

const authOptions: NextAuthOptions = {
  providers: [
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null;
        }

        // Call backend /auth/login API
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: credentials.email,
            password: credentials.password,
          }),
        });

        if (!res.ok) {
          return null;
        }

        const data = await res.json();

        // Return user + token
        return {
          id: data.user.user_id,
          email: data.user.email,
          name: data.user.full_name,
          subscription_tier: data.user.subscription_tier,
          access_token: data.access_token,
        };
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.access_token = user.access_token;
        token.subscription_tier = user.subscription_tier;
      }
      return token;
    },
    async session({ session, token }) {
      session.user.id = token.sub;
      session.user.access_token = token.access_token;
      session.user.subscription_tier = token.subscription_tier;
      return session;
    },
  },
  pages: {
    signIn: '/login',
  },
  secret: process.env.NEXTAUTH_SECRET,
};

const handler = NextAuth(authOptions);
export { handler as GET, handler as POST };
```

---

### React Query Setup

Create `app/providers.tsx`:

```typescript
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { SessionProvider } from 'next-auth/react';
import { useState } from 'react';

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 5 * 60 * 1000, // 5 minutes
            cacheTime: 24 * 60 * 60 * 1000, // 24 hours
            retry: 2,
            refetchOnWindowFocus: true,
          },
        },
      })
  );

  return (
    <SessionProvider>
      <QueryClientProvider client={queryClient}>
        {children}
        <ReactQueryDevtools initialIsOpen={false} />
      </QueryClientProvider>
    </SessionProvider>
  );
}
```

Update `app/layout.tsx`:

```typescript
import { Providers } from './providers';
import './globals.css';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
```

---

### API Client Setup

Create `lib/api/client.ts`:

```typescript
import axios from 'axios';
import { getSession } from 'next-auth/react';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to all requests
apiClient.interceptors.request.use(async (config) => {
  const session = await getSession();
  if (session?.user?.access_token) {
    config.headers.Authorization = `Bearer ${session.user.access_token}`;
  }
  return config;
});

// Handle errors globally
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login on 401 Unauthorized
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

---

### Testing Setup

#### Vitest Configuration

Create `vitest.config.ts`:

```typescript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./tests/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: ['node_modules/', 'tests/', '.next/'],
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './'),
    },
  },
});
```

Create `tests/setup.ts`:

```typescript
import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';

afterEach(() => {
  cleanup();
});
```

#### Playwright Configuration

Create `playwright.config.ts`:

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

---

### Example Component: Login Page

Create `app/(auth)/login/page.tsx`:

```typescript
'use client';

import { signIn } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const result = await signIn('credentials', {
      email,
      password,
      redirect: false,
    });

    setLoading(false);

    if (result?.error) {
      setError('Invalid email or password');
    } else {
      router.push('/dashboard');
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="w-full max-w-md space-y-6 rounded-lg border p-8">
        <h1 className="text-2xl font-bold">Login</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div>
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          {error && <p className="text-sm text-red-500">{error}</p>}
          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? 'Logging in...' : 'Login'}
          </Button>
        </form>
      </div>
    </div>
  );
}
```

---

### Running Tests

```bash
# Unit tests (Vitest)
npm run test

# E2E tests (Playwright)
npx playwright install  # First time only
npm run test:e2e

# Accessibility tests (axe-core)
npm run test:a11y

# Coverage
npm run test:coverage
```

Update `package.json` scripts:

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "test": "vitest",
    "test:e2e": "playwright test",
    "test:a11y": "playwright test tests/a11y",
    "test:coverage": "vitest --coverage",
    "format": "prettier --write ."
  }
}
```

---

## Vercel Deployment

### 1. Connect GitHub Repository

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New Project"
3. Import your GitHub repository
4. Select `frontend/` as root directory
5. Framework preset: Next.js (auto-detected)

### 2. Configure Environment Variables

Add the following in Vercel project settings:

```
NEXT_PUBLIC_API_URL=https://api.course-companion.example.com
NEXTAUTH_URL=https://app.course-companion.example.com
NEXTAUTH_SECRET=<generate-random-secret>
NEXT_PUBLIC_ENABLE_ADAPTIVE_PATHS=true
NEXT_PUBLIC_ENABLE_ASSESSMENTS=true
NEXT_PUBLIC_VERCEL_ANALYTICS=true
NODE_ENV=production
```

### 3. Deploy

```bash
# Vercel will auto-deploy on push to main branch
git push origin main

# Or deploy manually
npx vercel --prod
```

### 4. Custom Domain (Optional)

1. Go to Vercel project settings → Domains
2. Add custom domain: `app.course-companion.example.com`
3. Follow DNS configuration instructions (add CNAME record)

---

## Troubleshooting

### Issue: "Module not found: Can't resolve '@/components/...'"

**Solution**: Ensure `tsconfig.json` has correct path alias:
```json
"paths": {
  "@/*": ["./*"]
}
```

---

### Issue: "Authentication error: Unable to get CSRF token"

**Solution**: Ensure `NEXTAUTH_URL` and `NEXTAUTH_SECRET` are set in `.env.local`:
```env
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key-min-32-chars
```

---

### Issue: "API calls fail with CORS error"

**Solution**: Backend must allow frontend origin in CORS configuration:
```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://app.course-companion.example.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### Issue: "Hydration mismatch error in Next.js"

**Solution**: Avoid using `window` or `localStorage` during server-side rendering:
```typescript
// Wrong
const theme = localStorage.getItem('theme');

// Correct
const [theme, setTheme] = useState('light');
useEffect(() => {
  setTheme(localStorage.getItem('theme') || 'light');
}, []);
```

---

### Issue: "Lighthouse performance score below 90"

**Solution**:
1. Enable Next.js Image optimization: `<Image>` instead of `<img>`
2. Code split large components: `next/dynamic` with `{ ssr: false }`
3. Reduce bundle size: Check bundle analyzer
4. Enable Vercel Analytics to monitor real-world performance

```bash
# Analyze bundle
npm run build
npx @next/bundle-analyzer
```

---

### Issue: "Playwright tests timeout"

**Solution**:
1. Ensure dev server is running: `npm run dev`
2. Increase timeout in `playwright.config.ts`:
```typescript
use: {
  actionTimeout: 10000,  // 10 seconds
}
```

---

## Next Steps

After quickstart setup:

1. **Implement Core Components**:
   - Create `components/layouts/Header.tsx`
   - Create `components/features/dashboard/ProgressSummary.tsx`
   - Create `app/(app)/dashboard/page.tsx`

2. **Set Up API Hooks**:
   - Create `lib/hooks/useChapters.ts`
   - Create `lib/hooks/useProgress.ts`
   - Create `lib/api/chapters.ts`

3. **Add First E2E Test**:
   - Create `tests/e2e/auth.spec.ts`
   - Test login flow end-to-end

4. **Configure CI/CD**:
   - Create `.github/workflows/ci.yml`
   - Run tests on every PR

5. **Review Tasks**:
   - See `tasks.md` (generated by `/sp.tasks` command)
   - Start with Phase 0: Foundation tasks

---

**Quickstart Complete. Development environment ready. See `tasks.md` for implementation roadmap.**
