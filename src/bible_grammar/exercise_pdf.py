"""
Generate fillable PDF passage exercises from structured exercise data.

Produces an AcroForm PDF with:
- Hebrew passage text (RTL, vowel-pointed, Arial Hebrew font)
- English translation line
- One AcroForm text field per parse cell (Conjugation, PGN, Root, Function)
- Correct answers embedded as hidden field default values, revealed via
  a "Show Answers" button (JavaScript AcroForm action)

Usage:
    from bible_grammar.exercise_pdf import ExercisePDF
    pdf = ExercisePDF(title, subtitle)
    pdf.add_passage(ref, hebrew, english)
    pdf.add_verb_table(verbs)   # list of VerbEntry
    pdf.add_section_break()
    pdf.save(output_path)

Or use build_ch26_exercise() to regenerate the Chapter 26 exercise directly.
"""

from dataclasses import dataclass
from typing import Optional
import os

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
from bidi.algorithm import get_display

# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------
_FONTS_REGISTERED = False

def _register_fonts():
    global _FONTS_REGISTERED
    if _FONTS_REGISTERED:
        return
    pdfmetrics.registerFont(TTFont('ArialHebrew',     '/System/Library/Fonts/ArialHB.ttc', subfontIndex=2))
    pdfmetrics.registerFont(TTFont('ArialHebrewBold', '/System/Library/Fonts/ArialHB.ttc', subfontIndex=3))
    _FONTS_REGISTERED = True


def _heb(text: str) -> str:
    """Apply bidi algorithm so ReportLab draws Hebrew glyphs left-to-right."""
    return get_display(text)


# ---------------------------------------------------------------------------
# Colours
# ---------------------------------------------------------------------------
C_HEADER_BG  = HexColor('#e8e8e8')
C_ANSWER_BG  = HexColor('#f0faf0')
C_ANSWER_FG  = HexColor('#2a6e2a')
C_WATCHOUT   = HexColor('#fff8e1')
C_WATCHOUT_B = HexColor('#f0a500')
C_FIELD_BG   = HexColor('#fafff8')
C_RULE       = HexColor('#cccccc')
C_HEADING    = HexColor('#333333')
C_REF        = HexColor('#444444')
C_NOTE_BG    = HexColor('#fff8e8')
C_NOTE_B     = HexColor('#e0c060')
C_SCORE_BG   = HexColor('#f5f0ff')
C_SCORE_B    = HexColor('#c0a8e8')

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------
@dataclass
class VerbEntry:
    num: str          # "1", "B1", etc.
    verb: str         # pointed Hebrew
    conj: str         # answer
    pgn:  str         # answer
    root: str         # answer (Hebrew)
    func: str         # answer

@dataclass
class PassageBlock:
    ref:     str
    hebrew:  str
    english: str
    watchout: Optional[str] = None   # optional warning note

@dataclass
class ContrastEntry:
    num:         str   # "1", "9", etc.
    root:        str   # Hebrew root
    qal:         str   # Qal gloss (Latin)
    hiphil_form: str   # Hebrew Hiphil form
    hiphil_conj: str   # conjugation label
    ref:         str
    translation: str   # answer: English translation
    function:    str   # answer: Causative / Factitive / Declarative / Simple Action
    answer_note: str   # one-line explanation

@dataclass
class SortEntry:
    num:         str   # "1"–"24"
    heb:         str   # Hebrew form
    conj:        str   # conjugation label
    ref:         str
    gloss:       str   # contextual gloss
    function:    str   # answer: C / F / D / SA
    root:        str   # Hebrew root (unused in PDF answer; kept for reference)
    explanation: str   # one-line answer explanation

