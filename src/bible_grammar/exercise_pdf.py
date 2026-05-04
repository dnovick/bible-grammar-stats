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

    def add_verb_table(self, verbs: list[VerbEntry], show_answers: bool = True):
        """Draw the parse table for one or more verbs."""
        cw = self._col_widths()
        x0 = self.MARGIN_L

        needed = self.HEADER_H + len(verbs) * (self.ROW_H + (self.ANSWER_H if show_answers else 0)) + 0.08*inch
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
            self._check_space(self.ROW_H + (self.ANSWER_H if show_answers else 0))
            # --- input row ---
            c.setStrokeColor(C_RULE)
            c.setLineWidth(0.4)
            c.rect(x0, y - self.ROW_H, sum(cw), self.ROW_H, fill=0, stroke=1)

            cx = x0
            c.setFont('Helvetica-Bold', self.LABEL_SIZE)
            c.setFillColor(HexColor('#666666'))
            c.drawCentredString(cx + cw[0]/2, y - self.ROW_H + 8, str(verb.num))
            cx += cw[0]

            c.setFont('ArialHebrewBold', self.HEB_SIZE - 1)
            c.setFillColor(black)
            c.drawRightString(cx + cw[1] - 3, y - self.ROW_H + 7, _heb(verb.verb))
            cx += cw[1]

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
                c.setFillColor(C_FIELD_BG)
                c.setStrokeColor(HexColor('#bbbbbb'))
                c.setLineWidth(0.5)
                c.rect(fx, fy, fw2, fh, fill=1, stroke=1)
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

            # col 6: hint label only when answers are inline
            if show_answers:
                c.setFont('Helvetica', 7)
                c.setFillColor(HexColor('#2a6e2a'))
                c.drawCentredString(cx + cw[6]/2, y - self.ROW_H + 8, 'see ↓')

            y -= self.ROW_H

            if show_answers:
                # --- answer row ---
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
                c.setFillColor(C_ANSWER_FG)
                c.drawRightString(cx + cw[1] - 3, y - self.ANSWER_H + 6, _heb(verb.verb))
                cx += cw[1]

                answers = [
                    (cw[2], verb.conj, False),
                    (cw[3], verb.pgn,  False),
                    (cw[4], verb.root, True),
                    (cw[5], verb.func, False),
                ]
                for (aw, atext, is_heb) in answers:
                    if is_heb:
                        c.setFont('ArialHebrew', self.LABEL_SIZE)
                        c.drawRightString(cx + aw - 3, y - self.ANSWER_H + 6, _heb(atext))
                    else:
                        c.setFont('Helvetica', self.LABEL_SIZE)
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

    def add_contrast_table(self, entries: list['ContrastEntry'], show_answers: bool = True):
        """Draw a Qal-Hiphil contrast table with fillable Translation and Function columns."""
        c = self._canvas
        w = self._usable_w()
        # Columns: #, Root, Qal, Hiphil Form, Ref, Translation (field), Function (field)
        ratios = [0.05, 0.10, 0.22, 0.15, 0.10, 0.22, 0.16]
        cw = [r * w for r in ratios]
        headers = ['#', 'Root', 'Qal Meaning', 'Hiphil Form', 'Ref', 'Translation', 'Function']

        rows_per_entry = 1 + (1 if show_answers else 0)
        needed = self.HEADER_H + len(entries) * (self.ROW_H + (self.ANSWER_H if show_answers else 0)) + 0.08*inch
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
            self._check_space(self.ROW_H + (self.ANSWER_H if show_answers else 0))
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
            # Hiphil form (Hebrew)
            c.setFont('ArialHebrew', self.HEB_SIZE - 2)
            c.drawRightString(cx + cw[3] - 3, y - self.ROW_H + 8, _heb(e.hiphil_form))
            cx += cw[3]
            # Ref
            c.setFont('Helvetica', self.LABEL_SIZE)
            c.setFillColor(HexColor('#555555'))
            c.drawString(cx + 3, y - self.ROW_H + 8, e.ref)
            cx += cw[4]
            # Translation and Function fields
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

            if show_answers:
                # Answer row immediately below
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
                c.drawRightString(cx + cw[1] - 3, y - self.ANSWER_H + 6, _heb(e.root))
                cx += cw[1]
                c.setFont('Helvetica', self.LABEL_SIZE)
                c.drawString(cx + 3, y - self.ANSWER_H + 6, e.qal[:28])
                cx += cw[2]
                c.setFont('ArialHebrew', self.LABEL_SIZE)
                c.drawRightString(cx + cw[3] - 3, y - self.ANSWER_H + 6, _heb(e.hiphil_form))
                cx += cw[3]
                c.setFont('Helvetica', self.LABEL_SIZE)
                c.setFillColor(C_ANSWER_FG)
                c.drawString(cx + 3, y - self.ANSWER_H + 6, e.ref)
                cx += cw[4]
                lines = simpleSplit(e.translation, 'Helvetica', self.LABEL_SIZE, cw[5] - 6)
                c.drawString(cx + 3, y - self.ANSWER_H + 6, lines[0] if lines else e.translation)
                cx += cw[5]
                lines = simpleSplit(e.function, 'Helvetica-Bold', self.LABEL_SIZE, cw[6] - 6)
                c.setFont('Helvetica-Bold', self.LABEL_SIZE)
                c.drawString(cx + 3, y - self.ANSWER_H + 6, lines[0] if lines else e.function)
                y -= self.ANSWER_H

        self._y = y - 0.08 * inch

    def add_answer_key_contrast(self, entries: list['ContrastEntry']):
        """Draw a compact answer key page for the contrast drill."""
        self._new_page()
        c = self._canvas
        w = self._usable_w()
        c.setFont('Helvetica-Bold', self.HEAD_SIZE)
        c.setFillColor(C_HEADING)
        c.drawString(self.MARGIN_L, self._y, 'Answer Key')
        self._y -= (self.HEAD_SIZE + 8)
        self._hline(self._y + 2, color=HexColor('#aaaaaa'), width=0.75)
        self._y -= 0.1*inch

        # Compact table: #, Root, Translation, Function, Explanation
        ratios = [0.05, 0.10, 0.25, 0.16, 0.44]
        cw = [r * w for r in ratios]
        headers = ['#', 'Root', 'Translation', 'Function', 'Explanation']
        row_h = 0.22 * inch

        c.setFillColor(C_HEADER_BG)
        c.setStrokeColor(C_RULE)
        c.setLineWidth(0.4)
        c.rect(self.MARGIN_L, self._y - self.HEADER_H, sum(cw), self.HEADER_H, fill=1, stroke=1)
        cx = self.MARGIN_L
        c.setFont('Helvetica-Bold', self.LABEL_SIZE)
        c.setFillColor(black)
        for hdr, col_w in zip(headers, cw):
            c.drawString(cx + 3, self._y - self.HEADER_H + 5, hdr)
            cx += col_w
        self._y -= self.HEADER_H

        for i, e in enumerate(entries):
            self._check_space(row_h)
            bg = C_ANSWER_BG if i % 2 == 0 else white
            c.setFillColor(bg)
            c.setStrokeColor(C_RULE)
            c.setLineWidth(0.3)
            c.rect(self.MARGIN_L, self._y - row_h, sum(cw), row_h, fill=1, stroke=1)
            cx = self.MARGIN_L
            c.setFont('Helvetica-Bold', self.LABEL_SIZE)
            c.setFillColor(C_ANSWER_FG)
            c.drawCentredString(cx + cw[0]/2, self._y - row_h + 6, e.num)
            cx += cw[0]
            c.setFont('ArialHebrew', self.LABEL_SIZE)
            c.drawRightString(cx + cw[1] - 3, self._y - row_h + 6, _heb(e.root))
            cx += cw[1]
            c.setFont('Helvetica', self.LABEL_SIZE)
            c.setFillColor(black)
            lines = simpleSplit(e.translation, 'Helvetica', self.LABEL_SIZE, cw[2] - 6)
            c.drawString(cx + 3, self._y - row_h + 6, lines[0] if lines else e.translation)
            cx += cw[2]
            c.setFont('Helvetica-Bold', self.LABEL_SIZE)
            c.setFillColor(C_ANSWER_FG)
            c.drawString(cx + 3, self._y - row_h + 6, e.function)
            cx += cw[3]
            c.setFont('Helvetica', self.LABEL_SIZE)
            c.setFillColor(HexColor('#444444'))
            lines = simpleSplit(e.answer_note, 'Helvetica', self.LABEL_SIZE, cw[4] - 6)
            c.drawString(cx + 3, self._y - row_h + 6, lines[0] if lines else e.answer_note)
            self._y -= row_h

        self._y -= 0.1 * inch

    def add_answer_key_sort(self, entries: list['SortEntry']):
        """Draw a compact answer key page for the function-sort exercise."""
        self._new_page()
        c = self._canvas
        w = self._usable_w()
        c.setFont('Helvetica-Bold', self.HEAD_SIZE)
        c.setFillColor(C_HEADING)
        c.drawString(self.MARGIN_L, self._y, 'Answer Key')
        self._y -= (self.HEAD_SIZE + 8)
        self._hline(self._y + 2, color=HexColor('#aaaaaa'), width=0.75)
        self._y -= 0.1*inch

        # Compact table: #, Hebrew, Ref, Function, Explanation
        ratios = [0.05, 0.12, 0.09, 0.10, 0.64]
        cw = [r * w for r in ratios]
        headers = ['#', 'Hebrew', 'Ref', 'Fn', 'Explanation']
        row_h = 0.20 * inch

        c.setFillColor(C_HEADER_BG)
        c.setStrokeColor(C_RULE)
        c.setLineWidth(0.4)
        c.rect(self.MARGIN_L, self._y - self.HEADER_H, sum(cw), self.HEADER_H, fill=1, stroke=1)
        cx = self.MARGIN_L
        c.setFont('Helvetica-Bold', self.LABEL_SIZE)
        c.setFillColor(black)
        for hdr, col_w in zip(headers, cw):
            c.drawString(cx + 3, self._y - self.HEADER_H + 5, hdr)
            cx += col_w
        self._y -= self.HEADER_H

        for i, e in enumerate(entries):
            self._check_space(row_h)
            bg = C_ANSWER_BG if i % 2 == 0 else white
            c.setFillColor(bg)
            c.setStrokeColor(C_RULE)
            c.setLineWidth(0.3)
            c.rect(self.MARGIN_L, self._y - row_h, sum(cw), row_h, fill=1, stroke=1)
            cx = self.MARGIN_L
            c.setFont('Helvetica-Bold', self.LABEL_SIZE)
            c.setFillColor(C_ANSWER_FG)
            c.drawCentredString(cx + cw[0]/2, self._y - row_h + 5, e.num)
            cx += cw[0]
            c.setFont('ArialHebrew', self.LABEL_SIZE)
            c.drawRightString(cx + cw[1] - 3, self._y - row_h + 5, _heb(e.heb))
            cx += cw[1]
            c.setFont('Helvetica', self.LABEL_SIZE)
            c.setFillColor(HexColor('#555555'))
            c.drawString(cx + 3, self._y - row_h + 5, e.ref)
            cx += cw[2]
            c.setFont('Helvetica-Bold', self.LABEL_SIZE)
            c.setFillColor(C_ANSWER_FG)
            c.drawCentredString(cx + cw[3]/2, self._y - row_h + 5, e.function)
            cx += cw[3]
            c.setFont('Helvetica', self.LABEL_SIZE)
            c.setFillColor(HexColor('#444444'))
            lines = simpleSplit(e.explanation, 'Helvetica', self.LABEL_SIZE, cw[4] - 6)
            c.drawString(cx + 3, self._y - row_h + 5, lines[0] if lines else e.explanation)
            self._y -= row_h

        self._y -= 0.1 * inch

    def add_sort_table(self, entries: list['SortEntry'], show_answers: bool = True):
        """Draw a semantic-function sorting table with a single fillable Function column."""
        c = self._canvas
        w = self._usable_w()
        # Columns: #, Hebrew, Conjugation, Ref, Gloss, Function (field)
        ratios = [0.05, 0.12, 0.18, 0.09, 0.46, 0.10]
        cw = [r * w for r in ratios]
        headers = ['#', 'Hebrew', 'Conjugation', 'Ref', 'Contextual Gloss', 'Function']

        needed = self.HEADER_H + len(entries) * (self.ROW_H + (self.ANSWER_H if show_answers else 0)) + 0.08*inch
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

            if show_answers:
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
                lines = simpleSplit(e.explanation, 'Helvetica', self.LABEL_SIZE, cw[4] - 6)
                c.setFillColor(C_ANSWER_FG)
                c.drawString(cx + 3, y - self.ANSWER_H + 6, lines[0] if lines else e.explanation)
                cx += cw[4]
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

    def _render_passages(self, show_answers: bool):
        """Render all passages and verb tables; called twice (questions-only, then with answers)."""

        # ── Passage A ────────────────────────────────────────────────────────
        self.add_section_heading('Passage A — Genesis 6:12–20')

        self.add_passage(PassageBlock(
            '6:12',
            'וַיַּרְא אֱלֹהִים אֶת־הָאָרֶץ וְהִנֵּה נִשְׁחָתָה כִּי־הִשְׁחִית כָּל־בָּשָׂר אֶת־דַּרְכּוֹ עַל־הָאָרֶץ',
            '"And God saw the earth, and behold, it was corrupt; for all flesh had [1] ____ its way upon the earth."'))
        self.add_verb_table([VerbEntry('1','הִשְׁחִית','Perfect (qatal)','3ms','שָׁחַת','Causative — had corrupted')], show_answers=show_answers)

        self.add_passage(PassageBlock(
            '6:13',
            'הִנְנִי מַשְׁחִיתָם עִם־הָאָרֶץ',
            '"Behold, I am [2] ____ them with the earth."'))
        self.add_verb_table([VerbEntry('2','מַשְׁחִיתָם','Participle + 3mp suffix','ms','שָׁחַת','Causative — destroying them')], show_answers=show_answers)

        self.add_passage(PassageBlock(
            '6:17',
            'וַאֲנִי הִנְנִי מֵבִיא אֶת־הַמַּבּוּל מַיִם עַל־הָאָרֶץ',
            '"As for me, behold, I am [3] ____ the flood of waters upon the earth."'))
        self.add_verb_table([VerbEntry('3','מֵבִיא','Participle','ms','בּוֹא','Causative — bringing')], show_answers=show_answers)

        self.add_passage(PassageBlock(
            '6:18',
            'וַהֲקִמֹתִי אֶת־בְּרִיתִי אִתָּךְ',
            '"But I will [4] ____ my covenant with you."'))
        self.add_verb_table([VerbEntry('4','וַהֲקִמֹתִי','Weqatal','1cs','קוּם','Factitive — I will establish')], show_answers=show_answers)

        self.add_passage(PassageBlock(
            '6:19',
            'מִכָּל־בָּשָׂר שְׁנַיִם מִכֹּל תָּבִיא אֶל־הַתֵּבָה',
            '"Of every living thing you shall [5] ____ two of every kind into the ark."'))
        self.add_verb_table([VerbEntry('5','תָּבִיא','Imperfect','2ms','בּוֹא','Causative — you shall bring')], show_answers=show_answers)

        self.add_passage(PassageBlock(
            '6:19–20',
            'לְהַחֲיֹת אִתָּךְ … לְהַחֲיוֹת',
            '"to [6] ____ them alive with you … to [7] ____ them"'))
        self.add_verb_table([
            VerbEntry('6','לְהַחֲיֹת', 'Inf. Construct','—','חָיָה','Causative — to keep alive'),
            VerbEntry('7','לְהַחֲיוֹת','Inf. Construct','—','חָיָה','Causative — to keep alive'),
        ], show_answers=show_answers)

        self.add_section_break()

        # ── Passage B ────────────────────────────────────────────────────────
        self.add_section_heading('Passage B — Genesis 7:4')

        self.add_passage(PassageBlock(
            '7:4',
            'כִּי לְיָמִים עוֹד שִׁבְעָה אָנֹכִי מַמְטִיר עַל־הָאָרֶץ אַרְבָּעִים יוֹם',
            '"For in seven days I will [8] ____ rain on the earth forty days."'))
        self.add_verb_table([VerbEntry('8','מַמְטִיר','Participle','ms','מָטַר','Causative/Denominative — causing rain')], show_answers=show_answers)

        self.add_section_break()

        # ── Passage C ────────────────────────────────────────────────────────
        self.add_section_heading('Passage C — Genesis 8:1–21')

        self.add_passage(PassageBlock('8:1','וַיַּעֲבֵר אֱלֹהִים רוּחַ עַל־הָאָרֶץ',
            '"And God [9] ____ a wind over the earth."'))
        self.add_verb_table([VerbEntry('9','וַיַּעֲבֵר','Wayyiqtol','3ms','עָבַר','Causative — caused to pass over')], show_answers=show_answers)

        self.add_passage(PassageBlock('8:9','וַיָּבֵא אֹתָהּ אֵלָיו אֶל־הַתֵּבָה',
            '"And he [10] ____ her back to him into the ark."'))
        self.add_verb_table([VerbEntry('10','וַיָּבֵא','Wayyiqtol','3ms','בּוֹא','Causative — brought')], show_answers=show_answers)

        self.add_passage(PassageBlock('8:13','וַיָּסַר נֹחַ אֶת־מִכְסֵה הַתֵּבָה',
            '"And Noah [11] ____ the covering of the ark."'))
        self.add_verb_table([VerbEntry('11','וַיָּסַר','Wayyiqtol','3ms','סוּר','Causative — removed')], show_answers=show_answers)

        self.add_passage(PassageBlock('8:17','הַיְצֵא אִתָּךְ כָּל־הַחַיָּה',
            '"[12] ____ with you every living thing."'))
        self.add_verb_table([VerbEntry('12','הַיְצֵא','Imperative','2ms','יָצָא','Causative — bring out!')], show_answers=show_answers)

        self.add_passage(PassageBlock('8:20','וַיַּעַל עֹלֹת בַּמִּזְבֵּחַ',
            '"And he [13] ____ burnt offerings on the altar."'))
        self.add_verb_table([VerbEntry('13','וַיַּעַל','Wayyiqtol','3ms','עָלָה','Causative — offered up')], show_answers=show_answers)

        self.add_passage(PassageBlock('8:21','לֹא־אֹסִף לְהַכֹּת אֶת־כָּל־חַי',
            '"I will never again [14] ____ every living thing."'))
        self.add_verb_table([VerbEntry('14','לְהַכֹּת','Inf. Construct','—','נָכָה','Causative — to strike down')], show_answers=show_answers)

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
        ], show_answers=show_answers)

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
        ], show_answers=show_answers)

        self.add_section_break()

        # ── Bonus ─────────────────────────────────────────────────────────────
        self.add_section_heading('Bonus — Genesis 6:1, 6:10')

        self.add_passage(PassageBlock('6:1','כִּי־הֵחֵל הָאָדָם לָרֹב','"When man began to multiply…"'))
        self.add_passage(PassageBlock('6:10','וַיּוֹלֶד נֹחַ שְׁלֹשָׁה בָנִים','"And Noah fathered three sons."'))
        self.add_verb_table([
            VerbEntry('B1','הֵחֵל',    'Perfect (qatal)','3ms','חָלַל','Causative — began (Hiphil of חָלַל = to begin)'),
            VerbEntry('B2','וַיּוֹלֶד','Wayyiqtol',      '3ms','יָלַד','Causative — fathered / begat'),
        ], show_answers=show_answers)

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

        # ── Reflection (only on question pages, not repeated in key) ──────────
        if not show_answers:
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

    def _build(self):
        # ── Part 1: questions only (no answers visible) ───────────────────────
        self.add_instructions(
            'Every highlighted verb is a Hiphil form. For each one, fill in the Conjugation, '
            'PGN, Root, and Function fields. The answer key begins on the page marked "Answer Key".'
        )
        self._render_passages(show_answers=False)

        # ── Part 2: answer key (passages repeated with answers visible) ───────
        self._new_page()
        c = self._canvas
        c.setFont('Helvetica-Bold', 14)
        c.setFillColor(C_HEADING)
        c.drawString(self.MARGIN_L, self._y, 'Answer Key')
        self._y -= 0.22 * inch
        c.setFont('Helvetica-Oblique', 9)
        c.setFillColor(HexColor('#666666'))
        c.drawString(self.MARGIN_L, self._y,
                     'Passages with correct answers shown in the green row below each verb.')
        self._y -= 0.18 * inch
        c.setStrokeColor(C_RULE)
        c.setLineWidth(1)
        c.line(self.MARGIN_L, self._y, self.PAGE_W - self.MARGIN_R, self._y)
        self._y -= 0.15 * inch

        self._render_passages(show_answers=True)


