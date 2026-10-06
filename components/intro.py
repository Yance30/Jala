from datetime import timedelta

import streamlit as st

from components.theme import LOGO_SVG


INTRO_SECONDS = 3.2


NODES = [
    (120, 120),
    (300, 60),
    (520, 140),
    (760, 80),
    (940, 170),
    (200, 320),
    (430, 300),
    (680, 280),
    (880, 360),
    (330, 470),
    (600, 460),
    (820, 500),
]


EDGES = [
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 4),
    (0, 5),
    (1, 6),
    (2, 6),
    (3, 7),
    (4, 8),
    (5, 6),
    (6, 7),
    (7, 8),
    (5, 9),
    (6, 9),
    (6, 10),
    (7, 10),
    (8, 11),
    (10, 11),
]


FLAGGED = 6  # node oranye (anomali)


CSS = """
<style>

/* =========================================================
   HIDE SIDEBAR DURING INTRO
   ========================================================= */

section[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"] {
    display: none !important;
}


.block-container {
    position: relative;
    z-index: 1;
}


/* =========================================================
   BACKGROUND
   ========================================================= */

.j-intro-bg {
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    background:
        radial-gradient(
            circle at 20% 15%,
            #E6F4F2 0%,
            #F8FAFC 55%
        );
}


.j-intro-bg svg {
    width: 100%;
    height: 100%;
}


/* =========================================================
   NETWORK EDGES
   ========================================================= */

.j-edge {
    stroke: #0F766E;
    stroke-opacity: .35;
    stroke-width: 1.6;
    stroke-dasharray: 6 8;
    animation: j-flow 2.4s linear infinite;
}


.j-edge.risk {
    stroke: #EA580C;
    stroke-opacity: .55;
}


@keyframes j-flow {
    to {
        stroke-dashoffset: -28;
    }
}


/* =========================================================
   NETWORK NODES
   ========================================================= */

.j-node {
    fill: #0F766E;
    transform-box: fill-box;
    transform-origin: center;
    animation: j-pulse 3.2s ease-in-out infinite;
}


.j-node.risk {
    fill: #EA580C;
}


@keyframes j-pulse {

    0%,
    100% {
        transform: scale(1);
        opacity: .9;
    }

    50% {
        transform: scale(1.35);
        opacity: 1;
    }
}


/* =========================================================
   RISK RING
   ========================================================= */

.j-ring {
    fill: none;
    stroke: #EA580C;
    stroke-width: 2;
    transform-box: fill-box;
    transform-origin: center;
    animation: j-ring 2.4s ease-out infinite;
}


@keyframes j-ring {

    0% {
        transform: scale(.6);
        opacity: .8;
    }

    100% {
        transform: scale(3.2);
        opacity: 0;
    }
}


/* =========================================================
   DATA PACKET
   ========================================================= */

.j-packet {
    fill: #F97316;
}


/* =========================================================
   INTRO CENTER
   ========================================================= */

.j-intro-center {
    position: relative;
    z-index: 2;
    text-align: center;
    margin: 16vh auto 0;
    max-width: 560px;
    animation: j-rise .8s ease-out both;
}


@keyframes j-rise {

    from {
        opacity: 0;
        transform: translateY(18px);
    }

    to {
        opacity: 1;
        transform: none;
    }
}


/* =========================================================
   LOGO
   ========================================================= */

/*
   Logo SVG dihapus agar tidak membutuhkan LOGO_SVG.
   Sebagai gantinya digunakan lingkaran sederhana
   sebagai elemen visual pembuka.
*/

.j-intro-logo {
    width: 84px;
    height: 84px;
    margin: 0 auto 16px;
    border-radius: 22px;
    overflow: hidden;
    box-shadow: 0 12px 40px rgba(15, 118, 110, .25);
    animation: j-bob 3.5s ease-in-out infinite;
}


@keyframes j-bob {

    0%,
    100% {
        transform: translateY(0);
    }

    50% {
        transform: translateY(-6px);
    }
}


/* =========================================================
   TITLE
   ========================================================= */

.j-intro-title {
    font-size: 34px;
    font-weight: 700;
    color: #0F766E;
    letter-spacing: -0.02em;
}


.j-intro-sub {
    font-size: 14px;
    font-weight: 600;
    color: #132A1C;
    margin-top: 2px;
}


.j-intro-tag {
    font-size: 14px;
    line-height: 1.6;
    color: #475569;
    max-width: 440px;
    margin: 10px auto 0;
}


.j-intro-facts {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    justify-content: center;
    margin-top: 18px;
}


.j-intro-facts span {
    font-size: 12px;
    font-weight: 600;
    color: #0F766E;
    background: rgba(255, 255, 255, .8);
    border: 1px solid rgba(15, 118, 110, .22);
    border-radius: 9999px;
    padding: 5px 12px;
}


/* =========================================================
   LOADING BAR
   ========================================================= */

.j-intro-loadbar {
    height: 6px;
    border-radius: 9999px;
    background: #D7EDEA;
    overflow: hidden;
    margin: 22px auto 10px;
    width: 260px;
}


.j-intro-loadbar span {
    display: block;
    height: 100%;
    width: 0;
    background: #0F766E;
    animation: j-load 3s ease-in-out forwards;
}


@keyframes j-load {
    to {
        width: 100%;
    }
}


/* =========================================================
   STATUS TEXT
   ========================================================= */

.j-intro-status {
    position: relative;
    height: 18px;
    font-size: 12px;
    color: #64748B;
}


.j-intro-status span {
    position: absolute;
    left: 0;
    right: 0;
    opacity: 0;
    animation: j-status 3s linear forwards;
}


.j-intro-status span:nth-child(1) {
    animation-delay: 0s;
}


.j-intro-status span:nth-child(2) {
    animation-delay: 1s;
}


.j-intro-status span:nth-child(3) {
    animation-delay: 2s;
}


@keyframes j-status {

    0% {
        opacity: 0;
    }

    8%,
    30% {
        opacity: 1;
    }

    38%,
    100% {
        opacity: 0;
    }
}


/* =========================================================
   ACCESSIBILITY
   ========================================================= */

@media (prefers-reduced-motion: reduce) {

    .j-edge,
    .j-node,
    .j-ring,
    .j-intro-logo,
    .j-intro-center {
        animation: none !important;
    }

    .j-packet {
        display: none;
    }
}


/* =========================================================
   MOBILE
   ========================================================= */

@media (max-width: 640px) {

    .j-intro-center {
        margin: 10vh 16px 0;
    }

    .j-intro-title {
        font-size: 28px;
    }
}

</style>
"""


