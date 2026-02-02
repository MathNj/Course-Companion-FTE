# Course Companion Web App

Phase 3 of Course Companion FTE - Modern, dark-mode educational web application built with Next.js 14.

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript 5
- **Styling**: Tailwind CSS 3.4
- **Icons**: Lucide React
- **State Management**: Zustand
- **Data Fetching**: React Query (TanStack Query)
- **Markdown**: React Markdown + rehype-highlight
- **API**: Axios

## Features

### Implemented ✅

1. **Landing Page**
   - Hero section with gradient glow effect
   - Chapter grid with dark mode cards
   - Responsive design (mobile/tablet/desktop)
   - Premium content indicators

2. **Chapter Viewer** (3-Column Layout)
   - Left: Chapter navigation sidebar
   - Center: Content viewer (Markdown support)
   - Right: AI Assistant panel
   - Section-by-section navigation
   - Progress tracking

3. **Quiz Interface**
   - Question-by-question flow
   - Multiple choice, true/false, short answer
   - Immediate feedback with explanations
   - Score calculation and pass/fail
   - Review all answers

4. **Authentication**
   - Login/Register pages
   - JWT token management
   - Persistent sessions

5. **UI Components**
   - Dark mode design (zinc-950 background)
   - Emerald/mint green accents
   - Glowing effects and animations
   - Responsive breakpoints

6. **Integration**
   - Phase 1 API endpoints
   - Phase 2 premium features
   - Real-time progress tracking

### Design System

**Colors:**
- Background: `bg-[#0B0C10]` (deep dark)
- Cards: `bg-zinc-900` with `border-zinc-800`
- Primary: `text-emerald-400`, `bg-emerald-500`
- Text: `text-white`, `text-zinc-400`

**Typography:**
- Font: Inter (Google Fonts)
- Clean, sans-serif
- Multiple weights (400, 500, 600, 700)

**Components:**
- Cards with subtle borders
- Rounded corners (`rounded-xl`)
- Glowing effects (`glow-box`)
- Smooth transitions
- Hover states

## Getting Started

### Prerequisites

- Node.js 20+
- npm or yarn
- Backend API running (Phase 1 + 2)

### Installation

```bash
cd web-app

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local with your API URL

# Run development server
npm run dev
```

Visit `http://localhost:3000`

### Environment Variables

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Available Scripts

```bash
npm run dev      # Start development server
npm run build    # Build for production
npm run start    # Start production server
npm run lint     # Run ESLint
npm run type-check  # Run TypeScript check
```

## Project Structure

```
web-app/
├── src/
│   ├── app/                    # Next.js 14 App Router
│   │   ├── chapters/[id]/      # Chapter detail pages
│   │   │   ├── page.tsx        # Chapter viewer (3-column layout)
│   │   │   └── quiz/page.tsx   # Quiz interface
│   │   ├── login/              # Authentication pages
│   │   ├── register/
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Home page
│   │   ├── globals.css         # Global styles
│   │   └── providers.tsx       # React Query + Auth provider
│   ├── components/             # React components
│   │   ├── ui/                 # Reusable UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Progress.tsx
│   │   │   └── Badge.tsx
│   │   ├── Header.tsx          # Navigation header
│   │   ├── Hero.tsx            # Hero section
│   │   ├── ChapterGrid.tsx     # Chapter cards
│   │   ├── ChapterSidebar.tsx  # Left sidebar
│   │   ├── ChapterContent.tsx  # Center content
│   │   ├── AIAssistant.tsx     # Right panel
│   │   └── LoadingSpinner.tsx
│   ├── lib/                    # Utilities
│   │   ├── api.ts              # API client
│   │   └── utils.ts            # Helper functions
│   ├── store/                  # State management
│   │   └── useStore.ts         # Zustand store
│   ├── types/                  # TypeScript types
│   │   └── index.ts
│   └── hooks/                  # Custom hooks (if needed)
├── public/                     # Static assets
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.js
└── README.md
```

