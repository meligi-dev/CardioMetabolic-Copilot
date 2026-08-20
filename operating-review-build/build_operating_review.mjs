import fs from "node:fs/promises";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const tmp = "D:/RAG Projrects/Test/operating-review-build";
const starter = `${tmp}/template-starter.pptx`;
const output = "D:/RAG Projrects/Test/Clinical_Guideline_RAG_Operating_Review.pptx";
const deck = await PresentationFile.importPptx(await FileBlob.load(starter));

async function writeBlob(path, blob) {
  await fs.writeFile(path, new Uint8Array(await blob.arrayBuffer()));
}

const inspected = await deck.inspect({ kind: "slide,textbox,shape,table,notes", maxChars: 60000 });
const records = inspected.ndjson.split(/\r?\n/).filter(Boolean).map(JSON.parse);
const bySlide = new Map();
for (const record of records) {
  if (!Number.isInteger(record.slide)) continue;
  if (!bySlide.has(record.slide)) bySlide.set(record.slide, []);
  bySlide.get(record.slide).push(record);
}

function textRecords(slideNumber) {
  return (bySlide.get(slideNumber) || []).filter(
    (record) => record.kind === "textbox" && record.placeholder !== "slideNumber",
  );
}

function rewriteAll(slideNumber, values) {
  const targets = textRecords(slideNumber);
  if (targets.length !== values.length) {
    throw new Error(`Slide ${slideNumber}: expected ${values.length} editable text boxes, found ${targets.length}.`);
  }
  targets.forEach((record, index) => {
    const target = deck.resolve(record.id);
    target.text.set(values[index]);
  });
}

function deleteFooter(slideNumber) {
  const footer = (bySlide.get(slideNumber) || []).find(
    (record) => record.kind === "shape" && record.placeholder === "footer",
  );
  if (!footer) throw new Error(`Slide ${slideNumber}: footer placeholder not found.`);
  deck.resolve(footer.id).delete();
}

function setNotes(slideNumber, sources) {
  const notes = (bySlide.get(slideNumber) || []).find((record) => record.kind === "notes");
  if (!notes) throw new Error(`Slide ${slideNumber}: notes target not found.`);
  deck.resolve(notes.id).setText(`[Sources]\n- ${sources.join("\n- ")}`);
}

rewriteAll(1, [
  "Clinical Guideline\nRAG Copilot",
  "Project operating review\n20 August 2026",
  "Prepared for\nProject stakeholders",
  "Repository snapshot",
  "Clinical AI Project",
]);
setNotes(1, ["PROJECT_OVERVIEW.md (project purpose and scope)"]);

rewriteAll(2, ["Operating review", "Agenda"]);
const agenda = (bySlide.get(2) || []).find((record) => record.kind === "table");
if (!agenda) throw new Error("Slide 2: agenda table not found.");
const agendaRows = [
  ["01", "Purpose & scope"],
  ["02", "Solution architecture"],
  ["03", "Evidence coverage"],
  ["04", "Benchmark scorecard"],
  ["05", "Readiness & risks"],
  ["06", "Actions & decisions"],
];
const agendaTable = deck.resolve(agenda.id);
agendaRows.forEach((row, rowIndex) => row.forEach((value, columnIndex) => agendaTable.cells.set(rowIndex, columnIndex, value)));
deleteFooter(2);
setNotes(2, ["PROJECT_OVERVIEW.md (review structure)"]);

rewriteAll(3, [
  "A clinical decision-support application, not a clinical authority",
  "Clinical guideline Q&A\nFree-text questions with patient context.",
  "Patient parameter analyzer\nStructured cardiometabolic data and notes.",
  "Evidence & safety\nOptions, warnings, citations and follow-ups.",
  "Decision-support guardrail\nSupports—not replaces—judgment or local protocols.",
  "For licensed healthcare professionals. The prototype retrieves guideline passages and returns structured clinical analysis.",
]);
deleteFooter(3);
setNotes(3, ["PROJECT_OVERVIEW.md (purpose and capabilities)"]);