# ---------------------------------------------------------------------------
# Core PDF builder
# ---------------------------------------------------------------------------
class ExercisePDF:
    PAGE_W, PAGE_H = LETTER
    MARGIN_L = 0.75 * inch
    MARGIN_R = 0.75 * inch
    MARGIN_T = 0.85 * inch
    MARGIN_B = 0.75 * inch

    # Column widths for the parse table (proportional, sum = usable width)
    COL_RATIOS = [0.06, 0.13, 0.20, 0.10, 0.14, 0.30, 0.07]
    COL_HEADERS = ['#', 'Verb', 'Conjugation', 'PGN', 'Root', 'Function', '']

    ROW_H       = 0.30 * inch   # input row height
    ANSWER_H    = 0.26 * inch   # answer row height
    HEADER_H    = 0.22 * inch
    FIELD_PAD   = 3             # pts inside field border

    HEB_SIZE    = 13
    ENG_SIZE    = 9.5
    BODY_SIZE   = 9
    HEAD_SIZE   = 11
    SUBH_SIZE   = 9.5
    LABEL_SIZE  = 8

    def __init__(self, title: str, subtitle: str = ''):
        _register_fonts()
        self.title    = title
        self.subtitle = subtitle
        self._canvas  = None
        self._path    = None
        self._y       = 0.0
        self._page    = 0
        self._fields  = []   # (name, x, y, w, h, default_value, answer_value)
        self._field_idx = 0

    # ------------------------------------------------------------------ pages
    def _usable_w(self):
        return self.PAGE_W - self.MARGIN_L - self.MARGIN_R

    def _col_widths(self):
        w = self._usable_w()
        return [r * w for r in self.COL_RATIOS]

    def _new_page(self):
        if self._page > 0:
            self._canvas.showPage()
        self._page += 1
        self._y = self.PAGE_H - self.MARGIN_T
        self._draw_header()

    def _draw_header(self):
        c = self._canvas
        if self._page == 1:
            c.setFont('Helvetica-Bold', 14)
            c.setFillColor(C_HEADING)
            c.drawString(self.MARGIN_L, self._y, self.title)
            self._y -= 0.22 * inch
            if self.subtitle:
                c.setFont('Helvetica-Oblique', 9)
                c.setFillColor(HexColor('#666666'))
                c.drawString(self.MARGIN_L, self._y, self.subtitle)
                self._y -= 0.18 * inch
            # horizontal rule
            c.setStrokeColor(C_RULE)
            c.setLineWidth(1)
            c.line(self.MARGIN_L, self._y, self.PAGE_W - self.MARGIN_R, self._y)
            self._y -= 0.15 * inch
        else:
            c.setFont('Helvetica', 8)
            c.setFillColor(HexColor('#888888'))
            c.drawString(self.MARGIN_L, self._y, f'{self.title}  —  continued')
            c.drawRightString(self.PAGE_W - self.MARGIN_R, self._y, f'page {self._page}')
            self._y -= 0.22 * inch

    def _check_space(self, needed: float):
        if self._y - needed < self.MARGIN_B:
            self._new_page()

    # ---------------------------------------------------------------- helpers
    def _hline(self, y, color=C_RULE, width=0.5):
        self._canvas.setStrokeColor(color)
        self._canvas.setLineWidth(width)
        self._canvas.line(self.MARGIN_L, y, self.PAGE_W - self.MARGIN_R, y)

    def _wrapped_height(self, text: str, font: str, size: float, max_w: float) -> float:
        lines = simpleSplit(text, font, size, max_w)
        return len(lines) * (size + 2)

    def _draw_wrapped(self, text: str, font: str, size: float,
                       x: float, y: float, max_w: float, color=black) -> float:
        """Draw wrapped text, return new y (lower)."""
        c = self._canvas
        c.setFont(font, size)
        c.setFillColor(color)
        lines = simpleSplit(text, font, size, max_w)
        line_h = size + 2
        for line in lines:
            c.drawString(x, y, line)
            y -= line_h
        return y

    # -------------------------------------------------------- public sections
    def add_instructions(self, text: str):
        self._check_space(1.0 * inch)
        c = self._canvas
        w = self._usable_w()
        h = self._wrapped_height(text, 'Helvetica', self.BODY_SIZE, w - 0.2 * inch) + 0.2 * inch
        # box
        c.setFillColor(HexColor('#f8f8f0'))
        c.setStrokeColor(HexColor('#bbbbbb'))
        c.setLineWidth(0.5)
        c.rect(self.MARGIN_L, self._y - h, w, h, fill=1, stroke=1)
        self._y -= 0.1 * inch
        self._y = self._draw_wrapped(text, 'Helvetica', self.BODY_SIZE,
                                     self.MARGIN_L + 0.1 * inch, self._y,
                                     w - 0.2 * inch)
        self._y -= 0.15 * inch

    def add_section_heading(self, text: str):
        self._check_space(0.5 * inch)
        self._y -= 0.12 * inch
        self._canvas.setFont('Helvetica-Bold', self.HEAD_SIZE)
        self._canvas.setFillColor(C_HEADING)
        self._canvas.drawString(self.MARGIN_L, self._y, text)
        self._y -= (self.HEAD_SIZE + 4)
        self._hline(self._y + 2, color=HexColor('#aaaaaa'), width=0.75)
        self._y -= 0.08 * inch

    def add_section_break(self):
        self._check_space(0.3 * inch)
        self._y -= 0.12 * inch
        c = self._canvas
        c.setStrokeColor(HexColor('#cccccc'))
        c.setLineWidth(0.5)
        c.setDash(4, 4)
        c.line(self.MARGIN_L, self._y, self.PAGE_W - self.MARGIN_R, self._y)
        c.setDash()
        self._y -= 0.15 * inch

    def add_passage(self, block: PassageBlock):
        """Draw ref + Hebrew + English (+ optional watchout)."""
        c = self._canvas
        w = self._usable_w()

        # Estimate height needed
        heb_h = self._wrapped_height(_heb(block.hebrew), 'ArialHebrew',
                                      self.HEB_SIZE, w) + 4
        eng_h = self._wrapped_height(block.english, 'Helvetica-Oblique',
                                      self.ENG_SIZE, w) + 2
        wo_h  = 0
        if block.watchout:
            wo_h = self._wrapped_height(block.watchout, 'Helvetica',
                                         self.SUBH_SIZE, w - 0.2*inch) + 0.18*inch
        needed = 0.18*inch + heb_h + eng_h + wo_h + 0.1*inch
        self._check_space(needed)

        # Reference
        c.setFont('Helvetica-Bold', self.SUBH_SIZE)
        c.setFillColor(C_REF)
        c.drawString(self.MARGIN_L, self._y, block.ref)
        self._y -= (self.SUBH_SIZE + 3)

        # Hebrew — right-aligned RTL block
        heb_display = _heb(block.hebrew)
        lines = simpleSplit(heb_display, 'ArialHebrew', self.HEB_SIZE, w)
        line_h = self.HEB_SIZE + 4
        c.setFont('ArialHebrew', self.HEB_SIZE)
        c.setFillColor(black)
        for line in lines:
            c.drawRightString(self.MARGIN_L + w, self._y, line)
            self._y -= line_h
        self._y -= 2

        # English
        c.setFont('Helvetica-Oblique', self.ENG_SIZE)
        c.setFillColor(HexColor('#555555'))
        lines = simpleSplit(block.english, 'Helvetica-Oblique', self.ENG_SIZE, w)
        for line in lines:
            c.drawString(self.MARGIN_L, self._y, line)
            self._y -= (self.ENG_SIZE + 2)
        self._y -= 4

        # Watchout box
        if block.watchout:
            wo_lines = simpleSplit(block.watchout, 'Helvetica', self.SUBH_SIZE,
                                   w - 0.2*inch)
            box_h = len(wo_lines) * (self.SUBH_SIZE + 2) + 0.14*inch
            c.setFillColor(C_WATCHOUT)
            c.setStrokeColor(C_WATCHOUT_B)
            c.setLineWidth(2)
            c.rect(self.MARGIN_L, self._y - box_h, w, box_h, fill=1, stroke=0)
            c.setLineWidth(2)
            c.setStrokeColor(C_WATCHOUT_B)
            c.line(self.MARGIN_L, self._y - box_h,
                   self.MARGIN_L, self._y)
            self._y -= 0.07*inch
            c.setFont('Helvetica', self.SUBH_SIZE)
            c.setFillColor(black)
            for line in wo_lines:
                c.drawString(self.MARGIN_L + 0.1*inch, self._y, line)
                self._y -= (self.SUBH_SIZE + 2)
            self._y -= 0.08*inch

    def add_verb_table(self, verbs: list[VerbEntry]):
        """Draw the parse table for one or more verbs."""
        cw = self._col_widths()
        x0 = self.MARGIN_L

        # Each verb = input row + answer row; estimate total height
        needed = self.HEADER_H + len(verbs) * (self.ROW_H + self.ANSWER_H) + 0.08*inch
        self._check_space(needed)

        c = self._canvas

        # Header row
        y = self._y
        c.setFillColor(C_HEADER_BG)
        c.setStrokeColor(C_RULE)
        c.setLineWidth(0.4)
        c.rect(x0, y - self.HEADER_H, sum(cw), self.HEADER_H, fill=1, stroke=1)
        cx = x0
        c.setFont('Helvetica-Bold', self.LABEL_SIZE)
        c.setFillColor(black)
        for i, (hdr, w) in enumerate(zip(self.COL_HEADERS, cw)):
            if hdr:
                c.drawString(cx + 3, y - self.HEADER_H + 5, hdr)
            cx += w
        y -= self.HEADER_H

        for verb in verbs:
            # --- input row ---
            self._check_space(self.ROW_H + self.ANSWER_H)
            c.setStrokeColor(C_RULE)
            c.setLineWidth(0.4)
            c.rect(x0, y - self.ROW_H, sum(cw), self.ROW_H, fill=0, stroke=1)

            cx = x0
            # col 0: number
            c.setFont('Helvetica-Bold', self.LABEL_SIZE)
            c.setFillColor(HexColor('#666666'))
            c.drawCentredString(cx + cw[0]/2, y - self.ROW_H + 8, str(verb.num))
            cx += cw[0]

            # col 1: Hebrew verb (RTL)
            c.setFont('ArialHebrewBold', self.HEB_SIZE - 1)
            c.setFillColor(black)
            c.drawRightString(cx + cw[1] - 3, y - self.ROW_H + 7, _heb(verb.verb))
            cx += cw[1]

            # cols 2-5: AcroForm text fields
            field_cols = [
                (cw[2], 'conj', verb.conj),
                (cw[3], 'pgn',  verb.pgn),
                (cw[4], 'root', verb.root),
                (cw[5], 'func', verb.func),
            ]
            for (fw, fname, fanswer) in field_cols:
                fid = f'{verb.num}-{fname}-{self._field_idx}'
                self._field_idx += 1
                fx = cx + self.FIELD_PAD
                fy = y - self.ROW_H + self.FIELD_PAD
                fw2 = fw - self.FIELD_PAD * 2
                fh  = self.ROW_H - self.FIELD_PAD * 2

                # draw field background
                c.setFillColor(C_FIELD_BG)
                c.setStrokeColor(HexColor('#bbbbbb'))
                c.setLineWidth(0.5)
                c.rect(fx, fy, fw2, fh, fill=1, stroke=1)

                # AcroForm text field
                c.acroForm.textfield(
                    name=fid,
                    tooltip=f'{verb.num} {fname}',
                    x=fx, y=fy, width=fw2, height=fh,
                    borderStyle='underlined',
                    borderColor=HexColor('#bbbbbb'),
                    fillColor=C_FIELD_BG,
                    textColor=black,
                    fontSize=self.LABEL_SIZE,
                    fontName='Helvetica',
                    value='',
                    fieldFlags='',
                )
                cx += fw

            # col 6: "Ans ▼" label (static — answers shown in answer row below)
            c.setFont('Helvetica', 7)
            c.setFillColor(HexColor('#2a6e2a'))
            c.drawCentredString(cx + cw[6]/2, y - self.ROW_H + 8, 'see ↓')

            y -= self.ROW_H

            # --- answer row ---
            c.setFillColor(C_ANSWER_BG)
            c.setStrokeColor(C_RULE)
            c.setLineWidth(0.4)
            c.rect(x0, y - self.ANSWER_H, sum(cw), self.ANSWER_H, fill=1, stroke=1)

            cx = x0
            # ✓ label
            c.setFont('Helvetica-Bold', self.LABEL_SIZE)
            c.setFillColor(C_ANSWER_FG)
            c.drawCentredString(cx + cw[0]/2, y - self.ANSWER_H + 6, '✓')
            cx += cw[0]

            # Hebrew verb
            c.setFont('ArialHebrew', self.LABEL_SIZE)
            c.setFillColor(C_ANSWER_FG)
            c.drawRightString(cx + cw[1] - 3, y - self.ANSWER_H + 6, _heb(verb.verb))
            cx += cw[1]

            answers = [
                (cw[2], verb.conj, False),
                (cw[3], verb.pgn,  False),
                (cw[4], verb.root, True),   # Hebrew root
                (cw[5], verb.func, False),
            ]
            for (aw, atext, is_heb) in answers:
                if is_heb:
                    c.setFont('ArialHebrew', self.LABEL_SIZE)
                    c.drawRightString(cx + aw - 3, y - self.ANSWER_H + 6, _heb(atext))
                else:
                    c.setFont('Helvetica', self.LABEL_SIZE)
                    # truncate if too wide
                    lines = simpleSplit(atext, 'Helvetica', self.LABEL_SIZE, aw - 6)
                    c.drawString(cx + 3, y - self.ANSWER_H + 6,
                                 lines[0] if lines else atext)
                cx += aw

            y -= self.ANSWER_H

        self._y = y - 0.1 * inch

    def add_note(self, text: str):
        """Draw a note/info box."""
        c = self._canvas
        w = self._usable_w()
        h = self._wrapped_height(text, 'Helvetica', self.LABEL_SIZE,
                                  w - 0.2*inch) + 0.18*inch
        self._check_space(h + 0.1*inch)
        c.setFillColor(C_NOTE_BG)
        c.setStrokeColor(C_NOTE_B)
        c.setLineWidth(0.5)
        c.rect(self.MARGIN_L, self._y - h, w, h, fill=1, stroke=1)
        self._y -= 0.07*inch
        self._y = self._draw_wrapped(text, 'Helvetica', self.LABEL_SIZE,
                                     self.MARGIN_L + 0.1*inch, self._y,
                                     w - 0.2*inch, color=HexColor('#333333'))
        self._y -= 0.1*inch

    def add_score(self, text: str):
        c = self._canvas
        w = self._usable_w()
        h = 0.32 * inch
        self._check_space(h + 0.1*inch)
        c.setFillColor(C_SCORE_BG)
        c.setStrokeColor(C_SCORE_B)
        c.setLineWidth(0.5)
        c.rect(self.MARGIN_L, self._y - h, w, h, fill=1, stroke=1)
        self._y -= 0.09*inch
        c.setFont('Helvetica-Bold', self.BODY_SIZE)
        c.setFillColor(black)
        c.drawString(self.MARGIN_L + 0.1*inch, self._y, text)
        self._y -= (h - 0.09*inch + 0.1*inch)

    def add_coverage_table(self, rows: list[tuple[str, str]]):
        """Draw a simple 2-col coverage table."""
        c = self._canvas
        cw = [2.2*inch, self._usable_w() - 2.2*inch]
        row_h = 0.2*inch
        needed = row_h * (len(rows) + 1) + 0.2*inch
        self._check_space(needed)
        x0 = self.MARGIN_L
        y = self._y
        # header
        c.setFillColor(HexColor('#ddeeff'))
        c.setStrokeColor(C_RULE)
        c.setLineWidth(0.4)
        c.rect(x0, y - row_h, sum(cw), row_h, fill=1, stroke=1)
        c.setFont('Helvetica-Bold', self.LABEL_SIZE)
        c.setFillColor(black)
        c.drawString(x0+3, y-row_h+5, 'Conjugation')
        c.drawString(x0+cw[0]+3, y-row_h+5, 'Verbs')
        y -= row_h
        for conj, verbs in rows:
            c.setFillColor(white)
            c.setStrokeColor(C_RULE)
            c.rect(x0, y-row_h, sum(cw), row_h, fill=1, stroke=1)
            c.setFont('Helvetica', self.LABEL_SIZE)
            c.setFillColor(black)
            c.drawString(x0+3, y-row_h+5, conj)
            c.drawString(x0+cw[0]+3, y-row_h+5, verbs)
            y -= row_h
        self._y = y - 0.1*inch

    def add_contrast_table(self, entries: list['ContrastEntry']):
        """Draw a Qal-Hiphil contrast table with fillable Translation and Function columns."""
        c = self._canvas
        w = self._usable_w()
        # Columns: #, Root, Qal, Hiphil Form, Ref, Translation (field), Function (field)
        ratios = [0.05, 0.10, 0.22, 0.15, 0.10, 0.22, 0.16]
        cw = [r * w for r in ratios]
        headers = ['#', 'Root', 'Qal Meaning', 'Hiphil Form', 'Ref', 'Translation', 'Function']

        needed = self.HEADER_H + len(entries) * (self.ROW_H + self.ANSWER_H) + 0.08*inch
        self._check_space(needed)
        y = self._y
        x0 = self.MARGIN_L

        # Header
        c.setFillColor(C_HEADER_BG)
        c.setStrokeColor(C_RULE)
        c.setLineWidth(0.4)
        c.rect(x0, y - self.HEADER_H, sum(cw), self.HEADER_H, fill=1, stroke=1)
        cx = x0
        c.setFont('Helvetica-Bold', self.LABEL_SIZE)
        c.setFillColor(black)
        for hdr, col_w in zip(headers, cw):
            c.drawString(cx + 3, y - self.HEADER_H + 5, hdr)
            cx += col_w
        y -= self.HEADER_H

        for e in entries:
            self._check_space(self.ROW_H + self.ANSWER_H)
            # Input row
            c.setStrokeColor(C_RULE)
            c.setLineWidth(0.4)
            c.rect(x0, y - self.ROW_H, sum(cw), self.ROW_H, fill=0, stroke=1)
            cx = x0
            # #
            c.setFont('Helvetica-Bold', self.LABEL_SIZE)
            c.setFillColor(HexColor('#666666'))
            c.drawCentredString(cx + cw[0]/2, y - self.ROW_H + 8, e.num)
            cx += cw[0]
            # Root (Hebrew)
            c.setFont('ArialHebrewBold', self.HEB_SIZE - 2)
            c.setFillColor(black)
            c.drawRightString(cx + cw[1] - 3, y - self.ROW_H + 7, _heb(e.root))
            cx += cw[1]
            # Qal meaning
            c.setFont('Helvetica', self.LABEL_SIZE)
            c.setFillColor(black)
            lines = simpleSplit(e.qal, 'Helvetica', self.LABEL_SIZE, cw[2] - 6)
            c.drawString(cx + 3, y - self.ROW_H + 8, lines[0] if lines else e.qal)
            cx += cw[2]
            # Hiphil form (Hebrew) + conj
            c.setFont('ArialHebrew', self.HEB_SIZE - 2)
            c.drawRightString(cx + cw[3] - 3, y - self.ROW_H + 8, _heb(e.hiphil_form))
            cx += cw[3]
            # Ref
            c.setFont('Helvetica', self.LABEL_SIZE)
            c.setFillColor(HexColor('#555555'))
            c.drawString(cx + 3, y - self.ROW_H + 8, e.ref)
            cx += cw[4]
            # Translation field
            for fname, fw in [('trans', cw[5]), ('func', cw[6])]:
                fid = f'ctr-{e.num}-{fname}-{self._field_idx}'
                self._field_idx += 1
                fx = cx + self.FIELD_PAD
                fy = y - self.ROW_H + self.FIELD_PAD
                fw2 = fw - self.FIELD_PAD * 2
                fh = self.ROW_H - self.FIELD_PAD * 2
                c.setFillColor(C_FIELD_BG)
                c.setStrokeColor(HexColor('#bbbbbb'))
                c.setLineWidth(0.5)
                c.rect(fx, fy, fw2, fh, fill=1, stroke=1)
                c.acroForm.textfield(
                    name=fid, tooltip=f'{e.num} {fname}',
                    x=fx, y=fy, width=fw2, height=fh,
                    borderStyle='underlined', borderColor=HexColor('#bbbbbb'),
                    fillColor=C_FIELD_BG, textColor=black,
                    fontSize=self.LABEL_SIZE, fontName='Helvetica',
                    value='', fieldFlags='',
                )
                cx += fw
            y -= self.ROW_H

            # Answer row
            c.setFillColor(C_ANSWER_BG)
            c.setStrokeColor(C_RULE)
            c.setLineWidth(0.4)
            c.rect(x0, y - self.ANSWER_H, sum(cw), self.ANSWER_H, fill=1, stroke=1)
            cx = x0
            c.setFont('Helvetica-Bold', self.LABEL_SIZE)
            c.setFillColor(C_ANSWER_FG)
            c.drawCentredString(cx + cw[0]/2, y - self.ANSWER_H + 6, '✓')
            cx += cw[0]
            # root
            c.setFont('ArialHebrew', self.LABEL_SIZE)
            c.drawRightString(cx + cw[1] - 3, y - self.ANSWER_H + 6, _heb(e.root))
            cx += cw[1]
            # qal
            c.setFont('Helvetica', self.LABEL_SIZE)
            c.drawString(cx + 3, y - self.ANSWER_H + 6, e.qal[:28])
            cx += cw[2]
            # hiphil form
            c.setFont('ArialHebrew', self.LABEL_SIZE)
            c.drawRightString(cx + cw[3] - 3, y - self.ANSWER_H + 6, _heb(e.hiphil_form))
            cx += cw[3]
            # ref
            c.setFont('Helvetica', self.LABEL_SIZE)
            c.setFillColor(C_ANSWER_FG)
            c.drawString(cx + 3, y - self.ANSWER_H + 6, e.ref)
            cx += cw[4]
            # translation answer
            lines = simpleSplit(e.translation, 'Helvetica', self.LABEL_SIZE, cw[5] - 6)
            c.drawString(cx + 3, y - self.ANSWER_H + 6, lines[0] if lines else e.translation)
            cx += cw[5]
            # function answer
            lines = simpleSplit(e.function, 'Helvetica-Bold', self.LABEL_SIZE, cw[6] - 6)
            c.setFont('Helvetica-Bold', self.LABEL_SIZE)
            c.drawString(cx + 3, y - self.ANSWER_H + 6, lines[0] if lines else e.function)
            y -= self.ANSWER_H

        self._y = y - 0.08 * inch

    def add_sort_table(self, entries: list['SortEntry']):
        """Draw a semantic-function sorting table with a single fillable Function column."""
        c = self._canvas
        w = self._usable_w()
        # Columns: #, Hebrew, Conjugation, Ref, Gloss, Function (field)
        ratios = [0.05, 0.12, 0.18, 0.09, 0.46, 0.10]
        cw = [r * w for r in ratios]
        headers = ['#', 'Hebrew', 'Conjugation', 'Ref', 'Contextual Gloss', 'Function']

        needed = self.HEADER_H + len(entries) * (self.ROW_H + self.ANSWER_H) + 0.08*inch
        self._check_space(needed)
        y = self._y
        x0 = self.MARGIN_L

        # Header
        c.setFillColor(C_HEADER_BG)
        c.setStrokeColor(C_RULE)
        c.setLineWidth(0.4)
        c.rect(x0, y - self.HEADER_H, sum(cw), self.HEADER_H, fill=1, stroke=1)
        cx = x0
        c.setFont('Helvetica-Bold', self.LABEL_SIZE)
        c.setFillColor(black)
        for hdr, col_w in zip(headers, cw):
            c.drawString(cx + 3, y - self.HEADER_H + 5, hdr)
            cx += col_w
        y -= self.HEADER_H

        for e in entries:
            self._check_space(self.ROW_H + self.ANSWER_H)
            # Input row
            c.setStrokeColor(C_RULE)
            c.setLineWidth(0.4)
            c.rect(x0, y - self.ROW_H, sum(cw), self.ROW_H, fill=0, stroke=1)
            cx = x0
            c.setFont('Helvetica-Bold', self.LABEL_SIZE)
            c.setFillColor(HexColor('#666666'))
            c.drawCentredString(cx + cw[0]/2, y - self.ROW_H + 8, e.num)
            cx += cw[0]
            # Hebrew form
            c.setFont('ArialHebrewBold', self.HEB_SIZE - 2)
            c.setFillColor(black)
            c.drawRightString(cx + cw[1] - 3, y - self.ROW_H + 7, _heb(e.heb))
            cx += cw[1]
            # Conjugation
            c.setFont('Helvetica', self.LABEL_SIZE)
            lines = simpleSplit(e.conj, 'Helvetica', self.LABEL_SIZE, cw[2] - 6)
            c.drawString(cx + 3, y - self.ROW_H + 8, lines[0] if lines else e.conj)
            cx += cw[2]
            # Ref
            c.setFillColor(HexColor('#555555'))
            c.drawString(cx + 3, y - self.ROW_H + 8, e.ref)
            cx += cw[3]
            # Gloss
            c.setFillColor(black)
            lines = simpleSplit(e.gloss, 'Helvetica', self.LABEL_SIZE, cw[4] - 6)
            c.drawString(cx + 3, y - self.ROW_H + 8, lines[0] if lines else e.gloss)
            cx += cw[4]
            # Function field
            fid = f'sort-{e.num}-func-{self._field_idx}'
            self._field_idx += 1
            fx = cx + self.FIELD_PAD
            fy = y - self.ROW_H + self.FIELD_PAD
            fw2 = cw[5] - self.FIELD_PAD * 2
            fh = self.ROW_H - self.FIELD_PAD * 2
            c.setFillColor(C_FIELD_BG)
            c.setStrokeColor(HexColor('#bbbbbb'))
            c.setLineWidth(0.5)
            c.rect(fx, fy, fw2, fh, fill=1, stroke=1)
            c.acroForm.textfield(
                name=fid, tooltip=f'{e.num} function',
                x=fx, y=fy, width=fw2, height=fh,
                borderStyle='underlined', borderColor=HexColor('#bbbbbb'),
                fillColor=C_FIELD_BG, textColor=black,
                fontSize=self.LABEL_SIZE, fontName='Helvetica',
                value='', fieldFlags='',
            )
            y -= self.ROW_H

            # Answer row
            c.setFillColor(C_ANSWER_BG)
            c.setStrokeColor(C_RULE)
            c.setLineWidth(0.4)
            c.rect(x0, y - self.ANSWER_H, sum(cw), self.ANSWER_H, fill=1, stroke=1)
            cx = x0
            c.setFont('Helvetica-Bold', self.LABEL_SIZE)
            c.setFillColor(C_ANSWER_FG)
            c.drawCentredString(cx + cw[0]/2, y - self.ANSWER_H + 6, '✓')
            cx += cw[0]
            c.setFont('ArialHebrew', self.LABEL_SIZE)
            c.drawRightString(cx + cw[1] - 3, y - self.ANSWER_H + 6, _heb(e.heb))
            cx += cw[1]
            c.setFont('Helvetica', self.LABEL_SIZE)
            c.drawString(cx + 3, y - self.ANSWER_H + 6, e.conj[:22])
            cx += cw[2]
            c.setFillColor(C_ANSWER_FG)
            c.drawString(cx + 3, y - self.ANSWER_H + 6, e.ref)
            cx += cw[3]
            # explanation
            lines = simpleSplit(e.explanation, 'Helvetica', self.LABEL_SIZE, cw[4] - 6)
            c.setFillColor(C_ANSWER_FG)
            c.drawString(cx + 3, y - self.ANSWER_H + 6, lines[0] if lines else e.explanation)
            cx += cw[4]
            # function answer (bold)
            c.setFont('Helvetica-Bold', self.LABEL_SIZE)
            c.drawString(cx + 3, y - self.ANSWER_H + 6, e.function)
            y -= self.ANSWER_H

        self._y = y - 0.08 * inch

    def add_reflection(self, questions: list[str]):
        self._check_space(0.4*inch)
        c = self._canvas
        w = self._usable_w()
        c.setFont('Helvetica-Bold', self.HEAD_SIZE)
        c.setFillColor(C_HEADING)
        c.drawString(self.MARGIN_L, self._y, 'Reflection Questions')
        self._y -= (self.HEAD_SIZE + 6)
        for i, q in enumerate(questions, 1):
            needed = self._wrapped_height(q, 'Helvetica', self.BODY_SIZE,
                                           w - 0.3*inch) + 6
            self._check_space(needed)
            c.setFont('Helvetica-Bold', self.BODY_SIZE)
            c.setFillColor(black)
            c.drawString(self.MARGIN_L, self._y, f'{i}.')
            self._y = self._draw_wrapped(q, 'Helvetica', self.BODY_SIZE,
                                          self.MARGIN_L + 0.2*inch, self._y,
                                          w - 0.3*inch)
            self._y -= 6

    # -------------------------------------------------------- save
    def save(self, path: str):
        self._path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self._canvas = canvas.Canvas(path, pagesize=LETTER)
        self._canvas.setTitle(self.title)
        self._canvas.setAuthor('Bible Grammar Stats')
        self._canvas.setSubject('Biblical Hebrew Passage Exercise')
        self._page = 0
        self._y = 0.0
        self._field_idx = 0
        self._new_page()
        self._build()
        self._canvas.save()
        return path

    def _build(self):
        raise NotImplementedError('Subclass must implement _build()')


