# NWPU AskMe - Vercel

西北工业大学问答平台 Vercel 部署版本

## Overview

NWPU AskMe is a Q&A platform designed for Northwestern Polytechnical University (西北工业大学) students and faculty members. This is the Vercel-optimized version built with Next.js.

## Features

- 💬 Question and Answer forum
- 📚 Knowledge sharing platform
- 🤝 Academic discussion community
- 🚀 Optimized for Vercel deployment

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Deployment**: Vercel

## Getting Started

### Prerequisites

- Node.js 18.x or higher
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

Open [http://localhost:3000](http://localhost:3000) to view the application.

## Deployment

This project is optimized for deployment on Vercel:

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/deltaR-3k/nwpu-askme-vercel)

### Manual Deployment

1. Install Vercel CLI: `npm i -g vercel`
2. Run: `vercel`
3. Follow the prompts

## Project Structure

```
nwpu-askme-vercel/
├── app/                # Next.js App Router pages
│   ├── layout.tsx     # Root layout
│   ├── page.tsx       # Home page
│   └── globals.css    # Global styles
├── public/            # Static assets
├── package.json       # Dependencies
├── tsconfig.json      # TypeScript config
├── tailwind.config.js # Tailwind CSS config
├── next.config.js     # Next.js config
└── vercel.json        # Vercel config
```

## Development

```bash
# Lint code
npm run lint

# Type check
npx tsc --noEmit
```

## License

MIT

## Contact

For questions or suggestions, please open an issue on GitHub.