# ---------------------------------------------------------------------------
# Chapter 26 — Qal–Hiphil Contrast Drill
# ---------------------------------------------------------------------------
class Ch26ContrastExercise(ExercisePDF):

    _ENTRIES_A = [
        ContrastEntry('1', 'בּוֹא', 'to go in, come',   'יָּבֵא',      'Wayyiqtol 3ms', 'Gen 2:19',  'he brought (them)',          'Causative',      'God caused the animals to come to Adam'),
        ContrastEntry('2', 'יָצָא', 'to go out',        'תּוֹצֵא',     'Wayyiqtol 3fs', 'Gen 1:12',  'it brought forth',           'Causative',      'Earth caused vegetation to come out'),
        ContrastEntry('3', 'שׁוּב', 'to return',        'הֵשִׁיב',     'Weqatal 3ms',   'Gen 14:16', 'he brought back',            'Causative',      'Abraham caused Lot to return'),
        ContrastEntry('4', 'עָלָה', 'to go up',         'הַעֲלֵה',     'Imperative 2ms','Gen 22:2',  'offer up! / bring up!',      'Causative',      'Cause Isaac to go up as an offering'),
        ContrastEntry('5', 'יָרַד', 'to go down',       'תֹּרֶד',      'Wayyiqtol 3fs', 'Gen 24:18', 'she lowered (her jar)',       'Causative',      'Rebekah caused the jar to go down'),
        ContrastEntry('6', 'מוּת',  'to die',           'הָמִית',      'Inf. Constr.',  'Gen 18:25', 'to put to death / to kill',  'Causative',      'Causing someone to die'),
        ContrastEntry('7', 'יָלַד', 'to give birth',    'יּוֹלֶד',     'Wayyiqtol 3ms', 'Gen 5:3',   'he fathered / begat',        'Causative',      'Adam caused a son to be born'),
        ContrastEntry('8', 'שָׁקָה', 'to drink',        'הִשְׁקָה',    'Perfect 3ms',   'Gen 2:6',   'it watered',                 'Causative',      'Mist caused the ground to receive water'),
    ]
    _ENTRIES_B = [
        ContrastEntry('9',  'כָּבֵד', 'to be heavy/honored', 'יַּכְבֵּד',   'Wayyiqtol 3ms', 'Exo 8:28', 'he hardened (his heart)',         'Factitive',   'Caused heart to be in state of stubbornness'),
        ContrastEntry('10', 'גָּדַל', 'to be great',         'תַּגְדֵּל',   'Wayyiqtol 2ms', 'Gen 19:19','you have made great (your mercy)', 'Factitive',   'Caused kindness to be great'),
        ContrastEntry('11', 'רָשָׁע', 'to be wicked',        'הִרְשִׁיעוּ','Perfect 3cp',    'Deu 25:1', 'they condemned as guilty',         'Declarative', 'Legal verdict: declaring guilty party as guilty'),
    ]
    _ENTRIES_C = [
        ContrastEntry('12', 'נָכָה', 'no Qal in BH', 'הַכּוֹת',      'Inf. Construct', 'Gen 4:15',  'to strike / smite',  'Simple Action', 'Hiphil is primary form; no causative layer'),
        ContrastEntry('13', 'שָׁמַד', 'no Qal in BH', 'הִשְׁמַדְתִּי','Perfect 1cs',    'Lev 26:30', 'I will destroy',      'Simple Action', 'Niphal of same root = "to be destroyed"'),
        ContrastEntry('14', 'נָגַד', 'rare Qal',      'יַּגֵּד',      'Wayyiqtol 3ms', 'Gen 9:22',  'he told / reported', 'Simple Action', 'Root idea = place before someone'),
    ]

    def _build(self):
        self.add_instructions(
            'For each item: (1) write an English translation of the Hiphil form in the Translation '
            'column; (2) write the semantic function (Causative / Factitive / Declarative / Simple '
            'Action) in the Function column. Answer key is on the last page.'
        )

        self.add_section_heading('Part A — Motion Verbs (Causative)')
        self.add_note('These roots describe motion in the Qal. The Hiphil makes someone else do the moving.')
        self.add_contrast_table(self._ENTRIES_A, show_answers=False)

        self.add_section_heading('Part B — Stative Verbs (Factitive and Declarative)')
        self.add_note(
            'Factitive: the Hiphil causes an object to be in a state (make heavy, make great). '
            'Declarative: the Hiphil declares/treats something as being in that state (declare guilty).'
        )
        self.add_contrast_table(self._ENTRIES_B, show_answers=False)

        self.add_section_heading('Part C — Verbs with No Common Qal')
        self.add_note('Hiphil is the standard/primary form of these roots. No Qal "base" to compare against.')
        self.add_contrast_table(self._ENTRIES_C, show_answers=False)

        self.add_reflection([
            'For the motion verbs in Part A, describe the pattern in one sentence: what does the '
            'Hiphil consistently do to the Qal meaning?',
            'Which of Part B\'s three verbs is Factitive and which is Declarative? How did you decide?',
            'Does the lack of a Qal counterpart (Part C) affect how you translate the Hiphil? Why or why not?',
        ])

        self.add_answer_key_contrast(self._ENTRIES_A + self._ENTRIES_B + self._ENTRIES_C)


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

    _ENTRIES = [
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
        SortEntry('25', 'מַמְטִיר',    'Participle ms',  'Gen 7:4',   '"I am about to send rain on the earth"',             'DN', 'מָטַר',  'Noun: מָטָר (rain); Hiphil = to cause rain / send rain'),
        SortEntry('26', 'יַּשְׁכֵּם', 'Wayyiqtol 3ms',  'Gen 22:3',  '"Abraham rose early in the morning"',               'DN', 'שָׁכַם', 'Noun: שְׁכֶם (shoulder); to shoulder up = rise early'),
        SortEntry('27', 'הַאְזִינוּ', 'Imperative 2mp', 'Deu 32:1',  '"give ear, O heavens, and I will speak"',           'DN', 'אָזַן',  'Noun: אֹזֶן (ear); to ear = give ear / listen'),
    ]

    def _build(self):
        self.add_instructions(
            'Classify each Hiphil verb as C (Causative), F (Factitive), D (Declarative), '
            'SA (Simple Action), or DN (Denominative). Write your answer in the Function column. '
            'Answer key is on the last page.'
        )

        self.add_note(
            'C = Causative (subject causes another to act/experience)  |  '
            'F = Factitive (subject causes object to be in a state)  |  '
            'D = Declarative (subject declares something as being in a state)  |  '
            'SA = Simple Action (Hiphil is the standard form; no common Qal)  |  '
            'DN = Denominative (Hiphil derived from a noun; not in BBH)'
        )

        self.add_sort_table(self._ENTRIES, show_answers=False)

        self.add_reflection([
            'Items 18–19 both come from the root for "be heavy" (Exo 8). How does the Hiphil meaning '
            'connect to the Qal? Is this Factitive or Causative — and why?',
            'Items 21–22 are both Declarative (not Factitive), even though רָשָׁע has a clear stative '
            'Qal. What is the difference between making someone wicked and declaring someone wicked? '
            'What makes Deu 25:1 and Exo 22:8 clearly Declarative?',
            'Items 12–13 (זָכַר, "to remember") are classified as Causative. How does "mention me to '
            'Pharaoh" (Gen 40:14) fit the Causative definition? Does that reading change the translation?',
        ])

        self.add_answer_key_sort(self._ENTRIES)


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