# ---------------------------------------------------------------------------
# Chapter 26 exercise
# ---------------------------------------------------------------------------
class Ch26Exercise(ExercisePDF):

    def _build(self):
        c = self._canvas

        self.add_instructions(
            'Every highlighted verb is a Hiphil form. For each one: (1) fill in the '
            'Conjugation, PGN, Root, and Function fields. (2) Check your answer in the '
            'green row immediately below each verb.'
        )

        # ── Passage A ────────────────────────────────────────────────────────
        self.add_section_heading('Passage A — Genesis 6:12–20')

        self.add_passage(PassageBlock(
            '6:12',
            'וַיַּרְא אֱלֹהִים אֶת־הָאָרֶץ וְהִנֵּה נִשְׁחָתָה כִּי־הִשְׁחִית כָּל־בָּשָׂר אֶת־דַּרְכּוֹ עַל־הָאָרֶץ',
            '"And God saw the earth, and behold, it was corrupt; for all flesh had [1] ____ its way upon the earth."'))
        self.add_verb_table([VerbEntry('1','הִשְׁחִית','Perfect (qatal)','3ms','שָׁחַת','Causative — had corrupted')])

        self.add_passage(PassageBlock(
            '6:13',
            'הִנְנִי מַשְׁחִיתָם עִם־הָאָרֶץ',
            '"Behold, I am [2] ____ them with the earth."'))
        self.add_verb_table([VerbEntry('2','מַשְׁחִיתָם','Participle + 3mp suffix','ms','שָׁחַת','Causative — destroying them')])

        self.add_passage(PassageBlock(
            '6:17',
            'וַאֲנִי הִנְנִי מֵבִיא אֶת־הַמַּבּוּל מַיִם עַל־הָאָרֶץ',
            '"As for me, behold, I am [3] ____ the flood of waters upon the earth."'))
        self.add_verb_table([VerbEntry('3','מֵבִיא','Participle','ms','בּוֹא','Causative — bringing')])

        self.add_passage(PassageBlock(
            '6:18',
            'וַהֲקִמֹתִי אֶת־בְּרִיתִי אִתָּךְ',
            '"But I will [4] ____ my covenant with you."'))
        self.add_verb_table([VerbEntry('4','וַהֲקִמֹתִי','Weqatal','1cs','קוּם','Factitive — I will establish')])

        self.add_passage(PassageBlock(
            '6:19',
            'מִכָּל־בָּשָׂר שְׁנַיִם מִכֹּל תָּבִיא אֶל־הַתֵּבָה',
            '"Of every living thing you shall [5] ____ two of every kind into the ark."'))
        self.add_verb_table([VerbEntry('5','תָּבִיא','Imperfect','2ms','בּוֹא','Causative — you shall bring')])

        self.add_passage(PassageBlock(
            '6:19–20',
            'לְהַחֲיֹת אִתָּךְ … לְהַחֲיוֹת',
            '"to [6] ____ them alive with you … to [7] ____ them"'))
        self.add_verb_table([
            VerbEntry('6','לְהַחֲיֹת', 'Inf. Construct','—','חָיָה','Causative — to keep alive'),
            VerbEntry('7','לְהַחֲיוֹת','Inf. Construct','—','חָיָה','Causative — to keep alive'),
        ])

        self.add_section_break()

        # ── Passage B ────────────────────────────────────────────────────────
        self.add_section_heading('Passage B — Genesis 7:4')

        self.add_passage(PassageBlock(
            '7:4',
            'כִּי לְיָמִים עוֹד שִׁבְעָה אָנֹכִי מַמְטִיר עַל־הָאָרֶץ אַרְבָּעִים יוֹם',
            '"For in seven days I will [8] ____ rain on the earth forty days."'))
        self.add_verb_table([VerbEntry('8','מַמְטִיר','Participle','ms','מָטַר','Causative/Denominative — causing rain')])

        self.add_section_break()

        # ── Passage C ────────────────────────────────────────────────────────
        self.add_section_heading('Passage C — Genesis 8:1–21')

        self.add_passage(PassageBlock('8:1','וַיַּעֲבֵר אֱלֹהִים רוּחַ עַל־הָאָרֶץ',
            '"And God [9] ____ a wind over the earth."'))
        self.add_verb_table([VerbEntry('9','וַיַּעֲבֵר','Wayyiqtol','3ms','עָבַר','Causative — caused to pass over')])

        self.add_passage(PassageBlock('8:9','וַיָּבֵא אֹתָהּ אֵלָיו אֶל־הַתֵּבָה',
            '"And he [10] ____ her back to him into the ark."'))
        self.add_verb_table([VerbEntry('10','וַיָּבֵא','Wayyiqtol','3ms','בּוֹא','Causative — brought')])

        self.add_passage(PassageBlock('8:13','וַיָּסַר נֹחַ אֶת־מִכְסֵה הַתֵּבָה',
            '"And Noah [11] ____ the covering of the ark."'))
        self.add_verb_table([VerbEntry('11','וַיָּסַר','Wayyiqtol','3ms','סוּר','Causative — removed')])

        self.add_passage(PassageBlock('8:17','הַיְצֵא אִתָּךְ כָּל־הַחַיָּה',
            '"[12] ____ with you every living thing."'))
        self.add_verb_table([VerbEntry('12','הַיְצֵא','Imperative','2ms','יָצָא','Causative — bring out!')])

        self.add_passage(PassageBlock('8:20','וַיַּעַל עֹלֹת בַּמִּזְבֵּחַ',
            '"And he [13] ____ burnt offerings on the altar."'))
        self.add_verb_table([VerbEntry('13','וַיַּעַל','Wayyiqtol','3ms','עָלָה','Causative — offered up')])

        self.add_passage(PassageBlock('8:21','לֹא־אֹסִף לְהַכֹּת אֶת־כָּל־חַי',
            '"I will never again [14] ____ every living thing."'))
        self.add_verb_table([VerbEntry('14','לְהַכֹּת','Inf. Construct','—','נָכָה','Causative — to strike down')])

        self.add_section_break()

        # ── Passage D ────────────────────────────────────────────────────────
        self.add_section_heading('Passage D — Genesis 22:17  (Infinitive Absolute)')

        self.add_passage(PassageBlock(
            '22:17',
            'כִּי בָרֵךְ אֲבָרֶכְךָ וְהַרְבָּה אַרְבֶּה אֶת־זַרְעֲךָ כְּכוֹכְבֵי הַשָּׁמַיִם',
            '"For I will surely bless you, and I will [15] ____ [16] ____ your offspring as the stars of heaven."',
            watchout='Watch out: בָּרֵךְ and אֲבָרֶכְךָ are Piel forms of בָּרַךְ ("to bless") — not Hiphil. Parse only verbs 15–16.'))
        self.add_verb_table([
            VerbEntry('15','וְהַרְבָּה','Inf. Absolute','—','רָבָה','Causative — emphatic modifier (surely/multiplying)'),
            VerbEntry('16','אַרְבֶּה',  'Imperfect',   '1cs','רָבָה','Causative — I will multiply'),
        ])

        self.add_section_break()

        # ── Passage E ────────────────────────────────────────────────────────
        self.add_section_heading('Passage E — Deuteronomy 7:2  (Weqatal + Emphatic Pair)')

        self.add_passage(PassageBlock(
            '7:2',
            'וּנְתָנָם יְהוָה אֱלֹהֶיךָ לְפָנֶיךָ וְהִכִּיתָם הַכֵּה תַכֶּה לֹא־תִכְרֹת לָהֶם בְּרִית',
            '"When the LORD your God gives them over, you shall [17] ____ them — [18] ____ [19] ____ them — make no covenant with them."',
            watchout='Watch out: וּנְתָנָם is Qal perfect of נָתַן; תִכְרֹת is Qal imperfect of כָּרַת. Parse only verbs 17–19.'))
        self.add_verb_table([
            VerbEntry('17','וְהִכִּיתָם','Weqatal',     '2ms','נָכָה','Causative — and you shall strike them'),
            VerbEntry('18','הַכֵּה',    'Inf. Absolute','—',  'נָכָה','Causative — emphatic modifier (certainly)'),
            VerbEntry('19','תַכֶּה',    'Imperfect',   '2ms','נָכָה','Causative — you shall strike'),
        ])

        self.add_section_break()

        # ── Bonus ─────────────────────────────────────────────────────────────
        self.add_section_heading('Bonus — Genesis 6:1, 6:10')

        self.add_passage(PassageBlock('6:1','כִּי־הֵחֵל הָאָדָם לָרֹב','"When man began to multiply…"'))
        self.add_passage(PassageBlock('6:10','וַיּוֹלֶד נֹחַ שְׁלֹשָׁה בָנִים','"And Noah fathered three sons."'))
        self.add_verb_table([
            VerbEntry('B1','הֵחֵל',    'Perfect (qatal)','3ms','חָלַל','Causative — began (Hiphil of חָלַל = to begin)'),
            VerbEntry('B2','וַיּוֹלֶד','Wayyiqtol',      '3ms','יָלַד','Causative — fathered / begat'),
        ])

        self.add_section_break()

        # ── Notes + Score ─────────────────────────────────────────────────────
        self.add_note(
            'Note: #1 (הִשְׁחִית) and B1 (הֵחֵל) are Perfect (qatal), not Weqatal — both follow כִּי '
            'with no waw prefix. #15–16 and #18–19 illustrate the emphatic inf. absolute + imperfect '
            'construction: the inf. absolute intensifies the finite verb ("shall certainly strike").'
        )
        self.add_score(
            'Score: 19 main + 2 bonus = 21 total.  '
            '18–21 = excellent  |  13–17 = review the paradigm  |  below 13 = revisit §26.3–26.13'
        )

        # ── Coverage table ────────────────────────────────────────────────────
        self.add_section_heading('Conjugation Coverage')
        self.add_coverage_table([
            ('Wayyiqtol (5)',      '#9, #10, #11, #13, B2'),
            ('Inf. Construct (3)', '#6, #7, #14'),
            ('Participle (3)',     '#2, #3, #8'),
            ('Imperfect (3)',      '#5, #16, #19'),
            ('Perfect / qatal (2)','#1, B1'),
            ('Weqatal (2)',        '#4, #17'),
            ('Inf. Absolute (2)',  '#15, #18'),
            ('Imperative (1)',     '#12'),
        ])

        # ── Reflection ────────────────────────────────────────────────────────
        self.add_reflection([
            'Wayyiqtol dominates in Gen 6–8 but is absent from Passages D and E. What does this tell '
            'you about how genre — narrative vs. divine oracle (Gen 22) vs. legal instruction (Deut 7) '
            '— shapes conjugation choice in the Hiphil?',
            'Both Passage D (Gen 22:17) and Passage E (Deut 7:2) use the emphatic inf. absolute + '
            'imperfect pattern. What does the inf. absolute add beyond a plain imperfect? Are the two '
            'contexts — promise and command — using the emphasis for the same rhetorical purpose?',
            'In Gen 6–8, God is the subject of nearly every Hiphil; Noah appears as subject only at '
            '#11 and #13. What does this distribution of agency tell you about the theological '
            'architecture of the flood narrative?',
        ])


