# Web Dashboard

React + TypeScript admin dashboard for the Digital Art Platform.

## Features

- **React 18**: Latest React with concurrent features
- **TypeScript**: Type-safe development
- **Vite**: Lightning-fast build tool
- **Tailwind CSS**: Utility-first CSS framework
- **shadcn/ui**: High-quality UI components
- **React Query**: Powerful data synchronization
- **React Router**: Client-side routing
- **Zustand**: Lightweight state management
- **Zod**: Schema validation
- **Dark Mode**: Full dark mode support

## Prerequisites

- Node.js 18 or higher
- npm or yarn

## Quick Start

### 1. Install Dependencies

```bash
npm install
# or
yarn install
```

### 2. Set Up Environment Variables

```bash
cp .env.example .env.local
# Edit .env.local with your configuration
```

### 3. Start Development Server

```bash
npm run dev
# or
yarn dev
```

### 4. Access the Application

Open your browser and navigate to http://localhost:5173

## Available Scripts

```bash
# Development
npm run dev          # Start dev server
npm run dev:host     # Start dev server (network accessible)

# Building
npm run build        # Build for production
npm run preview      # Preview production build

# Code Quality
npm run lint         # Run ESLint
npm run lint:fix     # Fix ESLint errors
npm run format       # Format code with Prettier
npm run type-check   # Run TypeScript type checking

# Testing
npm run test         # Run tests
npm run test:watch   # Run tests in watch mode
npm run test:coverage # Run tests with coverage
```

## Project Structure

```
web-dashboard/
├── public/              # Static assets
├── src/
│   ├── main.tsx         # Application entry point
│   ├── App.tsx          # Root component
│   │
│   ├── components/      # React components
│   │   ├── ui/          # UI components (shadcn/ui)
│   │   ├── layout/      # Layout components
│   │   ├── artwork/     # Artwork-related components
│   │   ├── collection/  # Collection components
│   │   └── common/      # Shared components
│   │
│   ├── pages/           # Page components
│   │   ├── Dashboard.tsx
│   │   ├── Artworks.tsx
│   │   ├── Collections.tsx
│   │   ├── Devices.tsx
│   │   ├── Settings.tsx
│   │   └── auth/
│   │       ├── Login.tsx
│   │       └── Register.tsx
│   │
│   ├── hooks/           # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useArtworks.ts
│   │   └── useInfiniteScroll.ts
│   │
│   ├── lib/             # Utilities and helpers
│   │   ├── api.ts       # API client
│   │   ├── auth.ts      # Authentication utilities
│   │   └── utils.ts     # General utilities
│   │
│   ├── types/           # TypeScript type definitions
│   │   ├── artwork.ts
│   │   ├── user.ts
│   │   └── api.ts
│   │
│   ├── store/           # State management (Zustand)
│   │   ├── authStore.ts
│   │   └── uiStore.ts
│   │
│   ├── styles/          # Global styles
│   │   └── globals.css
│   │
│   └── config/          # Configuration
│       └── constants.ts
│
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
├── .env.example
└── README.md
```

## Key Features

### Authentication

The app uses JWT-based authentication with automatic token refresh:

```typescript
// Login
const { data } = await api.post('/auth/login', {
  email: 'user@example.com',
  password: 'password'
});

// Access token stored in memory
// Refresh token stored in httpOnly cookie
```

### API Integration

API client with automatic authentication and error handling:

```typescript
import { api } from '@/lib/api';

// GET request
const artworks = await api.get('/artworks');

// POST request
const newArtwork = await api.post('/artworks', formData);

// Automatic token refresh on 401
// Automatic retry on network errors
```

### Data Fetching with React Query

```typescript
import { useQuery, useMutation } from '@tanstack/react-query';

// Fetch artworks
const { data, isLoading, error } = useQuery({
  queryKey: ['artworks', filters],
  queryFn: () => fetchArtworks(filters),
});

// Upload artwork
const uploadMutation = useMutation({
  mutationFn: uploadArtwork,
  onSuccess: () => {
    queryClient.invalidateQueries(['artworks']);
  },
});
```

### Responsive Design

Built mobile-first with Tailwind CSS:

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {artworks.map(artwork => (
    <ArtworkCard key={artwork.id} artwork={artwork} />
  ))}
</div>
```

### Dark Mode

Automatic dark mode support:

```tsx
import { useTheme } from '@/hooks/useTheme';

function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  
  return (
    <button onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}>
      {theme === 'dark' ? '☀️' : '🌙'}
    </button>
  );
}
```

## Configuration

### Environment Variables

```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws

# Feature Flags
VITE_ENABLE_AI_FEATURES=true
VITE_ENABLE_ANALYTICS=false

# External Services
VITE_SENTRY_DSN=your-sentry-dsn
VITE_GOOGLE_ANALYTICS_ID=your-ga-id
```

### Path Aliases

TypeScript path aliases are configured for clean imports:

```typescript
// Instead of: import { Button } from '../../../components/ui/button'
import { Button } from '@/components/ui/button';
import { useAuth } from '@/hooks/useAuth';
import { api } from '@/lib/api';
```

## Styling

### Tailwind CSS

Utility-first CSS framework with custom configuration:

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          500: '#3b82f6',
          900: '#1e3a8a',
        },
      },
    },
  },
};
```

### Component Library

Using shadcn/ui for consistent, accessible components:

```bash
# Add new component
npx shadcn-ui@latest add button
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add dropdown-menu
```

## Building for Production

```bash
# Build
npm run build

# Preview build locally
npm run preview

# Build output in dist/
```

### Deployment

#### Static Hosting (Netlify, Vercel, Cloudflare Pages)

```bash
# Build command
npm run build

# Output directory
dist

# Environment variables
# Set in hosting platform dashboard
```

#### Docker

```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Performance Optimization

### Code Splitting

Automatic route-based code splitting:

```typescript
import { lazy, Suspense } from 'react';

const Artworks = lazy(() => import('@/pages/Artworks'));

<Suspense fallback={<LoadingSpinner />}>
  <Artworks />
</Suspense>
```

### Image Optimization

Lazy loading images with blur placeholders:

```tsx
<img
  src={artwork.thumbnailUrl}
  loading="lazy"
  className="aspect-video object-cover"
  alt={artwork.title}
/>
```

### Bundle Analysis

```bash
# Analyze bundle size
npm run build -- --analyze

# View bundle visualization
npm run preview
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Accessibility

- WCAG 2.1 Level AA compliance
- Keyboard navigation support
- Screen reader friendly
- High contrast mode support
- Focus visible indicators

## Testing

```bash
# Run tests
npm run test

# Watch mode
npm run test:watch

# Coverage
npm run test:coverage
```

Example test:

```typescript
import { render, screen } from '@testing-library/react';
import { ArtworkCard } from './ArtworkCard';

test('renders artwork card', () => {
  const artwork = {
    id: 1,
    title: 'Starry Night',
    artist: { name: 'Vincent van Gogh' },
    thumbnailUrl: '/image.jpg',
  };
  
  render(<ArtworkCard artwork={artwork} />);
  expect(screen.getByText('Starry Night')).toBeInTheDocument();
});
```

## Contributing

See [Coding Standards](../documentation/CODING_STANDARDS.md) for code style guidelines.

## License

MIT License - see [LICENSE](../LICENSE) file for details.
