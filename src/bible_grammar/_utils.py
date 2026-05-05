"""Shared low-level utilities used across bible_grammar modules."""

from __future__ import annotations
import re
import unicodedata


def strip_diacritics(text: str) -> str:
    """Remove all combining diacritical marks (vowels, dagesh, cantillation) from text."""
    return ''.join(
        c for c in unicodedata.normalize('NFD', str(text))
        if unicodedata.category(c) != 'Mn'
    )


def norm_strongs(s: str) -> str:
    """
    Normalise a Strong's value to H/G + unpadded number + optional variant letter.

    Handles both TAHOT stored format (braced, e.g. '{H0430G}', 'H9003/{H1697I}')
    and plain format (e.g. 'G2316', 'H0001').

    Examples
    --------
    '{H0430G}'       → 'H430G'
    'H9003/{H1697I}' → 'H1697I'   (skips H9xxx grammatical particle)
    'G2316'          → 'G2316'
    'H0001'          → 'H1'
    """
    # Hebrew TAHOT format: extract content word from curly braces, skip H9xxx particles
    braced = re.findall(r'\{([HG]\d+[A-Z]?)\}', s)
    for m in braced:
        if not re.match(r'H9\d+', m):
            pfx = m[0]
            rest = m[1:]
            num = re.match(r'0*(\d+)([A-Z]?)$', rest)
            if num:
                return pfx + num.group(1) + num.group(2)
            return m
    if braced:
        # All were H9xxx grammatical particles — fall back to first
        m = braced[0]
        pfx = m[0]
        rest = m[1:]
        num = re.match(r'0*(\d+)([A-Z]?)$', rest)
        return pfx + (num.group(1) + num.group(2) if num else rest)

    # Plain format: strip leading zeros
    m2 = re.match(r'^([HG])0*(\d+)([A-Z]?)$', s.strip().upper())
    if m2:
        return m2.group(1) + m2.group(2) + m2.group(3)
    return s.strip().upper()


def norm_strongs_user(s: str) -> str:
    """
    Normalise a user-supplied Strong's number for comparison against norm_strongs output.

    Only handles plain format (no braces); use for query inputs, not stored values.

    Examples
    --------
    'H0430'  → 'H430'
    'h7225'  → 'H7225'
    'G03056' → 'G3056'
    """
    m = re.match(r'^([HG])0*(\d+)([A-Z]?)$', s.strip().upper())
    if m:
        return m.group(1) + m.group(2) + m.group(3)
    return s.strip().upper()