# ---------------------------------------------------------------------------
# Chapter 26 — Qal–Hiphil Contrast Drill
# ---------------------------------------------------------------------------
class Ch26ContrastExercise(ExercisePDF):

    def _build(self):
        self.add_instructions(
            'For each item: (1) write an English translation of the Hiphil form in the Translation '
            'column; (2) write the semantic function (Causative / Factitive / Declarative / Simple '
            'Action) in the Function column. Check the green answer row immediately below each item.'
        )

        self.add_section_heading('Part A — Motion Verbs (Causative)')
        self.add_note('These roots describe motion in the Qal. The Hiphil makes someone else do the moving.')
        self.add_contrast_table([
            ContrastEntry('1', 'בּוֹא', 'to go in, come',   'יָּבֵא',      'Wayyiqtol 3ms', 'Gen 2:19',  'he brought (them)',          'Causative',      'God caused the animals to come to Adam'),
            ContrastEntry('2', 'יָצָא', 'to go out',        'תּוֹצֵא',     'Wayyiqtol 3fs', 'Gen 1:12',  'it brought forth',           'Causative',      'Earth caused vegetation to come out'),
            ContrastEntry('3', 'שׁוּב', 'to return',        'הֵשִׁיב',     'Weqatal 3ms',   'Gen 14:16', 'he brought back',            'Causative',      'Abraham caused Lot to return'),
            ContrastEntry('4', 'עָלָה', 'to go up',         'הַעֲלֵה',     'Imperative 2ms','Gen 22:2',  'offer up! / bring up!',      'Causative',      'Cause Isaac to go up as an offering'),
            ContrastEntry('5', 'יָרַד', 'to go down',       'תֹּרֶד',      'Wayyiqtol 3fs', 'Gen 24:18', 'she lowered (her jar)',       'Causative',      'Rebekah caused the jar to go down'),
            ContrastEntry('6', 'מוּת',  'to die',           'הָמִית',      'Inf. Constr.',  'Gen 18:25', 'to put to death / to kill',  'Causative',      'Causing someone to die'),
            ContrastEntry('7', 'יָלַד', 'to give birth',    'יּוֹלֶד',     'Wayyiqtol 3ms', 'Gen 5:3',   'he fathered / begat',        'Causative',      'Adam caused a son to be born'),
            ContrastEntry('8', 'שָׁקָה', 'to drink',        'הִשְׁקָה',    'Perfect 3ms',   'Gen 2:6',   'it watered',                 'Causative',      'Mist caused the ground to receive water'),
        ])

        self.add_section_heading('Part B — Stative Verbs (Factitive and Declarative)')
        self.add_note(
            'Factitive: the Hiphil causes an object to be in a state (make heavy, make great). '
            'Declarative: the Hiphil declares/treats something as being in that state (declare guilty).'
        )
        self.add_contrast_table([
            ContrastEntry('9',  'כָּבֵד', 'to be heavy/honored', 'יַּכְבֵּד',   'Wayyiqtol 3ms', 'Exo 8:28', 'he hardened (his heart)',         'Factitive',    'Caused heart to be in state of stubbornness'),
            ContrastEntry('10', 'גָּדַל', 'to be great',         'תַּגְדֵּל',   'Wayyiqtol 2ms', 'Gen 19:19','you have made great (your mercy)','Factitive',    'Caused kindness to be great'),
            ContrastEntry('11', 'רָשָׁע', 'to be wicked',        'הִרְשִׁיעוּ','Perfect 3cp',    'Deu 25:1', 'they condemned as guilty',        'Declarative',  'Legal verdict: declaring guilty party as guilty'),
        ])

        self.add_section_heading('Part C — Verbs with No Common Qal')
        self.add_note('Hiphil is the standard/primary form of these roots. No Qal "base" to compare against.')
        self.add_contrast_table([
            ContrastEntry('12', 'נָכָה', 'no Qal in BH', 'הַכּוֹת',      'Inf. Construct', 'Gen 4:15',  'to strike / smite',     'Simple Action', 'Hiphil is primary form; no causative layer'),
            ContrastEntry('13', 'שָׁמַד', 'no Qal in BH', 'הִשְׁמַדְתִּי','Perfect 1cs',    'Lev 26:30', 'I will destroy',         'Simple Action', 'Niphal of same root = "to be destroyed"'),
            ContrastEntry('14', 'נָגַד', 'rare Qal',      'יַּגֵּד',      'Wayyiqtol 3ms', 'Gen 9:22',  'he told / reported',    'Simple Action', 'Root idea = place before someone'),
        ])

        self.add_reflection([
            'For the motion verbs in Part A, describe the pattern in one sentence: what does the '
            'Hiphil consistently do to the Qal meaning?',
            'Which of Part B\'s three verbs is Factitive and which is Declarative? How did you decide?',
            'Does the lack of a Qal counterpart (Part C) affect how you translate the Hiphil? Why or why not?',
        ])


