from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import mm
from pathlib import Path

OUT=Path("docs")
OUT.mkdir(exist_ok=True)

manuals={
"SMX-3_Manual_EN.pdf": {
"title":"125A SMX-3 V2 2.0.0 - User Manual",
"sections":[
("1. Overview",[
"SMX-3 V2 is a free saturation processor by 125A. The package contains two plug-in variants: SMX-3 V2 Mix FX for the Mix FX slot in Studio One / Fender Studio, and SMX-3 V2 Channel as a conventional VST3 insert for channels and buses.",
"Both variants use the same V2 saturation engine with Triode, Pentode and Iron hardware-character modes. Drive includes calibrated internal level compensation. Bypass is the only fully neutral state."
]),
("2. Installation",[
"Copy both complete .vst3 bundles to C:\\Program Files\\Common Files\\VST3. Restart Studio One / Fender Studio afterwards or rescan plug-ins if required."
]),
("3. Which version should I use?",[
"SMX-3 V2 Channel: conventional VST3 insert for instruments, vocals, drums, buses or the master channel.",
"SMX-3 V2 Mix FX: dedicated version for the Mix FX slot in Studio One / Fender Studio."
]),
("4. Controls",[
"Bypass / On-Off: enables or bypasses processing.",
"Drive: controls saturation intensity. 0% still retains a subtle hardware path; only Bypass is fully neutral.",
"Character: Triode - softer and rounded; Pentode - more direct and harmonically assertive; Iron - denser and transformer-like.",
"Mix: dry/wet balance. 100% is fully processed.",
"Output: final output gain after processing."
]),
("5. Automation",[
"Bypass, Drive, Character, Mix and Output can be automated in the DAW. V2 was checked for automated parameter changes and multiple processing block sizes."
]),
("6. Gain staging",[
"Drive is internally level-compensated across the three character modes. Use Output for final gain staging or when you deliberately want a different output level."
]),
("7. System requirements",[
"Windows x64; VST3-compatible host for SMX-3 V2 Channel; Studio One / Fender Studio for SMX-3 V2 Mix FX."
]),
("8. QA status",[
"SMX-3 V2 2.0.0 release candidate passed the Steinberg validator for Channel with 47/47 tests, the Mix FX Audio Mix Processor class scan, V2 state migration/recall checks, and the 44.1/48/96/192 kHz release matrix."
]),
("9. Freeware and trademarks",[
"SMX-3 is provided free of charge under the terms in LICENSE.txt. SMX-3 is not a product of PreSonus or Fender. Studio One, Fender Studio and VST are trademarks of their respective owners."
])
]},
"SMX-3_Handbuch_DE.pdf": {
"title":"125A SMX-3 V2 2.0.0 - Bedienungsanleitung",
"sections":[
("1. Überblick",[
"SMX-3 V2 ist ein kostenloser Saturation-Prozessor von 125A. Das Paket enthält zwei Plug-in-Varianten: SMX-3 V2 Mix FX für den Mix-FX-Slot in Studio One / Fender Studio und SMX-3 V2 Channel als normalen VST3-Insert für Kanäle und Busse.",
"Beide Varianten verwenden dieselbe V2-Saturation-Engine mit den Hardware-Charakteren Triode, Pentode und Iron. Drive besitzt eine kalibrierte interne Pegelkompensation. Nur Bypass ist vollständig neutral."
]),
("2. Installation",[
"Beide kompletten .vst3-Bundles nach C:\\Program Files\\Common Files\\VST3 kopieren. Danach Studio One / Fender Studio neu starten oder einen Plug-in-Scan ausführen."
]),
("3. Welche Version soll ich verwenden?",[
"SMX-3 V2 Channel: normaler VST3-Insert für Instrumente, Vocals, Drums, Busse oder Master.",
"SMX-3 V2 Mix FX: spezielle Version für den Mix-FX-Slot in Studio One / Fender Studio."
]),
("4. Bedienelemente",[
"Bypass / On-Off: schaltet die Bearbeitung ein oder aus.",
"Drive: bestimmt die Sättigungsintensität. Auch 0% behält einen subtilen Hardware-Pfad; vollständig neutral ist nur Bypass.",
"Character: Triode - weicher und runder; Pentode - direkter und obertonreicher; Iron - dichter und transformatorartig.",
"Mix: Verhältnis aus trockenem und bearbeitetem Signal. 100% entspricht vollständig bearbeitetem Signal.",
"Output: finaler Ausgangspegel nach der Bearbeitung."
]),
("5. Automation",[
"Bypass, Drive, Character, Mix und Output können automatisiert werden. V2 wurde mit automatisierten Parameterwechseln und verschiedenen Processing-Blockgrößen geprüft."
]),
("6. Gain-Staging",[
"Drive wird innerhalb der drei Character-Modi intern pegelkompensiert. Output dient dem abschließenden Gain-Staging oder einer bewusst gewünschten Pegelanpassung."
]),
("7. Systemvoraussetzungen",[
"Windows x64; VST3-kompatibler Host für SMX-3 V2 Channel; Studio One / Fender Studio für SMX-3 V2 Mix FX."
]),
("8. QA-Status",[
"Der Release Candidate von SMX-3 V2 2.0.0 bestand den Steinberg Validator für Channel mit 47/47 Tests, den Audio-Mix-Processor-Klassenscan für Mix FX, V2 State-Migration/Recall und die Release-Matrix mit 44,1/48/96/192 kHz."
]),
("9. Freeware und Marken",[
"SMX-3 wird entsprechend den Bedingungen in LICENSE.txt kostenlos bereitgestellt. SMX-3 ist kein Produkt von PreSonus oder Fender. Studio One, Fender Studio und VST sind Marken ihrer jeweiligen Rechteinhaber."
])
]}
}

styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name="ManualTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=20, leading=24, alignment=TA_CENTER, spaceAfter=12))
styles.add(ParagraphStyle(name="ManualHeading", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=13, leading=16, spaceBefore=8, spaceAfter=5))
styles.add(ParagraphStyle(name="ManualBody", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.5, leading=13, spaceAfter=5))
styles.add(ParagraphStyle(name="ManualFoot", parent=styles["BodyText"], fontName="Helvetica", fontSize=8, leading=10, textColor=colors.grey))

for filename,data in manuals.items():
    doc=SimpleDocTemplate(str(OUT/filename), pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=16*mm, bottomMargin=16*mm)
    story=[Paragraph(data["title"],styles["ManualTitle"]), Paragraph("125A - Windows x64 / VST3",styles["ManualFoot"]), Spacer(1,8)]
    for heading,paras in data["sections"]:
        story.append(Paragraph(heading,styles["ManualHeading"]))
        for p in paras:
            story.append(Paragraph(p.replace("&","&amp;"),styles["ManualBody"]))
    doc.build(story)
    print(f"generated {OUT/filename}")