# ---------------------------------------------------------------------------
# Chapter 25 — "Spot the Niphal" Passage Exercise
# ---------------------------------------------------------------------------
class Ch25Exercise(ExercisePDF):

    def _render_passages(self, show_answers: bool):

        # ── Passage A ─────────────────────────────────────────────────────────
        self.add_section_heading('Passage A — Genesis 3:5–10')

        self.add_passage(PassageBlock('3:5',
            'וִֽהְיִיתֶם֙ כֵּֽאלֹהִ֔ים יֹדְעֵ֖י טוֹב וָרָ֑ע כִּ֣י יֹדֵ֔עַ אֱלֹהִ֕ים כִּ֗י בְּיֹ֛ום אֲכָלְכֶ֥ם מִמֶּ֖נּוּ וְנִפְקְח֖וּ עֵינֵיכֶ֑ם',
            '"…for God knows that in the day you eat of it your eyes will [1] ____."'))
        self.add_verb_table([VerbEntry('1','וְנִפְקְחוּ','Weqatal','3cp','פָּקַח','Middle — will be opened')], show_answers=show_answers)

        self.add_passage(PassageBlock('3:6',
            'וְנֶחְמָ֤ד הָעֵץ֙ לְהַשְׂכִּ֔יל',
            '"…and that the tree was desirable to make one wise."'))
        self.add_verb_table([VerbEntry('2','וְנֶחְמָד','Participle ms','ms','חָמַד','Passive — desirable (substantival ptc.)')], show_answers=show_answers)

        self.add_passage(PassageBlock('3:7',
            'וַתִּפָּקַ֙חְנָה֙ עֵינֵ֣י שְׁנֵיהֶ֔ם',
            '"Then the eyes of both of them [3] ____."'))
        self.add_verb_table([VerbEntry('3','וַתִּפָּקַחְנָה','Wayyiqtol','3fp','פָּקַח','Middle — they were opened')], show_answers=show_answers)

        self.add_passage(PassageBlock('3:10',
            'וָאִירָ֛א כִּֽי־עֵירֹ֥ם אָנֹ֖כִי וָאֵחָבֵֽא',
            '"I was afraid, because I was naked, and [4] ____."'))
        self.add_verb_table([VerbEntry('4','וָאֵחָבֵא','Wayyiqtol','1cs','חָבָא','Reflexive — I hid myself')], show_answers=show_answers)

        self.add_section_break()

        # ── Passage B ─────────────────────────────────────────────────────────
        self.add_section_heading('Passage B — Genesis 6:6–12')

        self.add_passage(PassageBlock('6:6',
            'וַיִּנָּ֣חֶם יְהוָ֔ה כִּֽי־עָשָׂ֥ה אֶת־הָאָדָ֖ם בָּאָ֑רֶץ',
            '"And the LORD [5] ____ that he had made man on the earth."'))
        self.add_verb_table([VerbEntry('5','וַיִּנָּחֶם','Wayyiqtol','3ms','נָחַם','Simple Action (Niphal-only) — relented')], show_answers=show_answers)

        self.add_passage(PassageBlock('6:7',
            'נִחַ֖מְתִּי כִּ֥י עֲשִׂיתִֽם',
            '"I [6] ____ that I made them."'))
        self.add_verb_table([VerbEntry('6','נִחַמְתִּי','Weqatal','1cs','נָחַם','Simple Action (Niphal-only) — I regret')], show_answers=show_answers)

        self.add_passage(PassageBlock('6:11',
            'וַתִּשָּׁחֵ֥ת הָאָ֖רֶץ … וַתִּמָּלֵ֥א הָאָ֖רֶץ חָמָֽס',
            '"The earth [7] ____ … and the earth [8] ____ with violence."'))
        self.add_verb_table([
            VerbEntry('7','וַתִּשָּׁחֵת','Wayyiqtol','3fs','שָׁחַת','Passive — it was corrupted'),
            VerbEntry('8','וַתִּמָּלֵא','Wayyiqtol','3fs','מָלֵא','Passive — it was filled'),
        ], show_answers=show_answers)

        self.add_passage(PassageBlock('6:12',
            'וְהִנֵּ֥ה נִשְׁחָ֑תָה כִּֽי־הִשְׁחִ֧ית כָּל־בָּשָׂ֛ר',
            '"and behold, it [9] ____, for all flesh had corrupted its way."'))
        self.add_verb_table([VerbEntry('9','נִשְׁחָתָה','Weqatal','3fs','שָׁחַת','Passive — it was corrupt')], show_answers=show_answers)

        self.add_passage(PassageBlock('6:21',
            'וְהָיָ֥ה לְךָ֖ וְלָהֶ֥ם לְאָכְלָֽה יֵֽאָכֵ֔ל',
            '"it shall be food for you and for them — it shall [10] ____."'))
        self.add_verb_table([VerbEntry('10','יֵאָכֵל','Imperfect','3ms','אָכַל','Passive — it shall be eaten')], show_answers=show_answers)

        self.add_section_break()

        # ── Passage C ─────────────────────────────────────────────────────────
        self.add_section_heading('Passage C — Genesis 21:23–31')

        self.add_passage(PassageBlock('21:23',
            'הִשָּׁ֨בְעָ֜ה לִּ֗י בֵּאלֹהִ֛ים הֵ֖נָּה',
            '"[11] ____ to me by God here."'))
        self.add_verb_table([VerbEntry('11','הִשָּׁבְעָה','Imperative','2ms','שָׁבַע','Reflexive — Swear! (bind yourself by oath)')], show_answers=show_answers)

        self.add_passage(PassageBlock('21:24',
            'וַיֹּ֙אמֶר֙ אַבְרָהָ֔ם אָנֹכִ֖י אִשָּׁבֵֽעַ',
            '"And Abraham said, \'I [12] ____.\'"'))
        self.add_verb_table([VerbEntry('12','אִשָּׁבֵעַ','Imperfect','1cs','שָׁבַע','Reflexive — I will swear')], show_answers=show_answers)

        self.add_passage(PassageBlock('21:31',
            'כִּ֛י שָׁ֥ם נִשְׁבְּע֖וּ שְׁנֵיהֶֽם',
            '"For there [13] ____ both of them."'))
        self.add_verb_table([VerbEntry('13','נִשְׁבְּעוּ','Weqatal','3mp','שָׁבַע','Reflexive — they swore (bound themselves by oath)')], show_answers=show_answers)

        self.add_section_break()

        # ── Bonus ─────────────────────────────────────────────────────────────
        self.add_section_heading('Bonus — Genesis 21:3, 21:8')

        self.add_passage(PassageBlock('21:3', 'אֲשֶׁר־נּֽוֹלַד־לֹ֛ו', '"who had been born to him"'))
        self.add_passage(PassageBlock('21:8', 'וַיִּגְדַּ֤ל הַיֶּ֙לֶד֙ וַיִּגָּמַ֑ל', '"And the child grew and was weaned."'))
        self.add_verb_table([
            VerbEntry('B1','נּוֹלַד',  'Weqatal',   '3ms','יָלַד','Passive — who had been born'),
            VerbEntry('B2','וַיִּגָּמַל','Wayyiqtol','3ms','גָּמַל','Passive — was weaned'),
        ], show_answers=show_answers)

        self.add_section_break()

        self.add_note(
            'Items 5–6 (וַיִּנָּחֶם / נִחַמְתִּי) are both from נָחַם, a verb that occurs almost exclusively '
            'in the Niphal. Items 11–13 all parse as Reflexive from שָׁבַע — '
            'notice how Imperative, Imperfect, and Weqatal all express the same oath-swearing action.'
        )
        self.add_score(
            'Score: 13 main + 2 bonus = 15 total.  '
            '13–15 = excellent  |  9–12 = review the paradigm  |  below 9 = revisit §23.3–23.13'
        )

        self.add_section_heading('Conjugation Coverage')
        self.add_coverage_table([
            ('Wayyiqtol (5)', '#3, #5, #7, #8, B2'),
            ('Weqatal (5)',   '#1, #6, #9, #13, B1'),
            ('Imperfect (2)', '#10, #12'),
            ('Participle (1)','#2'),
            ('Imperative (1)','#11'),
        ])

        if not show_answers:
            self.add_reflection([
                'Every Niphal in Passage A (Gen 3) involves eyes, hiding, or desire. What does the '
                'Niphal contribute to the theological message of the Fall narrative?',
                'In Gen 6:6–7, God is the subject of a Niphal-only verb (נָחַם). What does this choice '
                'tell us about how the narrator portrays God\'s emotional response?',
                'Compare Gen 3:5 (וְנִפְקְחוּ — "will be opened," Middle/Tolerative) with Gen 3:7 '
                '(וַתִּפָּקַחְנָה — "were opened," Middle). Is the function identical in both? '
                'What difference in nuance, if any, does the shift from weqatal to wayyiqtol suggest?',
            ])

    def _build(self):
        self.add_instructions(
            'Every highlighted verb is a Niphal form. For each one: '
            '(1) parse conjugation, PGN, and root; '
            '(2) state the semantic function (Passive / Reflexive / Middle / Simple Action). '
            'Answer key begins on the page marked "Answer Key".'
        )
        self._render_passages(show_answers=False)

        self._new_page()
        c = self._canvas
        c.setFont('Helvetica-Bold', 14)
        c.setFillColor(C_HEADING)
        c.drawString(self.MARGIN_L, self._y, 'Answer Key')
        self._y -= 0.22 * inch
        c.setFont('Helvetica-Oblique', 9)
        c.setFillColor(HexColor('#666666'))
        c.drawString(self.MARGIN_L, self._y,
                     'Passages with correct answers shown in the green row below each verb.')
        self._y -= 0.18 * inch
        c.setStrokeColor(C_RULE)
        c.setLineWidth(1)
        c.line(self.MARGIN_L, self._y, self.PAGE_W - self.MARGIN_R, self._y)
        self._y -= 0.15 * inch
        self._render_passages(show_answers=True)