## API Integration

The web app integrates with backend APIs from Phase 1 and Phase 2:

### Phase 1 Endpoints (All Users)
- `GET /api/v1/chapters` - List all chapters
- `GET /api/v1/chapters/{id}` - Get chapter content
- `GET /api/v1/chapters/search` - Search content
- `GET /api/v1/quizzes/{id}` - Get quiz
- `POST /api/v1/quizzes/{id}/submit` - Submit quiz
- `GET /api/v1/progress` - Get progress
- `POST /api/v1/auth/register` - Register
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user

### Phase 2 Endpoints (Premium Users)
- `POST /api/v2/premium/assessments/grade` - Grade assessments
- `POST /api/v2/premium/learning-path/generate` - Generate adaptive path
- `GET /api/v2/premium/subscription/status` - Get subscription status

## Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

Or connect your GitHub repository to Vercel for automatic deployments.

### Environment Variables on Vercel

Set `NEXT_PUBLIC_API_URL` to your production backend URL.

### Build Configuration

The app is optimized for Vercel deployment:
- Static page generation where possible
- API route handling
- Edge runtime compatibility
- Image optimization

## Performance

### Optimization Techniques

1. **Code Splitting**
   - Automatic with Next.js App Router
   - Lazy loading for heavy components
   - Dynamic imports for large libraries

2. **Data Fetching**
   - React Query caching (60s stale time)
   - Optimistic updates
   - Prefetching on hover

3. **Rendering**
   - Server components by default
   - Client components only when needed
   - Static generation for landing page

4. **Bundle Size**
   - Tree shaking
   - Minification
   - Gzip compression (automatic)

### Target Metrics

- First Contentful Paint (FCP): <1.5s
- Largest Contentful Paint (LCP): <2.5s
- Time to Interactive (TTI): <3s
- Cumulative Layout Shift (CLS): <0.1

## Accessibility

### WCAG 2.1 Level AA Compliance

- Semantic HTML elements
- ARIA labels where needed
- Keyboard navigation support
- Focus management
- Color contrast ratios (4.5:1 minimum)
- Screen reader testing

### Keyboard Shortcuts

- `Tab`: Navigate between interactive elements
- `Enter/Space`: Activate buttons/links
- `Escape`: Close modals (when implemented)

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

Mobile browsers (iOS Safari, Chrome Mobile) supported.

## Contributing

### Development Workflow

1. Create feature branch
2. Make changes
3. Test locally
4. Run `npm run lint` and `npm run type-check`
5. Submit pull request

### Code Style

- TypeScript strict mode enabled
- ESLint for linting
- Prettier for formatting (recommended)
- Conventional commits

## Future Enhancements

### Planned Features
- [ ] Progress dashboard with charts
- [ ] Adaptive learning path visualization
- [ ] AI assessment submission form
- [ ] Dark/light mode toggle
- [ ] Offline support (service workers)
- [ ] PWA capabilities
- [ ] Push notifications
- [ ] Bookmarking notes
- [ ] Highlighting text
- [ ] Discussion forums

### Nice-to-Have
- [ ] Reading time estimation per section
- [ ] Font size controls
- [ ] Print/PDF export
- [ ] Social sharing
- [ ] Certificate generation
- [ ] Leaderboards (gamification)

## Troubleshooting

### Common Issues

**API Connection Errors**
- Verify backend is running
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Ensure CORS is configured on backend

**Build Errors**
- Clear `.next` directory: `rm -rf .next`
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Check Node.js version: `node --version` (should be 20+)

**Styling Issues**
- Verify Tailwind CSS is configured correctly
- Check `tailwind.config.ts` content paths
- Ensure `globals.css` is imported in layout

## License

MIT License - see main project LICENSE file.

---

**Built with** ❤️ **using Next.js 14 and Tailwind CSS**