rewriteAll(4, [
  "The current workflow connects a clinician question to retrieved evidence",
  "Structured intake\nPatient parameters or a free-text clinical question.",
  "1. FastAPI receives the request through /api.\n2. ClinicalRAGEngine invokes Weaviate hybrid search and returns recommendation-level chunks with parent context.",
  "INPUTS",
  "Clinician experience\nReact + Vite renders recommendations and citations.",
  "3. An OpenAI-compatible endpoint produces structured clinical JSON.\n4. The frontend calls the local backend during development.",
  "DELIVERY",
]);
deleteFooter(4);
setNotes(4, ["PROJECT_OVERVIEW.md (architecture and frontend/backend details)"]);

rewriteAll(5, [
  "Indexed material covers six clinical source groups",
  "Retrieval can cover broader specialties, but the dedicated form and system prompt remain cardiometabolic-focused.",
  "GOLD / GINA\n2024", "COPD and asthma",
  "IDSA / Sepsis\n2024", "Infectious disease",
  "WHO / FDA\nformulary", "Dosing & warnings",
  "ADA\n2024", "Diabetes & obesity",
  "ACC/AHA\n2023", "HF, hypertension & lipids",
  "KDIGO\n2023", "CKD & diabetes",
]);
deleteFooter(5);
setNotes(5, ["PROJECT_OVERVIEW.md (guideline sources and scope)"]);

rewriteAll(6, [
  "Internal benchmark indicates strong concept-match performance",
  "85%", "Guideline\nretrieval recall",
  "90%", "Recommendation\nrecall",
  "85%", "Safety\nrecall",
  "92.6%", "Overall\nF1 score",
  "Checked-in evaluation report:\n10 benchmark cases",
  "Internal retrieval / concept-match metrics; not proof of clinical validity.",
]);
deleteFooter(6);
setNotes(6, ["eval/evaluation_report.json (aggregate metrics and 10 benchmark cases)", "PROJECT_OVERVIEW.md (metric limitations)"]);

rewriteAll(7, [
  "Clinical deployment needs safety and governance work",
  "Evidence governance\nValidate guideline sources and citations against current primary sources.",
  "Versioning & provenance\nEffective dates\nFormal source review",
  "Clinical & privacy controls\nAdd security and privacy controls before processing PHI.",
  "Authentication & authorization\nAudit logging\nEncryption & privacy",
  "Current state\nThe repository supports controlled development evaluation; it is not ready for independent clinical deployment.",
  "Specific functionality risk: if the backend is unavailable, the frontend can generate a demonstration fallback. It must not be mistaken for retrieved evidence.",
]);
deleteFooter(7);
setNotes(7, ["PROJECT_OVERVIEW.md (current limitations and recommended next steps)"]);

rewriteAll(8, [
  "Prioritize provenance, clear failure behavior, test coverage and governance before expansion.",
  "Next operating cycle: deployment evidence",
  "Decision requests\n1. Confirm a non-clinical deployment boundary.\n2. Fund safety, provenance and privacy work before live patient data.\n3. Review evidence and test coverage in the next operating cycle.",
  "Make fallback an explicit offline/error state",
  "Verify guideline currency and provenance",
  "Add API, retrieval, schema & end-to-end tests",
  "Add authentication, audit logging & privacy controls",
  "Validate broader specialty scope before expansion",
]);
deleteFooter(8);
setNotes(8, ["PROJECT_OVERVIEW.md (current limitations and recommended next steps)"]);

rewriteAll(9, [
  "Decision requests\nfor the next review",
  "Confirm safety and governance priorities\nbefore widening scope.",
  "Clinical Guideline RAG Copilot",
]);
setNotes(9, ["PROJECT_OVERVIEW.md (deployment limitations and recommended next steps)"]);

await fs.mkdir(`${tmp}/final-render`, { recursive: true });
for (const [index, slide] of deck.slides.items.entries()) {
  await writeBlob(`${tmp}/final-render/slide-${String(index + 1).padStart(2, "0")}.png`, await deck.export({ slide, format: "png", scale: 1 }));
  const layout = await deck.export({ slide, format: "layout" });
  await fs.writeFile(`${tmp}/final-render/slide-${String(index + 1).padStart(2, "0")}.layout.json`, await layout.text());
}
await writeBlob(`${tmp}/final-render/deck-montage.webp`, await deck.export({ format: "webp", montage: true, scale: 1 }));
const pptx = await PresentationFile.exportPptx(deck);
await pptx.save(output);
