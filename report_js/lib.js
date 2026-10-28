const D = require("docx");
const fs = require("fs");
const path = require("path");

const FONT = "Times New Roman";
// A4 Paper Dimensions (210 mm x 297 mm)
const PAGE_W = 11906; // A4 width in twips (595.3 pt)
const PAGE_H = 16838; // A4 height in twips (841.9 pt)
const MARGIN = 1440;  // 1 inch in twips (72.0 pt)
const TEXT_W = PAGE_W - (2 * MARGIN); // 9026 twips (451.3 pt)
const MID_W = Math.round(TEXT_W / 2); // 4513 twips (225.65 pt)

const reg = {
  tabs: [],
  figs: [],
  cited: []
};

// Citation lookup
let REFS_MAP = null;
function getRefsMap() {
  if (!REFS_MAP) {
    REFS_MAP = require("./refs").REFS;
  }
  return REFS_MAP;
}

function c(key) {
  const map = getRefsMap();
  const keys = key.split(",").map(k => k.trim());
  const nums = [];
  for (const k of keys) {
    if (map[k]) {
      if (!reg.cited.includes(k)) {
        reg.cited.push(k);
      }
      nums.push(reg.cited.indexOf(k) + 1);
    } else {
      nums.push(k);
    }
  }
  return `[${nums.join(", ")}]`;
}