def build_ch25_exercise(out_dir: str = None) -> str:
    if out_dir is None:
        here = os.path.dirname(os.path.abspath(__file__))
        out_dir = os.path.join(here, '..', '..', 'output', 'lessons',
                               'hebrew', 'bbh', 'ch25', 'exercises',
                               'ch25-passage-exercise')
    path = os.path.join(out_dir, 'ch25-passage-exercise.pdf')
    ex = Ch25Exercise(
        title='Chapter 25 — "Spot the Niphal" Passage Exercise',
        subtitle='Genesis 3, 6, and 21  ·  The Garden, the Flood Prelude, and Beersheba',
    )
    return ex.save(path)


# ---------------------------------------------------------------------------
# Chapter 24 — "Spot the Niphal" Passage Exercise
# ---------------------------------------------------------------------------
class Ch24Exercise(ExercisePDF):

    def _render_passages(self, show_answers: bool):

        # ── Passage A ─────────────────────────────────────────────────────────
        self.add_section_heading('Passage A — Genesis 37:7, 36')

        self.add_passage(PassageBlock('37:7',
            'וְהִנֵּה קָמָה אֲלֻמָּתִי וְגַם נִצָּבָה',
            '"and behold, my sheaf arose and [1] ____."'))
        self.add_verb_table([VerbEntry('1','נִצָּבָה','Perfect','3fs','נָצַב','Reflexive — it stood upright (stationed itself)')], show_answers=show_answers)

        self.add_passage(PassageBlock('37:36',
            'וְהַמְּדָנִים מָכְרוּ אֹתוֹ … וַיִּמָּכֵר יוֹסֵף אֶל־מִצְרָיִם',
            '"Now the Midianites had sold him … and Joseph [2] ____ into Egypt."'))
        self.add_verb_table([VerbEntry('2','וַיִּמָּכֵר','Wayyiqtol','3ms','מָכַר','Passive — he was sold')], show_answers=show_answers)

        self.add_section_break()

        # ── Passage B ─────────────────────────────────────────────────────────
        self.add_section_heading('Passage B — Genesis 44:9–20')

        self.add_passage(PassageBlock('44:9',
            'אֲשֶׁר יִמָּצֵא אִתּוֹ מֵעֲבָדֶיךָ וָמֵת',
            '"With whichever of your servants [3] ____ [the cup] shall die."'))
        self.add_verb_table([VerbEntry('3','יִמָּצֵא','Imperfect','3ms','מָצָא','Passive — is found')], show_answers=show_answers)

        self.add_passage(PassageBlock('44:12',
            'וַיִּמָּצֵא הַגָּבִיעַ בְּאַמְתַּחַת בִּנְיָמִן',
            '"And the cup [4] ____ in Benjamin\'s sack."'))
        self.add_verb_table([VerbEntry('4','וַיִּמָּצֵא','Wayyiqtol','3ms','מָצָא','Passive — was found')], show_answers=show_answers)

        self.add_passage(PassageBlock('44:20',
            'יֶשׁ לָנוּ אָב זָקֵן וְיֶלֶד זְקֻנִים קָטָן וְאָחִיו מֵת וַיִּוָּתֵר הוּא',
            '"We have an aged father … his brother is dead, and he alone [5] ____."'))
        self.add_verb_table([VerbEntry('5','וַיִּוָּתֵר','Wayyiqtol','3ms','יָתַר','Passive/Middle — was left, remained')], show_answers=show_answers)

        self.add_section_break()

        # ── Passage C ─────────────────────────────────────────────────────────
        self.add_section_heading('Passage C — Genesis 45:1, 16')

        self.add_passage(PassageBlock('45:1',
            'וְלֹא־יָכֹל יוֹסֵף לְהִתְאַפֵּק לְכֹל הַנִּצָּבִים עָלָיו',
            '"Joseph could no longer control himself before all those [6] ____ near him."'))
        self.add_verb_table([VerbEntry('6','הַנִּצָּבִים','Participle','mp','נָצַב','Reflexive — those standing (stationed themselves)')], show_answers=show_answers)

        self.add_passage(PassageBlock('45:16',
            'וְהַקֹּל נִשְׁמַע בֵּית פַּרְעֹה לֵאמֹר בָּאוּ אֲחֵי־יוֹסֵף',
            '"And the report [7] ____ in Pharaoh\'s household, \'Joseph\'s brothers have come.\'"'))
        self.add_verb_table([VerbEntry('7','נִשְׁמַע','Perfect','3ms','שָׁמַע','Passive — was heard')], show_answers=show_answers)

        self.add_section_break()

        # ── Passage D ─────────────────────────────────────────────────────────
        self.add_section_heading('Passage D — Genesis 47:14, 31')

        self.add_passage(PassageBlock('47:14',
            'וַיְלַקֵּט יוֹסֵף אֶת־כָּל־הַכֶּסֶף הַנִּמְצָא בְאֶרֶץ־מִצְרַיִם',
            '"And Joseph collected all the silver [8] ____ in the land of Egypt."'))
        self.add_verb_table([VerbEntry('8','הַנִּמְצָא','Participle','ms','מָצָא','Passive — that was found')], show_answers=show_answers)

        self.add_passage(PassageBlock('47:31',
            'הִשָּׁבְעָה לִי וַיִּשָּׁבַע לוֹ',
            '"[9] ____ to me." And he [10] ____ to him."'))
        self.add_verb_table([
            VerbEntry('9', 'הִשָּׁבְעָה','Imperative','2ms','שָׁבַע','Reflexive — swear! (bind yourself by oath)'),
            VerbEntry('10','וַיִּשָּׁבַע','Wayyiqtol', '3ms','שָׁבַע','Reflexive — he swore (bound himself by oath)'),
        ], show_answers=show_answers)

        self.add_section_break()

        # ── Passage E ─────────────────────────────────────────────────────────
        self.add_section_heading('Passage E — Genesis 49:1, 29, 33')

        self.add_passage(PassageBlock('49:1',
            'הֵאָסְפוּ וְאַגִּידָה לָכֶם',
            '"[11] ____ and I will tell you."'))
        self.add_verb_table([VerbEntry('11','הֵאָסְפוּ','Imperative','2mp','אָסַף','Passive — gather yourselves!')], show_answers=show_answers)

        self.add_passage(PassageBlock('49:29',
            'אֲנִי נֶאֱסָף אֶל־עַמִּי',
            '"I am [12] ____ to my people."'))
        self.add_verb_table([VerbEntry('12','נֶאֱסָף','Participle','ms','אָסַף','Passive — am about to be gathered (die)')], show_answers=show_answers)

        self.add_passage(PassageBlock('49:33',
            'וַיֵּאָסֶף אֶל־עַמָּיו',
            '"and he was [13] ____ to his people."'))
        self.add_verb_table([VerbEntry('13','וַיֵּאָסֶף','Wayyiqtol','3ms','אָסַף','Passive — was gathered (died)')], show_answers=show_answers)

        self.add_section_break()

        # ── Bonus ─────────────────────────────────────────────────────────────
        self.add_section_heading('Bonus — Exodus 19:12')

        self.add_passage(PassageBlock('19:12',
            'וְהִשָּׁמַרְתֶּם … הִשָּׁמְרוּ לָכֶם',
            '"And you shall [B1] ____ … [B2] ____ for yourselves."'))
        self.add_verb_table([
            VerbEntry('B1','וְהִשָּׁמַרְתֶּם','Weqatal',   '2mp','שָׁמַר','Reflexive — take heed for yourselves'),
            VerbEntry('B2','הִשָּׁמְרוּ',      'Imperative','2mp','שָׁמַר','Reflexive — take heed! (guard yourselves)'),
        ], show_answers=show_answers)

        self.add_section_break()

        self.add_note(
            'Items 12–13 (נֶאֱסָף / וַיֵּאָסֶף) are both from אָסַף — the euphemism "gathered to '
            'one\'s people" means death. Items 9–10 both parse as Reflexive from שָׁבַע — '
            'notice Imperative followed by Wayyiqtol in the same verse (Gen 47:31).'
        )
        self.add_score(
            'Score: 13 main + 2 bonus = 15 total.  '
            '13–15 = excellent  |  9–12 = review the paradigm  |  below 9 = revisit §24.3–24.13'
        )

        self.add_section_heading('Conjugation Coverage')
        self.add_coverage_table([
            ('Wayyiqtol (5)',  '#2, #4, #5, #10, #13'),
            ('Participle (3)', '#6, #8, #12'),
            ('Imperfect (1)',  '#3'),
            ('Perfect (2)',    '#1, #7'),
            ('Imperative (3)', '#9, #11, B2'),
            ('Weqatal (1)',    'B1'),
        ])

        if not show_answers:
            self.add_reflection([
                'Several Niphal forms of אָסַף in this passage describe Jacob\'s death (Gen 49:29, 33). '
                'What does the passive "to be gathered to one\'s people" suggest about ancient Israelite '
                'views of death?',
                'In Gen 47:31, both הִשָּׁ֣בְעָה (imperative) and וַיִּשָּׁבַע (wayyiqtol) appear together. '
                'How does the narrative sequence reinforce the solemnity of Jacob\'s deathbed request?',
                'Compare נִצָּבָה in Gen 37:7 (Reflexive — sheaf stands itself upright) with הַנִּצָּבִים '
                'in Gen 45:1 (Reflexive participle — servants stationed before Joseph). Is the reflexive '
                'force the same in both? What does each communicate about agency?',
            ])

    def _build(self):
        self.add_instructions(
            'Every highlighted verb is a Niphal form. For each one: '
            '(1) parse conjugation, PGN, and root; '
            '(2) state the semantic function (Passive / Reflexive / Simple Action). '
            'Answer key begins on the page marked "Answer Key".'
        )
        self._render_passages(show_answers=False)

        self._new_page()
        c = self._canvas
        c.setFont('Helvetica-Bold', 14)
        c.setFillColor(C_HEADING)
        c.drawString(self.MARGIN_L, self._y, 'Answer Key')
        self._y -= 0.22 * inch
        c.setFont('Helvetica-Oblique', 9)
        c.setFillColor(HexColor('#666666'))
        c.drawString(self.MARGIN_L, self._y,
                     'Passages with correct answers shown in the green row below each verb.')
        self._y -= 0.18 * inch
        c.setStrokeColor(C_RULE)
        c.setLineWidth(1)
        c.line(self.MARGIN_L, self._y, self.PAGE_W - self.MARGIN_R, self._y)
        self._y -= 0.15 * inch
        self._render_passages(show_answers=True)


