import { FileBlob, PresentationFile } from "@oai/artifact-tool";
const deck = await PresentationFile.importPptx(await FileBlob.load("D:/RAG Projrects/Test/operating-review-build/template-starter.pptx"));
for (const id of ["sh/itozupwb", "sh/xsfylkfq", "tb/wb65kj2d"]) {
  const target = deck.resolve(id);
  console.log(id, Object.getOwnPropertyNames(Object.getPrototypeOf(target)).join(","));
}
