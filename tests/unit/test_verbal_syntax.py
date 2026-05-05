"""Tests for bible_grammar.verbal_syntax helper functions — pure logic, no I/O."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from bible_grammar.verbal_syntax import _strip_diacritics, VERB_FORM_ORDER, VERB_FORM_LABELS


class TestStripDiacritics:
    def test_removes_hebrew_vowel_points(self) -> None:
        # בְּרֵאשִׁית with vowels → bare consonants
        pointed = "בְּרֵאשִׁית"
        stripped = _strip_diacritics(pointed)
        assert stripped == "בראשית"

    def test_removes_cantillation(self) -> None:
        # Etnahta U+0591 is cantillation
        with_accent = "בְּרֵאשִׁ֣ית"
        assert _strip_diacritics(with_accent) == "בראשית"

    def test_plain_ascii_unchanged(self) -> None:
        assert _strip_diacritics("hello") == "hello"

    def test_empty_string(self) -> None:
        assert _strip_diacritics("") == ""

    def test_removes_dagesh(self) -> None:
        # בּ has a dagesh (U+05BC combining character)
        with_dagesh = "בּ"  # bet + dagesh
        assert _strip_diacritics(with_dagesh) == "ב"

    def test_latin_with_accents(self) -> None:
        # é → e (Latin combining acute)
        assert _strip_diacritics("é") == "e"

    def test_mixed_pointed_and_plain(self) -> None:
        mixed = "H7965 שָׁלוֹם"
        result = _strip_diacritics(mixed)
        assert "שלום" in result
        assert "H7965" in result


class TestVerbFormConstants:
    def test_form_order_has_expected_entries(self) -> None:
        assert "wayyiqtol" in VERB_FORM_ORDER
        assert "qatal" in VERB_FORM_ORDER
        assert "yiqtol" in VERB_FORM_ORDER
        assert "infinitive construct" in VERB_FORM_ORDER
        assert "infinitive absolute" in VERB_FORM_ORDER

    def test_form_labels_cover_form_order(self) -> None:
        for form in VERB_FORM_ORDER:
            assert form in VERB_FORM_LABELS, f"Missing label for {form!r}"

    def test_labels_are_short(self) -> None:
        for form, label in VERB_FORM_LABELS.items():
            assert len(label) <= 10, f"Label {label!r} is too long for chart axis"

    def test_unique_entries(self) -> None:
        assert len(VERB_FORM_ORDER) == len(set(VERB_FORM_ORDER))