def build_ch24_exercise(out_dir: str = None) -> str:
    if out_dir is None:
        here = os.path.dirname(os.path.abspath(__file__))
        out_dir = os.path.join(here, '..', '..', 'output', 'lessons',
                               'hebrew', 'bbh', 'ch24', 'exercises',
                               'ch24-passage-exercise')
    path = os.path.join(out_dir, 'ch24-passage-exercise.pdf')
    ex = Ch24Exercise(
        title='Chapter 24 — "Spot the Niphal" Passage Exercise',
        subtitle='Genesis 37, 44, 45, 47, 49  ·  The Joseph Narrative',
    )
    return ex.save(path)


# ---------------------------------------------------------------------------
# Chapter 24 — Qal–Niphal Contrast Drill
# ---------------------------------------------------------------------------
class Ch24ContrastExercise(ExercisePDF):

    _ENTRIES_A = [
        ContrastEntry('1',  'מָכַר', 'to sell',            'וַיִּמָּכֵר',      'Wayyiqtol 3ms',  'Gen 37:36', 'he was sold into Egypt',         'Passive',       'The object of selling (Joseph) becomes the subject'),
        ContrastEntry('2',  'מָצָא', 'to find',            'יִמָּצֵא',         'Imperfect 3ms',  'Gen 44:9',  'is found (with the cup)',         'Passive',       'The thing found becomes the subject; finder absent'),
        ContrastEntry('3',  'שָׁמַע', 'to hear',           'נִשְׁמַע',         'Perfect 3ms',    'Gen 45:16', 'was heard (in Pharaoh\'s house)', 'Passive',       'The report receives the hearing — it becomes audible'),
        ContrastEntry('4',  'אָסַף', 'to gather',          'וַיֵּאָסֶף',       'Wayyiqtol 3ms',  'Gen 49:33', 'was gathered to his people',      'Passive',       'Jacob receives the action of being gathered in (die)'),
        ContrastEntry('5',  'כָּרַת', 'to cut off',        'וְנִכְרְתָה',      'Weqatal 3fs',    'Exo 12:15', 'will be cut off from Israel',     'Passive',       'The person receives covenant-exclusion penalty'),
        ContrastEntry('6',  'נָתַן', 'to give',            'נִתְּנוּ',         'Perfect 3mp',    'Gen 9:2',   'they are given into your hand',   'Passive',       'Animals receive the action of being given/placed'),
        ContrastEntry('7',  'אָכַל', 'to eat',             'יֵאָכֵל',          'Imperfect 3ms',  'Exo 12:46', 'it shall be eaten',               'Passive',       'Passover lamb receives the action of eating'),
        ContrastEntry('8',  'שָׁמַר', 'to keep / guard',  'הִשָּׁמְרוּ',      'Imperative 2mp', 'Exo 19:12', 'take heed for yourselves!',       'Reflexive',     'Guard yourself — subject directs action back on itself'),
    ]
    _ENTRIES_B = [
        ContrastEntry('9',  'נָצַב', 'to be stationed',    'נִצָּבָה',         'Perfect 3fs',    'Gen 37:7',  'it stood upright',                'Reflexive',     'The sheaf stations itself in the standing position'),
        ContrastEntry('10', 'יָתַר', 'to remain',          'וַיִּוָּתֵר',      'Wayyiqtol 3ms',  'Gen 44:20', 'he alone was left',               'Passive/Middle','State of being-left fell upon him; middle nuance'),
        ContrastEntry('11', 'שָׁאַר', 'to remain',         'נִשְׁאַר',         'Perfect 3ms',    'Exo 14:28', 'not one of them remained',        'Middle',        'Soldiers were in the state of having been left'),
    ]
    _ENTRIES_C = [
        ContrastEntry('12', 'לָחַם', 'no standard Qal',    'הִלָּחֵם',         'Imperative 2ms', 'Exo 17:9',  'fight against Amalek!',           'Simple action', 'Niphal is the base form; no causative layer'),
        ContrastEntry('13', 'נָחַם', 'no standard Qal',    'וַיִּנָּחֶם',      'Wayyiqtol 3ms',  'Gen 6:6',   'the LORD regretted / relented',   'Simple action', 'Niphal is the base form; to regret/relent/be comforted'),
        ContrastEntry('14', 'שָׁבַע', 'to seven/complete', 'הִשָּׁבְעָה',      'Imperative 2ms', 'Gen 47:31', 'swear to me!',                    'Reflexive',     'Bind yourself by oath; reflexive oath-taking'),
    ]

    def _build(self):
        self.add_instructions(
            'For each item: (1) write an English translation of the Niphal form in the Translation '
            'column; (2) write the semantic function (Passive / Reflexive / Simple Action) in the '
            'Function column. Answer key is on the last page.'
        )

        self.add_section_heading('Part A — Transitive Roots (Qal acts on an object)')
        self.add_note('These roots take a direct object in the Qal. The Niphal turns the object into the subject — the classic passive pattern.')
        self.add_contrast_table(self._ENTRIES_A, show_answers=False)

        self.add_section_heading('Part B — Stative / Intransitive Roots')
        self.add_note('These roots describe states. Their Niphal expresses the subject coming into or remaining in a state.')
        self.add_contrast_table(self._ENTRIES_B, show_answers=False)

        self.add_section_heading('Part C — Roots with No Standard Qal')
        self.add_note('These roots occur almost exclusively in the Niphal. The Niphal form is the standard lexical entry.')
        self.add_contrast_table(self._ENTRIES_C, show_answers=False)

        self.add_reflection([
            'For the transitive roots in Part A, describe the pattern in one sentence: what does the '
            'Niphal consistently do to the Qal meaning?',
            'Items 9–11 all involve verbs of position or remaining (נָצַב, יָתַר, שָׁאַר). How does '
            '"reflexive" vs. "middle" vs. "passive" help explain the subtle difference in agency?',
            'לָחַם (item 12) and נָחַם (item 13) are both "lexical Niphal" roots. How does a student '
            'recognize this? What should they look for in a dictionary entry?',
        ])

        self.add_answer_key_contrast(self._ENTRIES_A + self._ENTRIES_B + self._ENTRIES_C)