def build_ch26_contrast_exercise(out_dir: str = None) -> str:
    if out_dir is None:
        here = os.path.dirname(os.path.abspath(__file__))
        out_dir = os.path.join(here, '..', '..', 'output', 'lessons',
                               'hebrew', 'bbh', 'ch26', 'exercises',
                               'ch26-qal-hiphil-contrast')
    path = os.path.join(out_dir, 'ch26-qal-hiphil-contrast.pdf')
    ex = Ch26ContrastExercise(
        title='Chapter 26 — Qal–Hiphil Contrast Drill',
        subtitle='BBH Chapter 26 · Hiphil Strong Verbs',
    )
    return ex.save(path)


# ---------------------------------------------------------------------------
# Chapter 26 — Semantic Function Sorting
# ---------------------------------------------------------------------------
class Ch26FunctionSortExercise(ExercisePDF):

    def _build(self):
        self.add_instructions(
            'Classify each Hiphil verb as C (Causative), F (Factitive), D (Declarative), or '
            'SA (Simple Action). Write your answer in the Function column, then check the green '
            'answer row immediately below.'
        )

        # Reference legend
        self.add_note(
            'C = Causative (subject causes another to act/experience)  |  '
            'F = Factitive (subject causes object to be in a state)  |  '
            'D = Declarative (subject declares something as being in a state)  |  '
            'SA = Simple Action (Hiphil is the standard form; no common Qal)'
        )

        self.add_sort_table([
            SortEntry('1',  'יָּבֵא',        'Wayyiqtol 3ms',  'Gen 2:19',  '"he brought them to the man"',                     'C',  'בּוֹא',  'Qal = to come; Hiphil = cause to come'),
            SortEntry('2',  'תּוֹצֵא',       'Wayyiqtol 3fs',  'Gen 1:12',  '"the earth brought forth vegetation"',              'C',  'יָצָא',  'Qal = to go out; Hiphil = cause to come out'),
            SortEntry('3',  'הֵשִׁיב',       'Weqatal 3ms',    'Gen 14:16', '"he brought back his brother Lot"',                 'C',  'שׁוּב',  'Qal = to return; Hiphil = cause to return'),
            SortEntry('4',  'הִשְׁקָה',      'Perfect 3ms',    'Gen 2:6',   '"a mist watered the whole surface"',                'C',  'שָׁקָה', 'Qal = to drink; Hiphil = cause to drink/water'),
            SortEntry('5',  'יּוֹלֶד',       'Wayyiqtol 3ms',  'Gen 5:3',   '"Adam fathered a son"',                            'C',  'יָלַד',  'Qal = to give birth; Hiphil = cause to be born'),
            SortEntry('6',  'הַעֲלֵה',       'Imperative 2ms', 'Gen 22:2',  '"offer him as a burnt offering"',                   'C',  'עָלָה',  'Qal = to go up; Hiphil = cause to go up/offer'),
            SortEntry('7',  'תֹּרֶד',        'Wayyiqtol 3fs',  'Gen 24:18', '"she lowered her jar to give him a drink"',         'C',  'יָרַד',  'Qal = to go down; Hiphil = cause to go down'),
            SortEntry('8',  'הֵסִיר',        'Wayyiqtol 3ms',  'Gen 30:35', '"he removed the streaked goats"',                   'C',  'סוּר',   'Qal = to turn aside; Hiphil = cause to depart'),
            SortEntry('9',  'יַּגֵּד',       'Wayyiqtol 3ms',  'Gen 9:22',  '"Ham told his two brothers"',                      'SA', 'נָגַד',  'Rare Qal; Hiphil is operative form: to tell'),
            SortEntry('10', 'הִגִּיד',       'Weqatal 3ms',    'Gen 3:11',  '"who told you that you were naked?"',               'SA', 'נָגַד',  'Same root as #9; Hiphil = standard form'),
            SortEntry('11', 'תַּשְׁלֵךְ',   'Wayyiqtol 3fs',  'Gen 21:15', '"she threw the child under a bush"',                'SA', 'שָׁלַךְ','No common Qal; Hiphil = to throw/cast'),
            SortEntry('12', 'הִזְכַּרְתָּ', 'Perfect 2ms',    'Gen 40:14', '"mention me to Pharaoh"',                           'C',  'זָכַר',  'Qal = to remember; Hiphil = cause to remember'),
            SortEntry('13', 'מַזְכִּיר',    'Participle ms',  'Gen 41:9',  '"I am bringing my faults to mind"',                 'C',  'זָכַר',  'Causing something to be remembered'),
            SortEntry('14', 'הָמִית',        'Inf. Constr.',   'Gen 18:25', '"far be it from you to put…to death"',              'C',  'מוּת',   'Qal = to die; Hiphil = cause to die'),
            SortEntry('15', 'הַכּוֹת',       'Inf. Constr.',   'Gen 4:15',  '"lest anyone who found him strike him"',            'SA', 'נָכָה',  'No Qal; Hiphil = primary form: to strike'),
            SortEntry('16', 'הִשְׁמַדְתִּי', 'Perfect 1cs',   'Lev 26:30', '"I will destroy your high places"',                 'SA', 'שָׁמַד', 'No Qal; Niphal = "be destroyed"'),
            SortEntry('17', 'תַּשְׁמִידוּ', 'Imperfect 2mp',  'Num 33:52', '"you shall demolish their figured stones"',          'SA', 'שָׁמַד', 'Same root as #16; conquest context'),
            SortEntry('18', 'יַּכְבֵּד',    'Wayyiqtol 3ms',  'Exo 8:28',  '"Pharaoh hardened his heart this time also"',        'F',  'כָּבֵד', 'Qal = be heavy; Hiphil = make/cause heaviness'),
            SortEntry('19', 'הַכְבֵּד',     'Inf. Absolute',  'Exo 8:11',  '"he made his heart stubborn" (intensified)',         'F',  'כָּבֵד', 'Inf. Abs. intensifies the factitive action'),
            SortEntry('20', 'תַּגְדֵּל',    'Wayyiqtol 2ms',  'Gen 19:19', '"you have shown great kindness to me"',             'F',  'גָּדַל', 'Qal = be great; Hiphil = cause greatness'),
            SortEntry('21', 'הִרְשִׁיעוּ', 'Perfect 3cp',    'Deu 25:1',  '"acquit the innocent and condemn the guilty"',       'D',  'רָשָׁע', 'Legal verdict; declaring — not causing — guilt'),
            SortEntry('22', 'יַרְשִׁיעֻ',  'Imperfect 3mp',  'Exo 22:8',  '"the judges shall declare him guilty"',              'D',  'רָשָׁע', 'Same root; judicial pronouncement'),
            SortEntry('23', 'יַּעַל',       'Wayyiqtol 3ms',  'Gen 8:20',  '"Noah offered burnt offerings on the altar"',        'C',  'עָלָה',  'Qal = go up; Hiphil = cause to go up/offer'),
            SortEntry('24', 'הָמִית',        'Inf. Constr.',   'Gen 37:18', '"they conspired against him to kill him"',           'C',  'מוּת',   'Same form as #14; different context'),
        ])

        self.add_reflection([
            'Items 18–19 both come from the root for "be heavy" (Exo 8). How does the Hiphil meaning '
            'connect to the Qal? Is this Factitive or Causative — and why?',
            'Items 21–22 are both Declarative (not Factitive), even though רָשָׁע has a clear stative '
            'Qal. What is the difference between making someone wicked and declaring someone wicked? '
            'What makes Deu 25:1 and Exo 22:8 clearly Declarative?',
            'Items 12–13 (זָכַר, "to remember") are classified as Causative. How does "mention me to '
            'Pharaoh" (Gen 40:14) fit the Causative definition? Does that reading change the translation?',
        ])


