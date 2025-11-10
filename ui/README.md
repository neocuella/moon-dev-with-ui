# Moon Dev Flow UI - Frontend

React + xyflow visual flow builder for orchestrating AI trading agents.

## Setup

```bash
npm install
npm run dev
```

Frontend will be available at `http://localhost:5173`

## Project Structure

```
ui/
├── src/
│   ├── components/       # React components
│   ├── hooks/           # Custom React hooks
│   ├── store/           # Zustand stores
│   ├── api/             # API client
│   ├── types/           # TypeScript types
│   ├── utils/           # Utility functions
│   ├── App.tsx          # Root component
│   ├── main.tsx         # Entry point
│   └── index.css        # Global styles
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── README.md
```

## Development

See `.amp/WEEK_1_DAILY_TASKS.md` for detailed daily tasks.

## Building for Production

```bash
npm run build
npm run preview
```
