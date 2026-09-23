import path from "node:path";
import { fileURLToPath } from "node:url";
import { PHASE_DEVELOPMENT_SERVER } from "next/constants.js";

/** @type {import('next').NextConfig} */
const projectRoot = path.dirname(fileURLToPath(import.meta.url));

export default function nextConfig(phase) {
  return {
    reactStrictMode: true,
    outputFileTracingRoot: projectRoot,
    // Keep `next build` from invalidating assets served by a running dev server.
    distDir: phase === PHASE_DEVELOPMENT_SERVER ? ".next-dev" : ".next",
  };
}