def build_ch26_function_sort_exercise(out_dir: str = None) -> str:
    if out_dir is None:
        here = os.path.dirname(os.path.abspath(__file__))
        out_dir = os.path.join(here, '..', '..', 'output', 'lessons',
                               'hebrew', 'bbh', 'ch26', 'exercises',
                               'ch26-function-sort')
    path = os.path.join(out_dir, 'ch26-function-sort.pdf')
    ex = Ch26FunctionSortExercise(
        title='Chapter 26 — Semantic Function Sorting',
        subtitle='BBH Chapter 26 · Hiphil Strong Verbs',
    )
    return ex.save(path)


def build_ch26_exercise(out_dir: str = None) -> str:
    if out_dir is None:
        here = os.path.dirname(os.path.abspath(__file__))
        out_dir = os.path.join(here, '..', '..', 'output', 'lessons',
                               'hebrew', 'bbh', 'ch26', 'exercises',
                               'ch26-passage-exercise')
    path = os.path.join(out_dir, 'ch26-passage-exercise.pdf')
    ex = Ch26Exercise(
        title='Chapter 26 — "Spot the Hiphil" Passage Exercise',
        subtitle='Genesis 6–8  ·  Genesis 22  ·  Deuteronomy 7',
    )
    return ex.save(path)


if __name__ == '__main__':
    p1 = build_ch26_exercise()
    print(f'Saved: {p1}')
    p2 = build_ch26_contrast_exercise()
    print(f'Saved: {p2}')
    p3 = build_ch26_function_sort_exercise()
    print(f'Saved: {p3}')
