import fs from "node:fs";
import path from "node:path";
import { createHash } from "node:crypto";

export interface StickerBundle {
  owner: "ai-ggbond-sticker-writer";
  schema_version: 1;
  article_type: "newspic";
  status: "ready" | "review_required";
  title: string;
  author?: string;
  content: string;
  images: { id: string; order: number; path: string; sha256: string; alt: string; localPath: string }[];
  draft_target?: { account?: string | null; existing_media_id?: string | null };
}

// Local validation only. No credentials, uploads, network calls or image editing.
export function readStickerBundle(file: string): StickerBundle {
  const data = JSON.parse(fs.readFileSync(file, "utf8"));
  if (data.owner !== "ai-ggbond-sticker-writer" || data.schema_version !== 1 || data.article_type !== "newspic") {
    throw new Error("Unsupported sticker bundle; use sticker_pack.py output");
  }
  const root = fs.realpathSync(path.dirname(file));
  const manifest = JSON.parse(fs.readFileSync(path.join(root,"manifest.json"),"utf8"));
  if (manifest.owner !== data.owner || !manifest.files || !manifest.files[path.basename(file)]) throw new Error("Sticker manifest is missing its handoff record");
  for (const [name,hash] of Object.entries(manifest.files)) {
    const checked=fs.realpathSync(path.resolve(root,name));
    const relative=path.relative(root,checked);
    if (!relative || relative === ".." || relative.startsWith(".."+path.sep) || path.isAbsolute(relative) || createHash("sha256").update(fs.readFileSync(checked)).digest("hex") !== hash) {
      throw new Error("Sticker manifest changed after review: "+name);
    }
  }
  if (!data.title || typeof data.title !== "string" || typeof data.content !== "string" || !["ready", "review_required"].includes(data.status)) {
    throw new Error("Sticker title, plain content or review status is invalid");
  }
  if (/^\s*#{1,6}\s|\*\*|!\[[^\]]*\]\(|<\/?[A-Za-z][^>]*>/m.test(data.content)) {
    throw new Error("Native sticker content must be plain text, not article HTML or Markdown");
  }
  if (!Array.isArray(data.images) || data.images.length === 0) throw new Error("Sticker images are missing");
  const ids = new Set<string>();
  const images = data.images.map((image: any, index: number) => {
    if (!image || typeof image.id !== "string" || ids.has(image.id) || image.order !== index + 1 || typeof image.path !== "string" || !/^[a-f0-9]{64}$/.test(image.sha256)) {
      throw new Error("Sticker image order, identity or hash is invalid");
    }
    ids.add(image.id);
    const localPath = fs.realpathSync(path.resolve(root, image.path));
    const relative = path.relative(root, localPath);
    if (!relative || relative === ".." || relative.startsWith(".." + path.sep) || path.isAbsolute(relative)) {
      throw new Error("Sticker images must be inside the delivery bundle");
    }
    if (!fs.statSync(localPath).isFile() || !/\.(png|jpe?g|gif|webp)$/i.test(localPath)) throw new Error("Unsupported sticker image file");
    if (createHash("sha256").update(fs.readFileSync(localPath)).digest("hex") !== image.sha256) {
      throw new Error("Sticker image changed after review: " + image.id);
    }
    return { ...image, localPath };
  });
  if (data.draft_target !== undefined && (!data.draft_target || typeof data.draft_target !== "object" || Array.isArray(data.draft_target))) {
    throw new Error("Invalid sticker draft target");
  }
  for (const key of ["account","existing_media_id"]) if (data.draft_target?.[key] != null && typeof data.draft_target[key] !== "string") throw new Error("Invalid sticker target field: "+key);
  return { ...data, images };
}

export function assertStickerWritable(bundle: StickerBundle): void {
  if (bundle.status !== "ready") throw new Error("Sticker image/content review is pending; finish the local review before uploading");
  if (bundle.draft_target?.existing_media_id) throw new Error("This bundle targets an existing draft; use draft update instead of creating a duplicate");
}

export async function uploadStickerImages(bundle: StickerBundle, upload: (file: string) => Promise<{ media_id?: string }>): Promise<string[]> {
  const ids: string[] = [];
  for (const image of bundle.images) {
    const result = await upload(image.localPath);
    if (!result.media_id) throw new Error("Image upload returned no media_id: " + image.id);
    ids.push(result.media_id);
  }
  return ids;
}
