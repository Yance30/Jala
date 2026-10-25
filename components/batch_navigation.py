"""Focus a batch section after a session-preserving page change."""
import json

import streamlit.components.v1 as components


def scroll_to_section(anchor):
    if anchor not in ("siapkan-data", "validasi-paket", "jalankan-prediksi"):
        raise ValueError("Unknown batch section")
    components.html(
        """<script>
        const anchor = ANCHOR;
        const doc = window.parent.document;
        let attempts = 0;
        const timer = setInterval(() => {
            const heading = doc.getElementById(anchor);
            if (heading) {
                heading.scrollIntoView({behavior: 'instant', block: 'start'});
                heading.setAttribute('tabindex', '-1');
                heading.focus({preventScroll: true});
                clearInterval(timer);
            } else if (++attempts >= 80) {
                clearInterval(timer);
            }
        }, 100);
        window.addEventListener('pagehide', () => clearInterval(timer), {once: true});
        </script>""".replace("ANCHOR", json.dumps(anchor)),
        height=0,
    )