// Inline formatting parser
function parseRuns(text, baseProps = {}) {
  const runs = [];
  const regex = /(\*\*([^*]+)\*\*|\*([^*]+)\*|`([^`]+)`)/g;
  let lastIndex = 0;
  let match;

  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      runs.push(new D.TextRun({
        text: text.substring(lastIndex, match.index),
        font: FONT,
        size: baseProps.size || 24,
        color: baseProps.color || "000000",
        ...baseProps
      }));
    }

    if (match[2]) {
      // Bold
      runs.push(new D.TextRun({
        text: match[2],
        font: FONT,
        size: baseProps.size || 24,
        bold: true,
        color: baseProps.color || "000000",
        ...baseProps
      }));
    } else if (match[3]) {
      // Italic
      runs.push(new D.TextRun({
        text: match[3],
        font: FONT,
        size: baseProps.size || 24,
        italics: true,
        color: baseProps.color || "000000",
        ...baseProps
      }));
    } else if (match[4]) {
      // Inline code
      runs.push(new D.TextRun({
        text: match[4],
        font: "Consolas",
        size: (baseProps.size || 24) - 2,
        color: "000000"
      }));
    }
    lastIndex = regex.lastIndex;
  }

  if (lastIndex < text.length) {
    runs.push(new D.TextRun({
      text: text.substring(lastIndex),
      font: FONT,
      size: baseProps.size || 24,
      color: baseProps.color || "000000",
      ...baseProps
    }));
  }

  return runs.length > 0 ? runs : [new D.TextRun({ text: "", font: FONT, size: baseProps.size || 24 })];
}

function p(text, opts = {}) {
  return new D.Paragraph({
    alignment: opts.alignment || D.AlignmentType.JUSTIFIED,
    spacing: {
      before: opts.before || 0,
      after: opts.after !== undefined ? opts.after : 140, // 7 pt
      line: opts.line || 360 // 1.5 line spacing as per institutional standard
    },
    children: parseRuns(text, opts)
  });
}

function h1(text) {
  return new D.Paragraph({
    heading: D.HeadingLevel.HEADING_1,
    alignment: D.AlignmentType.CENTER,
    spacing: { before: 360, after: 180 },
    keepNext: true,
    children: [
      new D.TextRun({
        text: text.toUpperCase(),
        font: FONT,
        size: 28, // 14pt
        bold: true,
        color: "000000" // STRICTLY BLACK
      })
    ]
  });
}

function h2(text) {
  return new D.Paragraph({
    heading: D.HeadingLevel.HEADING_2,
    alignment: D.AlignmentType.LEFT,
    spacing: { before: 260, after: 100 },
    keepNext: true,
    children: [
      new D.TextRun({
        text,
        font: FONT,
        size: 24, // 12pt
        bold: true,
        color: "000000" // STRICTLY BLACK
      })
    ]
  });
}

function h3(text) {
  return new D.Paragraph({
    heading: D.HeadingLevel.HEADING_3,
    alignment: D.AlignmentType.LEFT,
    spacing: { before: 180, after: 80 },
    keepNext: true,
    children: [
      new D.TextRun({
        text,
        font: FONT,
        size: 24, // 12pt
        bold: true,
        italics: true,
        color: "000000" // STRICTLY BLACK
      })
    ]
  });
}

function bullets(arr) {
  return arr.map(item => new D.Paragraph({
    bullet: { level: 0 },
    alignment: D.AlignmentType.JUSTIFIED,
    spacing: { before: 40, after: 60, line: 360 },
    children: parseRuns(item)
  }));
}

// Formal academic table matching A4 TEXT_W
function tbl(num, caption, headers, rows, colWidths = null) {
  reg.tabs.push({ num, caption });

  const numCols = headers.length;
  let widths = [];
  if (colWidths && colWidths.length === numCols) {
    const sum = colWidths.reduce((a, b) => a + b, 0);
    widths = colWidths.map(w => Math.round((w / sum) * TEXT_W));
  } else {
    const evenW = Math.round(TEXT_W / numCols);
    widths = new Array(numCols).fill(evenW);
  }

  const borderSpec = {
    top: { style: D.BorderStyle.SINGLE, size: 6, color: "000000" },
    bottom: { style: D.BorderStyle.SINGLE, size: 6, color: "000000" },
    left: { style: D.BorderStyle.SINGLE, size: 4, color: "B0B0B0" },
    right: { style: D.BorderStyle.SINGLE, size: 4, color: "B0B0B0" },
    insideHorizontal: { style: D.BorderStyle.SINGLE, size: 4, color: "E0E0E0" },
    insideVertical: { style: D.BorderStyle.SINGLE, size: 4, color: "E0E0E0" }
  };

  const headerRow = new D.TableRow({
    tableHeader: true,
    cantSplit: true,
    children: headers.map((h, i) => new D.TableCell({
      width: { size: widths[i], type: D.WidthType.DXA },
      shading: { fill: "F2F2F2" }, // Light formal grey
      margins: { top: 120, bottom: 120, left: 140, right: 140 },
      children: [
        new D.Paragraph({
          alignment: D.AlignmentType.CENTER,
          spacing: { before: 20, after: 20 },
          children: [new D.TextRun({ text: h, font: FONT, size: 21, bold: true, color: "000000" })]
        })
      ]
    }))
  });

  const tableRows = [headerRow];
  rows.forEach((row, rIdx) => {
    const bgFill = rIdx % 2 === 1 ? "FBFBFB" : "FFFFFF";
    tableRows.push(new D.TableRow({
      cantSplit: true,
      children: row.map((cellText, cIdx) => new D.TableCell({
        width: { size: widths[cIdx], type: D.WidthType.DXA },
        shading: { fill: bgFill },
        margins: { top: 80, bottom: 80, left: 140, right: 140 },
        children: [
          new D.Paragraph({
            alignment: cIdx === 0 && cellText.length < 15 ? D.AlignmentType.CENTER : D.AlignmentType.LEFT,
            spacing: { before: 20, after: 20, line: 240 },
            children: parseRuns(String(cellText), { size: 20, color: "000000" })
          })
        ]
      }))
    }));
  });

  const captionPara = new D.Paragraph({
    alignment: D.AlignmentType.LEFT,
    spacing: { before: 180, after: 80 },
    keepNext: true,
    children: [
      new D.TextRun({ text: `Table ${num}: `, font: FONT, size: 21, bold: true, color: "000000" }),
      new D.TextRun({ text: caption, font: FONT, size: 21, italics: true, color: "000000" })
    ]
  });

  const docTable = new D.Table({
    width: { size: TEXT_W, type: D.WidthType.DXA },
    borders: borderSpec,
    rows: tableRows
  });

  const spacerPara = new D.Paragraph({
    spacing: { before: 0, after: 140 },
    children: [new D.TextRun({ text: "", size: 1 })]
  });

  return [captionPara, docTable, spacerPara];
}

// Helper to read true PNG dimensions for distortion-free aspect ratio
function getPngDimensions(filePath) {
  try {
    const buf = fs.readFileSync(filePath);
    if (buf.length >= 24 && buf.toString("ascii", 12, 16) === "IHDR") {
      const width = buf.readUInt32BE(16);
      const height = buf.readUInt32BE(20);
      return { width, height };
    }
  } catch (e) {}
  return { width: 800, height: 450 };
}

// Figure handler - fully mapped to authentic figures with zero duplicates
const FIG_PATHS = {
  // Front matter
  f_logo: path.resolve(__dirname, "../extracted_images/rId7_image1.png"),

  // Chapter 1
  f_1_1: path.resolve(__dirname, "../extracted_images/rId8_image2.png"),
  f_1_2: path.resolve(__dirname, "../extracted_images/rId9_image3.png"),

  // Chapter 2
  f_2_1: path.resolve(__dirname, "../extracted_images/rId10_image4.png"),

  // Chapter 3
  f_3_1: path.resolve(__dirname, "../extracted_images/rId11_image5.png"),

  // Chapter 4
  f_4_1: path.resolve(__dirname, "../paper/figures/fig1_architecture.png"),
  f_4_2: path.resolve(__dirname, "../paper/figures/fig2_pipeline.png"),
  f_4_3: path.resolve(__dirname, "../extracted_images/rId14_image8.png"),
  f_4_4: path.resolve(__dirname, "../paper/figures/fig3_decision_gate.png"),
  f_4_5: path.resolve(__dirname, "../extracted_images/rId16_image10.png"),
  f_4_6: path.resolve(__dirname, "../extracted_images/rId17_image11.png"),
  f_4_7: path.resolve(__dirname, "../paper/figures/fig6_lineage.png"),
  f_4_8: path.resolve(__dirname, "../paper/figures/fig8_containment_lifecycle.png"),
  f_4_9: path.resolve(__dirname, "../extracted_images/rId18_image12.png"),

  // Chapter 5
  f_5_1: path.resolve(__dirname, "../paper/figures/fig_ml_training.png"),
  f_5_2: path.resolve(__dirname, "../paper/figures/fig4_ablation.png"),
  f_5_3: path.resolve(__dirname, "../paper/figures/fig7_evasion_benchmark.png"),
  f_5_4: path.resolve(__dirname, "../paper/figures/fig_latency_throughput.png"),
  f_5_5: path.resolve(__dirname, "../extracted_images/rId22_image16.png"),
  f_5_6: path.resolve(__dirname, "../extracted_images/rId23_image17.png"),
  f_5_7: path.resolve(__dirname, "../extracted_images/rId24_image18.png"),

  // Chapter 6
  f_6_1: path.resolve(__dirname, "../extracted_images/rId26_image20.png"),

  // Chapter 7
  f_7_1: path.resolve(__dirname, "../paper/figures/fig_contributions_summary.png"),

  // Direct aliases
  f_arch: path.resolve(__dirname, "../paper/figures/fig1_architecture.png"),
  f_pipeline: path.resolve(__dirname, "../paper/figures/fig2_pipeline.png"),
  f_ablation: path.resolve(__dirname, "../paper/figures/fig4_ablation.png"),
  f_benchmark: path.resolve(__dirname, "../paper/figures/fig5_benchmark.png"),
  f_lineage: path.resolve(__dirname, "../paper/figures/fig6_lineage.png"),
  f_evasion: path.resolve(__dirname, "../paper/figures/fig7_evasion_benchmark.png"),
  f_containment: path.resolve(__dirname, "../paper/figures/fig8_containment_lifecycle.png"),
  f_ml: path.resolve(__dirname, "../paper/figures/fig_ml_training.png")
};

function fig(num, key, caption, scale = 0.85, customHeight = null) {
  reg.figs.push({ num, caption });

  const filePath = FIG_PATHS[key] || path.resolve(__dirname, `../paper/figures/${key}.png`);
  if (!fs.existsSync(filePath)) {
    console.warn(`[fig] Warning: Image file not found: ${filePath}`);
    const missingPara = new D.Paragraph({
      alignment: D.AlignmentType.CENTER,
      spacing: { before: 100, after: 100 },
      children: [new D.TextRun({ text: `[Figure ${num}: ${caption} - Image File Not Found]`, font: FONT, size: 20, italics: true })]
    });
    return [missingPara];
  }

  const dims = getPngDimensions(filePath);
  let targetW = Math.round(500 * scale);
  let targetH = customHeight ? Math.round(customHeight * scale) : Math.round(targetW * (dims.height / dims.width));

  // Cap height to ensure it fits cleanly on an A4 page without awkward page overflow
  if (targetH > 340) {
    targetH = 340;
    targetW = Math.round(targetH * (dims.width / dims.height));
  }
  if (targetW > 450) {
    targetW = 450;
    targetH = Math.round(targetW * (dims.height / dims.width));
  }

  const imgRun = new D.ImageRun({
    data: fs.readFileSync(filePath),
    transformation: { width: targetW, height: targetH }
  });

  const imgPara = new D.Paragraph({
    alignment: D.AlignmentType.CENTER,
    spacing: { before: 160, after: 80 },
    keepNext: true,
    children: [imgRun]
  });

  const captionPara = new D.Paragraph({
    alignment: D.AlignmentType.CENTER,
    spacing: { before: 60, after: 180 },
    children: [
      new D.TextRun({ text: `Figure ${num}: `, font: FONT, size: 20, bold: true, color: "000000" }),
      new D.TextRun({ text: caption, font: FONT, size: 20, italics: true, color: "000000" })
    ]
  });

  return [imgPara, captionPara];
}

// Formal academic code block for Appendix A
function codeBlock(listingId, title, codeLines) {
  const captionPara = new D.Paragraph({
    alignment: D.AlignmentType.LEFT,
    spacing: { before: 160, after: 60 },
    keepNext: true,
    children: [
      new D.TextRun({ text: `${listingId}: `, font: FONT, size: 21, bold: true, color: "000000" }),
      new D.TextRun({ text: title, font: FONT, size: 21, italics: true, color: "000000" })
    ]
  });

  const borderSpec = {
    top: { style: D.BorderStyle.SINGLE, size: 6, color: "D0D7DE" },
    bottom: { style: D.BorderStyle.SINGLE, size: 6, color: "D0D7DE" },
    left: { style: D.BorderStyle.SINGLE, size: 6, color: "D0D7DE" },
    right: { style: D.BorderStyle.SINGLE, size: 6, color: "D0D7DE" }
  };

  const linesArr = Array.isArray(codeLines) ? codeLines : codeLines.split("\n");
  const paragraphs = linesArr.map(line => {
    const trimmed = line.trim();
    const isComment = trimmed.startsWith("#") || trimmed.startsWith("//");
    const isKeyword = trimmed.startsWith("def ") || trimmed.startsWith("class ") || 
                      trimmed.startsWith("import ") || trimmed.startsWith("from ") || 
                      trimmed.startsWith("return ") || trimmed.startsWith("if ") || 
                      trimmed.startsWith("elif ") || trimmed.startsWith("else:");
    return new D.Paragraph({
      alignment: D.AlignmentType.LEFT,
      spacing: { before: 8, after: 8, line: 240 },
      children: [
        new D.TextRun({
          text: line.length > 0 ? line : " ",
          font: "Consolas",
          size: 18, // 9 pt
          bold: isKeyword,
          color: isComment ? "57606A" : (isKeyword ? "0550AE" : "24292F")
        })
      ]
    });
  });

  const cell = new D.TableCell({
    width: { size: TEXT_W, type: D.WidthType.DXA },
    shading: { fill: "F6F8FA" }, // Light formal code background
    margins: { top: 100, bottom: 100, left: 160, right: 160 },
    children: paragraphs
  });

  const table = new D.Table({
    width: { size: TEXT_W, type: D.WidthType.DXA },
    borders: borderSpec,
    rows: [new D.TableRow({ cantSplit: true, children: [cell] })]
  });

  const spacerPara = new D.Paragraph({
    spacing: { before: 0, after: 120 },
    children: [new D.TextRun({ text: "", size: 1 })]
  });

  return [captionPara, table, spacerPara];
}

module.exports = {
  FONT,
  PAGE_W,
  PAGE_H,
  MARGIN,
  TEXT_W,
  MID_W,
  reg,
  c,
  p,
  h1,
  h2,
  h3,
  bullets,
  tbl,
  fig,
  codeBlock,
  parseRuns
};