def build_ch24_contrast_exercise(out_dir: str = None) -> str:
    if out_dir is None:
        here = os.path.dirname(os.path.abspath(__file__))
        out_dir = os.path.join(here, '..', '..', 'output', 'lessons',
                               'hebrew', 'bbh', 'ch24', 'exercises',
                               'ch24-qal-niphal-contrast')
    path = os.path.join(out_dir, 'ch24-qal-niphal-contrast.pdf')
    ex = Ch24ContrastExercise(
        title='Chapter 24 — Qal–Niphal Contrast Drill',
        subtitle='BBH Chapter 24 · Niphal Strong Verbs',
    )
    return ex.save(path)


# ---------------------------------------------------------------------------
# Chapter 24 — Semantic Function Sorting
# ---------------------------------------------------------------------------
class Ch24FunctionSortExercise(ExercisePDF):

    _ENTRIES = [
        SortEntry('1',  'וַיִּמָּכֵר',      'Wayyiqtol 3ms',  'Gen 37:36', '"and Joseph was sold into Egypt"',              'P',  'מָכַר',  'Joseph receives the action of being sold'),
        SortEntry('2',  'נִצָּבָה',         'Perfect 3fs',    'Gen 37:7',  '"my sheaf stood upright"',                      'R',  'נָצַב',  'Sheaf stations itself (acts on itself)'),
        SortEntry('3',  'וַיִּנָּחֶם',      'Wayyiqtol 3ms',  'Gen 6:6',   '"the LORD regretted"',                          'SA', 'נָחַם',  'Niphal-only: no standard Qal; to regret/relent'),
        SortEntry('4',  'יֵאָכֵל',          'Imperfect 3ms',  'Exo 12:46', '"it shall be eaten"',                           'P',  'אָכַל',  'Passover lamb receives the action of eating'),
        SortEntry('5',  'הִשָּׁמְרוּ',      'Imperative 2mp', 'Exo 19:12', '"take heed for yourselves!"',                   'R',  'שָׁמַר', 'Guard yourself — subject directs action back on self'),
        SortEntry('6',  'נִשְׁמַע',         'Perfect 3ms',    'Gen 45:16', '"the report was heard"',                        'P',  'שָׁמַע', 'Report receives the hearing — it becomes audible'),
        SortEntry('7',  'הִשָּׁבְעָה',      'Imperative 2ms', 'Gen 47:31', '"swear to me!"',                                'R',  'שָׁבַע', 'Bind yourself by oath (reflexive oath-taking)'),
        SortEntry('8',  'הַנִּמְצָא',       'Participle ms',  'Gen 47:14', '"the silver that was found"',                   'P',  'מָצָא',  'Silver was discovered (received the finding action)'),
        SortEntry('9',  'וְנִכְרְתָה',      'Weqatal 3fs',    'Exo 12:15', '"that person will be cut off"',                 'P',  'כָּרַת', 'Person receives covenant-exclusion penalty'),
        SortEntry('10', 'נִצָּבִים',        'Participle mp',  'Exo 5:20',  '"standing before Pharaoh"',                     'R',  'נָצַב',  'Overseers have stationed themselves before Pharaoh'),
        SortEntry('11', 'אִוָּעֵד',         'Imperfect 1cs',  'Exo 29:42', '"I will meet with you there"',                  'RC', 'יָעַד',  'God and Israel meet one another at the tent'),
        SortEntry('12', 'וַיִּשָּׁבַע',     'Wayyiqtol 3ms',  'Gen 47:31', '"and he swore to him"',                         'R',  'שָׁבַע', 'Jacob binds himself by oath at Joseph\'s request'),
        SortEntry('13', 'וַיֵּאָסֶף',       'Wayyiqtol 3ms',  'Gen 49:33', '"and he was gathered to his people"',           'P',  'אָסַף',  'Jacob is gathered in (brought to ancestors — die)'),
        SortEntry('14', 'יִלָּחֵם',         'Imperfect 3ms',  'Exo 14:14', '"the LORD will fight for you"',                 'SA', 'לָחַם',  'Niphal-only: to fight is the base meaning'),
        SortEntry('15', 'נִשְׁבְּעוּ',      'Weqatal 3mp',    'Gen 21:31', '"both of them swore"',                          'R',  'שָׁבַע', 'Each binds himself individually — reflexive, not reciprocal'),
        SortEntry('16', 'תִּכָּרֵת',        'Imperfect 3fs',  'Gen 41:36', '"the land will not be cut off"',                'P',  'כָּרַת', 'Land receives the action of being cut off (depleted)'),
        SortEntry('17', 'נִלְחָם',          'Participle ms',  'Exo 14:25', '"the LORD is fighting for them"',               'SA', 'לָחַם',  'Niphal-only: the LORD fights (no Qal to contrast)'),
        SortEntry('18', 'הֵאָסְפוּ',        'Imperative 2mp', 'Gen 49:1',  '"gather yourselves!"',                          'P',  'אָסַף',  'Passive imperative: be gathered (assemble)'),
        SortEntry('19', 'וְנוֹעֲדוּ',       'Weqatal 3mp',    'Num 10:3',  '"all the congregation shall assemble"',         'RC', 'יָעַד',  'Congregation assembles mutually together'),
        SortEntry('20', 'נִחַמְתִּי',       'Weqatal 1cs',    'Gen 6:7',   '"I regret that I made them"',                   'SA', 'נָחַם',  'Niphal-only: I regret is the base meaning'),
        SortEntry('21', 'נְמַלְתֶּם',       'Weqatal 2mp',    'Gen 17:11', '"you shall be circumcised"',                    'P',  'מוּל',   'Males receive the action of circumcision'),
        SortEntry('22', 'נִצַּבְתָּ',       'Perfect 2ms',    'Exo 7:15',  '"station yourself to meet him"',                'R',  'נָצַב',  'Moses positions himself at the Nile'),
        SortEntry('23', 'לְהִלָּחֵם',       'Inf. Construct', 'Exo 17:10', '"to fight against Amalek"',                     'SA', 'לָחַם',  'Niphal-only: to fight — the inf. construct form'),
        SortEntry('24', 'יִמָּצֵא',         'Imperfect 3ms',  'Gen 44:9',  '"whoever is found [with the cup]"',             'P',  'מָצָא',  'Person discovered with cup — receives the finding'),
        SortEntry('25', 'הִמָּצֵא יִמָּצֵא','Inf. Abs. + Impl','Exo 22:3', '"if it is actually found in his possession"',  'P',  'מָצָא',  'Emphatic passive; doubling stresses the discovery'),
    ]

    def _build(self):
        self.add_instructions(
            'Classify each Niphal verb as P (Passive), R (Reflexive), RC (Reciprocal), '
            'or SA (Simple Action). Write your answer in the Function column. '
            'Answer key is on the last page.'
        )

        self.add_note(
            'P = Passive (subject receives the action)  |  '
            'R = Reflexive (subject acts on/for itself)  |  '
            'RC = Reciprocal (subjects act on one another)  |  '
            'SA = Simple Action (Niphal-only root; no distinct Qal meaning)'
        )

        self.add_sort_table(self._ENTRIES, show_answers=False)

        self.add_reflection([
            'Items 3, 14, 17, 20, and 23 are all Simple Action (לָחַם and נָחַם). What is the practical '
            'difference between a Niphal-only root and a root that simply lacks a Qal in the OT corpus?',
            'Compare items 7 and 12 (both שָׁבַע). The imperative and wayyiqtol appear in the same verse '
            '(Gen 47:31). How does the sequential narrative create a scene of formal oath-taking?',
            'Item 18 (הֵאָסְפוּ) is Passive, yet it is an imperative. Explain how a Niphal imperative '
            'can be both a command and passive in force.',
        ])

        self.add_answer_key_sort(self._ENTRIES)


def build_ch24_function_sort_exercise(out_dir: str = None) -> str:
    if out_dir is None:
        here = os.path.dirname(os.path.abspath(__file__))
        out_dir = os.path.join(here, '..', '..', 'output', 'lessons',
                               'hebrew', 'bbh', 'ch24', 'exercises',
                               'ch24-function-sort')
    path = os.path.join(out_dir, 'ch24-function-sort.pdf')
    ex = Ch24FunctionSortExercise(
        title='Chapter 24 — Semantic Function Sorting',
        subtitle='BBH Chapter 24 · Niphal Strong Verbs',
    )
    return ex.save(path)


if __name__ == '__main__':
    p0 = build_ch24_exercise()
    print(f'Saved: {p0}')
    p1 = build_ch24_contrast_exercise()
    print(f'Saved: {p1}')
    p2 = build_ch24_function_sort_exercise()
    print(f'Saved: {p2}')
    p3 = build_ch25_exercise()
    print(f'Saved: {p3}')
    p4 = build_ch26_exercise()
    print(f'Saved: {p4}')
    p5 = build_ch26_contrast_exercise()
    print(f'Saved: {p5}')
    p6 = build_ch26_function_sort_exercise()
    print(f'Saved: {p6}')
