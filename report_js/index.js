const D = require("docx");
const { Paragraph, TextRun, AlignmentType, Header, Footer,
        TabStopType, SectionType, BorderStyle } = D;
const fs = require("fs");
const path = require("path");

// Load references and lib
require("./refs");
const { FONT, PAGE_W, PAGE_H, MARGIN, TEXT_W, MID_W, reg } = require("./lib");
const fb = require("./frontback");

// Chapter modules
const ch12 = require("./ch12");
const ch34 = require("./ch34");
const ch567 = require("./ch567");

function pageBreak() {
  return new Paragraph({ children: [new D.PageBreak()] });
}

// Running header text: A4 width tab stop
function makeHeader() {
  return new Header({
    children: [new Paragraph({
      border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "000000", space: 4 } },
      alignment: AlignmentType.LEFT,
      tabStops: [{ type: TabStopType.RIGHT, position: TEXT_W }],
      children: [
        new TextRun({ text: "LogShield: Runtime Log Secret Detection and Recovery System", font: FONT, size: 18, color: "000000" }),
        new TextRun({ text: "\t", font: FONT }),
        new TextRun({ text: "Academic Year: 2026-27", font: FONT, size: 18, color: "000000" }),
      ],
    })],
  });
}

function makeFooter() {
  return new Footer({
    children: [new Paragraph({
      alignment: AlignmentType.RIGHT,
      children: [
        new TextRun({ children: [D.PageNumber.CURRENT], font: FONT, size: 20, color: "000000" })
      ]
    })]
  });
}

// Numbering configuration for lists
const numbering = {
  config: [
    { reference: "bullets", levels: [{ level: 0, format: D.LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    { reference: "nums", levels: [{ level: 0, format: D.LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
  ],
};

// Document Styles: PURE BLACK HEADINGS ONLY, NO BLUE
const styles = {
  default: {
    document: { run: { font: FONT, size: 24, color: "000000" } },
    heading1: { run: { font: FONT, size: 28, bold: true, color: "000000" }, paragraph: { spacing: { before: 360, after: 180 }, alignment: AlignmentType.CENTER } },
    heading2: { run: { font: FONT, size: 24, bold: true, color: "000000" }, paragraph: { spacing: { before: 260, after: 100 } } },
    heading3: { run: { font: FONT, size: 24, bold: true, italics: true, color: "000000" }, paragraph: { spacing: { before: 180, after: 80 } } },
  },
  paragraphStyles: [],
};

const a4Page = {
  size: { width: PAGE_W, height: PAGE_H },
  margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN }
};

console.log("Generating LogShield Capstone Report via Node.js docx engine (A4 Standard)...");

// 1. Process chapters and appendices first to populate reg.figs, reg.tabs, and reg.cited
const body12 = ch12();
const body34 = ch34();
const body567 = ch567();
const appA     = fb.appendixA();
const appB     = fb.appendixB();
const appC     = fb.appendixC();
const appD     = fb.appendixD();
const refs     = fb.references();

console.log(`Chapters and Appendices processed: ${reg.figs.length} figures, ${reg.tabs.length} tables, ${reg.cited.length} citations.`);

// 2. Generate front matter (now fully aware of all registered figures and tables)
const title    = fb.titlePage();
const cert     = fb.certificate();
const approval = fb.certOfApproval();
const decl     = fb.declaration();
const ack      = fb.acknowledgement();
const abs      = fb.abstract();
const toc      = fb.toc();
const lof      = fb.lof();
const lot      = fb.lot();

// 3. Assemble document sections (Each front matter page is its own clean section)
const doc = new D.Document({
  numbering,
  styles,
  sections: [
    { properties: { page: a4Page }, children: title },
    { properties: { type: SectionType.NEXT_PAGE, page: a4Page }, children: cert },
    { properties: { type: SectionType.NEXT_PAGE, page: a4Page }, children: approval },
    { properties: { type: SectionType.NEXT_PAGE, page: a4Page }, children: decl },
    { properties: { type: SectionType.NEXT_PAGE, page: a4Page }, children: ack },
    { properties: { type: SectionType.NEXT_PAGE, page: a4Page }, children: abs },
    { properties: { type: SectionType.NEXT_PAGE, page: a4Page }, children: toc },
    { properties: { type: SectionType.NEXT_PAGE, page: a4Page }, children: lof },
    { properties: { type: SectionType.NEXT_PAGE, page: a4Page }, children: lot },

    // Main Body: Chapters 1-7, References, and Appendices A-D
    {
      properties: { type: SectionType.NEXT_PAGE, page: a4Page },
      headers: { default: makeHeader() },
      footers: { default: makeFooter() },
      children: [
        ...body12, pageBreak(),
        ...body34, pageBreak(),
        ...body567, pageBreak(),
        ...refs, pageBreak(),
        ...appA, pageBreak(),
        ...appB, pageBreak(),
        ...appC, pageBreak(),
        ...appD
      ],
    },
  ],
});

// 4. Pack and write output file
async function build() {
  const buf = await D.Packer.toBuffer(doc);
  const kb = Math.round(buf.length / 1024);

  const targets = [
    path.resolve(__dirname, "../LogShield_Final_Report_v7_Complete.docx"),
    path.resolve(__dirname, "../LogShield_Final_Report_Updated.docx"),
    path.resolve(__dirname, "../LogShield_Final_Report.docx")
  ];

  for (const target of targets) {
    try {
      fs.writeFileSync(target, buf);
      console.log(`Successfully wrote ${kb} KB to: ${target}`);
    } catch (err) {
      if (err.code === "EBUSY" || err.code === "EPERM") {
        console.warn(`File locked by external viewer (e.g. Word): ${target}. Trying fallback name...`);
        const fallback = target.replace(".docx", "_fresh.docx");
        fs.writeFileSync(fallback, buf);
        console.log(`Wrote fallback to: ${fallback}`);
      } else {
        throw err;
      }
    }
  }

  console.log(`\n======================================================`);
  console.log(`Document Generation Complete (A4 Standard)!`);
  console.log(`Total Figures Registered: ${reg.figs.length}`);
  console.log(`Total Tables Registered:  ${reg.tabs.length}`);
  console.log(`Total Citations Mapped:   ${reg.cited.length}`);
  console.log(`Document Size:            ${kb} KB`);
  console.log(`Headings Styling:         STRICTLY BLACK (#000000), BOLD`);
  console.log(`======================================================`);
}

build().catch(err => {
  console.error("Build failed:", err);
  process.exit(1);
});
