"""MkDocs hooks — inject Binder badge into notebook pages."""

BINDER_BASE = (
    "https://mybinder.org/v2/gh/dnovick/berean-bible-bots/main"
    "?urlpath=lab/tree/"
)
BADGE_IMG = "https://mybinder.org/badge_logo.svg"

_BADGE_HTML = (
    '<p style="margin-bottom:1rem;">'
    '<a href="{url}" target="_blank" rel="noopener">'
    '<img src="' + BADGE_IMG + '" alt="Launch in Binder">'
    "</a></p>\n"
)


def on_page_content(html: str, page: object, **kwargs: object) -> str:
    """Prepend a Binder launch badge to every notebook page."""
    src = getattr(page, "file", None)
    if src is None:
        return html
    path = str(src.src_uri)
    if not path.startswith("notebooks/") or not path.endswith(".ipynb"):
        return html

    binder_url = f"{BINDER_BASE}{path}"
    badge = _BADGE_HTML.format(url=binder_url)
    return badge + html
