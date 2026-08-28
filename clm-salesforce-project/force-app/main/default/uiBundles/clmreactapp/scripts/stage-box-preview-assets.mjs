/**
 * Stage Box Content Preview's runtime assets into public/ so they are served from our own
 * origin.
 *
 * The Preview class itself is imported and bundled, but it fetches viewer assets at
 * runtime -- the pdf.js worker, CMaps for embedded fonts, and per-type third-party code.
 * Those cannot come from cdn01.boxcdn.net: Experience Cloud CSP allows only 'self' under
 * script-src and worker-src, which is the same wall that defeated the earlier vendored
 * copy.
 *
 * Copied from node_modules at build time rather than committed, so the assets stay
 * pinned to the box-content-preview version in package.json and never enter git.
 *
 * model3d is excluded deliberately: it is 17 MB of the package's 25 MB and renders 3D
 * models, which a contract workspace never previews. Add it back here if that changes.
 */
import { cp, mkdir, rm, readdir, stat } from "node:fs/promises";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const SOURCE = join(ROOT, "node_modules", "box-content-preview", "dist", "lib");
const TARGET = join(ROOT, "public", "box-preview");
const EXCLUDE = new Set(["model3d"]);

async function directorySize(dir) {
  let total = 0;
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const full = join(dir, entry.name);
    total += entry.isDirectory() ? await directorySize(full) : (await stat(full)).size;
  }
  return total;
}

async function main() {
  if (!existsSync(SOURCE)) {
    console.error(
      "[box-preview] box-content-preview is not installed. Run `npm install` before building.",
    );
    process.exit(1);
  }

  await rm(TARGET, { recursive: true, force: true });
  await mkdir(TARGET, { recursive: true });

  await cp(SOURCE, TARGET, {
    recursive: true,
    filter: (source) => {
      const relative = source.slice(SOURCE.length + 1);
      const [first, second] = relative.split("/");
      // Skip the 3D viewer wherever it appears in the tree.
      return !(EXCLUDE.has(first) || (first === "third-party" && EXCLUDE.has(second)));
    },
  });

  const megabytes = ((await directorySize(TARGET)) / 1024 / 1024).toFixed(1);
  console.log(`[box-preview] staged runtime assets into public/box-preview (${megabytes} MB)`);
}

await main();