def _background() -> str:
    """
    Membuat background berupa jaringan node dan edge
    yang dianimasikan.
    """

    edges = []
    packets = []

    # -----------------------------------------------------
    # EDGE + PACKET
    # -----------------------------------------------------

    for i, (a, b) in enumerate(EDGES):

        (x1, y1), (x2, y2) = NODES[a], NODES[b]

        risk = FLAGGED in (a, b)

        edge_class = "j-edge risk" if risk else "j-edge"

        edges.append(
            f'<line '
            f'class="{edge_class}" '
            f'x1="{x1}" '
            f'y1="{y1}" '
            f'x2="{x2}" '
            f'y2="{y2}" '
            f'style="animation-delay:{(i % 5) * .3}s"/>'
        )

        packets.append(
            f'<circle class="j-packet" r="3.5">'
            f'<animateMotion '
            f'dur="{3 + (i % 4)}s" '
            f'begin="{(i % 6) * .5}s" '
            f'repeatCount="indefinite" '
            f'path="M{x1} {y1} L{x2} {y2}"/>'
            f'</circle>'
        )

    # -----------------------------------------------------
    # NODES
    # -----------------------------------------------------

    nodes = []

    for i, (x, y) in enumerate(NODES):

        risk = i == FLAGGED

        # Node anomali
        if risk:
            nodes.append(
                f'<circle '
                f'class="j-ring" '
                f'cx="{x}" '
                f'cy="{y}" '
                f'r="10"/>'
            )

        node_class = "j-node risk" if risk else "j-node"

        radius = 11 if risk else 8

        nodes.append(
            f'<circle '
            f'class="{node_class}" '
            f'cx="{x}" '
            f'cy="{y}" '
            f'r="{radius}" '
            f'style="animation-delay:{(i % 6) * .4}s"/>'
        )

    # -----------------------------------------------------
    # RETURN SVG
    # -----------------------------------------------------

    return (
        '<div class="j-intro-bg">'
        '<svg '
        'viewBox="0 0 1080 580" '
        'preserveAspectRatio="xMidYMid slice" '
        'aria-hidden="true">'
        + "".join(edges)
        + "".join(packets)
        + "".join(nodes)
        + "</svg>"
        "</div>"
    )


def render():
    """
    Tampilkan animasi pembuka,
    lalu lanjut ke dashboard.
    """

    st.markdown(
        CSS
        + _background()
        + """
        <div class="j-intro-center" role="status" aria-live="polite">
          <div class="j-intro-logo">__LOGO__</div>
          <div class="j-intro-title">JALA</div>
          <div class="j-intro-sub">Jaringan Analitik Lintas Aktor</div>
          <div class="j-intro-tag">
            Membantu tim pencegahan fraud menemukan klaim kesehatan yang
            mencurigakan dengan melihat hubungan antara fasilitas kesehatan,
            dokter, dan pasien.
          </div>
          <div class="j-intro-facts">
            <span>Data buatan, bukan data peserta</span>
            <span>Prototipe untuk uji coba</span>
            <span>Keputusan akhir di tangan petugas</span>
          </div>
          <div class="j-intro-loadbar"><span></span></div>
          <div class="j-intro-status">
            <span>Membaca data klaim…</span>
            <span>Menyusun peta hubungan…</span>
            <span>Menyiapkan tampilan…</span>
          </div>
        </div>
        """.replace("__LOGO__", LOGO_SVG),
        unsafe_allow_html=True,
    )

    # Animasi berjalan di sisi klien (CSS). Fragment dengan run_every memicu rerun
    # setelah INTRO_SECONDS tanpa menahan thread server (penting di Streamlit Cloud).
    @st.fragment(run_every=timedelta(seconds=INTRO_SECONDS))
    def _advance():
        if st.session_state.get("_intro_started"):
            st.session_state.intro_done = True
            st.session_state.pop("_intro_started", None)
            st.rerun()
        else:
            st.session_state["_intro_started"] = True

    _advance()