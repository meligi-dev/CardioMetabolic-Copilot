import fs from "node:fs/promises";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const source = "C:/Users/MF/.codex/plugins/cache/openai-curated-remote/openai-templates/0.1.1/skills/artifact-template-operating-review/assets/reference.pptx";
const output = "D:/RAG Projrects/Test/operating-review-build/selected-slides-inspect.ndjson";
const deck = await PresentationFile.importPptx(await FileBlob.load(source));
const all = await deck.inspect({ kind: "slide", maxChars: 30000 });
const lines = all.ndjson.split(/\r?\n/).filter(Boolean).map(JSON.parse);
const picks = new Set([1, 2, 7, 9, 10, 17, 28, 30, 31]);
const outputLines = [];
for (const item of lines.filter((item) => picks.has(item.slide))) {
  const detail = await deck.inspect({
    kind: "slide,textbox,shape,image,table,chart,notes",
    target: { id: item.id, beforeLines: 0, afterLines: 0 },
    maxChars: 18000,
  });
  outputLines.push(`--- SLIDE ${item.slide} ${item.id} ---`);
  outputLines.push(detail.ndjson);
}
await fs.writeFile(output, `${outputLines.join("\n")}\n`, "utf8");
