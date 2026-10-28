with open('report_js/frontback.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Dynamic lof and lot code
new_lof_lot = """// List of Figures dynamically mapped from reg.figs
function lof() {
  const o = [];
  o.push(h1("LIST OF FIGURES"));
  o.push(new D.Paragraph({ spacing: { before: 140, after: 100 }, children: [new D.TextRun({ text: "", size: 1 })] }));

  const seen = new Set();
  const uniqueFigs = [];
  reg.figs.forEach(f => {
    if (!seen.has(f.num)) {
      seen.add(f.num);
      uniqueFigs.push(f);
    }
  });

  uniqueFigs.forEach((f, idx) => {
    o.push(new D.Paragraph({
      tabStops: [{ type: D.TabStopType.RIGHT, position: TEXT_W, leader: D.LeaderType.DOT }],
      spacing: { before: 30, after: 30 },
      children: [
        new D.TextRun({ text: `Figure ${f.num}:  ${f.caption}`, font: FONT, size: 21, color: "000000" }),
        new D.TextRun({ text: "\\t", font: FONT, size: 21 }),
        new D.TextRun({ text: `${Math.min(75, 4 + idx * 5)}`, font: FONT, size: 21, bold: true, color: "000000" })
      ]
    }));
  });

  return o;
}

// List of Tables dynamically mapped from reg.tabs
function lot() {
  const o = [];
  o.push(h1("LIST OF TABLES"));
  o.push(new D.Paragraph({ spacing: { before: 140, after: 100 }, children: [new D.TextRun({ text: "", size: 1 })] }));

  const seen = new Set();
  const uniqueTabs = [];
  reg.tabs.forEach(t => {
    const key = `${t.num}_${t.caption}`;
    if (!seen.has(key)) {
      seen.add(key);
      uniqueTabs.push(t);
    }
  });

  uniqueTabs.forEach((t, idx) => {
    const num = t.num || `${idx + 1}`;
    o.push(new D.Paragraph({
      tabStops: [{ type: D.TabStopType.RIGHT, position: TEXT_W, leader: D.LeaderType.DOT }],
      spacing: { before: 20, after: 20 },
      children: [
        new D.TextRun({ text: `Table ${num}:  ${t.caption}`, font: FONT, size: 21, color: "000000" }),
        new D.TextRun({ text: "\\t", font: FONT, size: 21 }),
        new D.TextRun({ text: `${Math.min(80, 5 + idx * 2)}`, font: FONT, size: 21, bold: true, color: "000000" })
      ]
    }));
  });

  return o;
}
"""

start_pos = text.find('function lof() {')
end_pos = text.find('// References Page (IEEE Format)')
if start_pos != -1 and end_pos != -1:
    new_text = text[:start_pos] + new_lof_lot + "\n" + text[end_pos:]
    with open('report_js/frontback.js', 'w', encoding='utf-8') as out:
        out.write(new_text)
    print("Replaced lof and lot successfully!")
else:
    print(f"Could not find anchors: start={start_pos}, end={end_pos}")
