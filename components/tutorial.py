"""Tutorial penggunaan: dialog langkah demi langkah yang mengikuti alur demo JALA.

* Tombol "Cara Pakai" di sidebar membuka dialog kapan saja.
* Terbuka otomatis sekali per sesi setelah animasi pembuka; matikan dengan `?tour=0` (demo, tes e2e).
* Tiap langkah punya tombol "Buka halaman ini" yang langsung memuat klaster contoh dari data nyata.
* Bahasa sehari-hari; istilah teknis dijelaskan di "Arti istilah yang dipakai" (components/guide.py).
* Tidak ada angka di teks langkah (agar tidak basi); klaster contoh diambil dari skor dasar model.
"""
import html

import streamlit as st

from components import bench, guide, layout

# page: halaman yang dibuka tombol "Buka halaman ini" (None = tidak ada); cluster: bawa klaster contoh
STEPS = [
    {"page": None, "cluster": False, "icon": "👋", "title": "Selamat datang di JALA", "tag": "Mulai di sini",
     "goal": "Paham apa yang dilakukan JALA, dan apa yang tidak, sebelum mulai.",
     "lead": "JALA membantu menemukan kecurangan klaim yang dilakukan bersama-sama oleh beberapa pihak, "
             "yang sulit terlihat bila klaim diperiksa satu per satu.",
     "do": ["Bayangkan JALA sebagai peta: ia menunjukkan siapa berhubungan dengan siapa, lalu menandai kelompok yang janggal.",
            "Semua data di sini buatan. Tidak ada data peserta yang sebenarnya.",
            "JALA hanya menyarankan urutan pemeriksaan. Keputusan akhir selalu ada pada petugas verifikator.",
            "Alurnya sederhana: lihat ringkasan, pilih kelompok, lihat jaringannya, baca alasannya, lalu putuskan."],
     "tip": "Panduan ini bisa dibuka lagi kapan saja lewat tombol Cara Pakai di menu samping."},
    {"page": "dashboard", "cluster": False, "icon": "📊", "title": "1. Dashboard: lihat gambaran besar", "tag": "Ringkasan",
     "goal": "Tahu seberapa banyak yang perlu diperhatikan hari ini dan apa yang paling mendesak.",
     "lead": "Halaman pertama merangkum keadaan terkini: berapa klaim yang ditandai dan kelompok mana yang menunggu diperiksa.",
     "do": ["Lihat kartu di bagian atas. Kartu itu menjawab seberapa banyak yang perlu perhatian.",
            "Lihat grafik tren. Cari apakah ada kenaikan tajam yang tidak biasa.",
            "Lihat daftar di bagian bawah. Kelompok paling atas adalah yang paling mendesak.",
            "Semua angka dihitung dari data yang ada, bukan angka contoh."],
     "tip": "Klik nama kelompok di daftar untuk langsung melihat detailnya."},
    {"page": "risk", "cluster": False, "icon": "🏆", "title": "2. Prioritas Klaster: pilih yang diperiksa dulu", "tag": "Prioritas",
     "goal": "Mendapat daftar urut kelompok yang siap diperiksa, lengkap dengan alasan singkat.",
     "lead": "Karena waktu pemeriksa terbatas, kelompok diurutkan menurut skor prioritas. Label merah menunjukkan kelompok untuk ditinjau lebih dahulu.",
     "do": ["Mulai dari kelompok paling atas, karena itu yang paling mencurigakan.",
            "Gunakan kotak cari atau tombol filter bila ingin mencari jenis atau nama tertentu.",
            "Buka satu kelompok untuk membaca alasan mengapa ia ditandai.",
            "Unduh daftar sebagai berkas CSV bila perlu dibawa ke rapat atau dibuka di Excel."],
     "tip": "Skor tinggi bukan bukti curang. Pola yang sah, seperti cuci darah terjadwal, kadang ikut tertandai. Karena itu ada tombol untuk menandai kelompok sebagai wajar."},
    {"page": "network", "cluster": True, "icon": "🕸", "title": "3. Peta Jaringan: lihat hubungannya", "tag": "Penelusuran",
     "goal": "Melihat pola hubungan yang tidak tampak bila klaim dibaca satu per satu.",
     "lead": "Peta ini menunjukkan siapa terhubung dengan siapa untuk membantu meninjau dugaan Phantom Billing (Klaim Palsu), Repeat Billing, atau Rujukan tidak sesuai (Self-referral).",
     "do": ["Pilih satu kelompok, lalu perbesar atau geser peta untuk melihat lebih dekat.",
            "Titik adalah pihak yang terlibat: fasilitas kesehatan, dokter, pasien, dan diagnosis. Garis adalah hubungannya.",
            "Cari yang janggal: dokter yang menagih di banyak fasilitas, atau pasien dari luar daerah yang muncul berulang.",
            "Klik sebuah titik untuk menyorot hubungan miliknya saja."],
     "tip": "Titik yang pudar adalah fasilitas sejenis yang wajar. Gunakan sebagai pembanding."},
    {"page": "claim", "cluster": True, "icon": "🔎", "title": "4. Alasan Penandaan: pahami konteksnya", "tag": "Bukti",
     "goal": "Mendapat penjelasan yang bisa diperiksa dan paket pemeriksaan untuk ditinjau lebih lanjut.",
     "lead": "Halaman ini menjelaskan mengapa sebuah kelompok ditandai, dengan bahasa biasa dan angka yang bisa dicek.",
     "do": ["Baca ringkasan di bagian atas. Isinya kecurigaan dalam satu atau dua kalimat.",
            "Periksa bukti terukur untuk melihat angka yang mendasari penandaan.",
            "Lihat klaim dengan skor tertinggi untuk tahu mana yang perlu dibuka berkasnya lebih dulu.",
            "Unduh paket pemeriksaan (.zip) untuk dibaca dan diverifikasi lebih lanjut."],
     "tip": "Paket pemeriksaan berisi ringkasan, klaim terkait, data fasilitas dan dokter, serta gambar peta hubungan. Isinya bahan tinjauan, bukan bukti pelanggaran yang sudah terverifikasi."},
    {"page": "audit", "cluster": True, "icon": "⚖", "title": "5. Tindak Lanjut: catat keputusan", "tag": "Keputusan",
     "goal": "Mengambil tindakan yang tercatat, dan melihat urutan prioritas ikut menyesuaikan.",
     "lead": "Setelah memahami kasusnya, pilih salah satu dari tiga tindakan. Ada dua alat bantu untuk memutuskan dengan lebih yakin.",
     "do": ["Tulis catatan verifikator terlebih dahulu agar keputusan ada jejaknya.",
            "Pilih tahan pembayaran (simulasi), kirim pemeriksa ke lapangan, atau tandai sebagai wajar.",
            "Mencoba simulasi: bagaimana jika dokter ini dikeluarkan? Hasilnya menunjukkan siapa tulang punggung jaringan.",
            "Salah memilih? Tombol Batalkan mengembalikan skor seperti semula."],
     "tip": "Menandai sebagai wajar hanya menurunkan skor kelompok serupa. Kelompok itu tidak disembunyikan, jadi masih bisa ditinjau."},
    {"page": "about", "cluster": False, "icon": "📐", "title": "6. About: seberapa bisa dipercaya", "tag": "Kejujuran hasil",
     "goal": "Tahu sejauh mana hasil JALA boleh dipercaya dan dikutip.",
     "lead": "Bagian terakhir menunjukkan seberapa baik prototipe bekerja pada data buatan yang jawabannya sudah diketahui.",
     "do": ["Lihat simulasi kapasitas: berapa kecurangan yang tertangkap bila hanya sebagian klaim yang diperiksa.",
            "Baca kotak batasan sebelum mengutip angka ke pihak lain.",
            "Ingat bahwa angka ini bukan ketepatan pada data BPJS yang sebenarnya.",
            "Lihat uji ketahanan untuk tahu apakah hasilnya tetap baik ketika pola kecurangan berubah."],
     "tip": "Selesai! Coba ulangi alurnya dengan kelompok lain."},
]


def _example():
    """Klaster contoh: peringkat teratas menurut skor dasar model (tanpa umpan balik sesi)."""
    c = bench.get_live_base().clusters[0]
    return c["id"], c["name"], c["score"]


def _go(delta: int) -> None:
    st.session_state["tour_step"] = max(0, min(len(STEPS) - 1, st.session_state.get("tour_step", 0) + delta))


_CSS = """
<style>
.jt-head{display:flex;align-items:flex-start;gap:14px;margin:2px 0 14px;}
.jt-icon{width:52px;height:52px;flex:none;border-radius:14px;display:flex;align-items:center;justify-content:center;
  font-size:24px;background:linear-gradient(135deg,#D7EDEA,#EAF6F4);border:1px solid rgba(15,118,110,.22);}
.jt-meta{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:5px;}
.jt-count{font-size:12px;font-weight:600;color:#64748B;}
.jt-progress{height:5px;background:#E2E8F0;border-radius:999px;overflow:hidden;margin:0 0 10px;}
.jt-progress > span{display:block;height:100%;border-radius:inherit;background:linear-gradient(90deg,#0F766E,#2DD4BF);transition:width .2s ease;}
.jt-title{font-size:21px;font-weight:700;letter-spacing:-.02em;color:#132A1C;line-height:1.25;margin:0 0 6px;}
.jt-lead{font-size:14px;line-height:1.6;color:#475569;margin:0;}

.jt-rail{display:flex;align-items:center;margin:4px 0 16px;padding:10px 12px;background:#F8FAFC;
  border:1px solid #E2E8F0;border-radius:12px;}
.jt-dot{width:26px;height:26px;flex:none;border-radius:50%;display:flex;align-items:center;justify-content:center;
  font-size:11px;font-weight:700;background:#fff;color:#94A3B8;border:2px solid #CBD5E1;}
.jt-dot.done{background:#0F766E;border-color:#0F766E;color:#fff;}
.jt-dot.now{background:#fff;border-color:#0F766E;color:#0F766E;box-shadow:0 0 0 4px rgba(15,118,110,.15);}
.jt-bar{flex:1;height:2px;background:#E2E8F0;margin:0 4px;min-width:6px;}
.jt-bar.done{background:#0F766E;}

.jt-grid{display:flex;gap:14px;flex-wrap:wrap;align-items:stretch;}
.jt-main{flex:1.6 1 300px;min-width:0;}
.jt-side{flex:1 1 220px;min-width:0;display:flex;flex-direction:column;gap:10px;}
.jt-label{font-size:13px;font-weight:700;color:#334155;margin:0 0 8px;}

.jt-acts{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:8px;}
.jt-act{display:flex;gap:10px;align-items:flex-start;background:#fff;border:1px solid #E2E8F0;border-radius:10px;
  padding:10px 12px;font-size:13.5px;line-height:1.5;color:#334155;}
.jt-n{width:22px;height:22px;flex:none;border-radius:50%;background:rgba(15,118,110,.10);color:#0F766E;
  font-size:11px;font-weight:700;display:flex;align-items:center;justify-content:center;margin-top:1px;}

.jt-card{border:1px solid #E2E8F0;border-radius:12px;padding:12px 14px;background:#fff;}
.jt-card.goal{background:linear-gradient(145deg,#F0FDFA,#FFFFFF 78%);border-color:#B9DED9;box-shadow:0 3px 12px rgba(15,118,110,.04);}
.jt-card.example{background:#FFF7ED;border-color:rgba(249,115,22,.30);}
.jt-card .k{font-size:12.5px;font-weight:700;margin-bottom:5px;}
.jt-card.goal .k{color:#0F766E;} .jt-card.example .k{color:#C2410C;}
.jt-card .v{font-size:13.5px;line-height:1.5;color:#132A1C;font-weight:500;}
.jt-card .s{font-size:12px;color:#64748B;margin-top:3px;}

.jt-tip{display:flex;gap:8px;align-items:flex-start;margin-top:14px;padding:10px 12px;border-radius:10px;
  background:#F1F5F9;border-left:3px solid #0F766E;font-size:12.5px;line-height:1.5;color:#475569;}

.jt-flow{display:flex;flex-wrap:wrap;align-items:center;gap:6px;margin-top:14px;}
.jt-chip{font-size:11.5px;font-weight:600;padding:4px 10px;border-radius:9999px;background:rgba(15,118,110,.08);
  color:#0F766E;border:1px solid rgba(15,118,110,.20);}
.jt-chip.now{background:#0F766E;color:#fff;}
.jt-arrow{color:#94A3B8;font-size:12px;}
@media (max-width:640px){
  .jt-head{gap:10px;margin-bottom:12px;}
  .jt-icon{width:44px;height:44px;border-radius:12px;font-size:21px;}
  .jt-title{font-size:19px;}
  .jt-rail{padding:8px;margin-bottom:12px;}
  .jt-dot{width:23px;height:23px;font-size:10px;}
  .jt-bar{margin:0 2px;}
}
@media (prefers-reduced-motion:reduce){.jt-progress > span{transition:none;}}
</style>
"""


def _short(title: str) -> str:
    """'3. Network Graph: lihat jaringannya' -> 'Network Graph'."""
    return title.split(".", 1)[-1].split(":", 1)[0].strip()


def _rail(i: int) -> str:
    out = []
    for k in range(len(STEPS)):
        cls = "done" if k < i else "now" if k == i else ""
        out.append(f'<div class="jt-dot {cls}">{"✓" if k < i else k + 1}</div>')
        if k < len(STEPS) - 1:
            out.append(f'<div class="jt-bar {"done" if k < i else ""}"></div>')
    return f'<div class="jt-rail" aria-label="Kemajuan panduan">{"".join(out)}</div>'


def _flow(i: int) -> str:
    chips = []
    for k, st_ in enumerate(STEPS[1:], start=1):
        chips.append(f'<span class="jt-chip {"now" if k == i else ""}">{_short(st_["title"])}</span>')
    arrow = '<span class="jt-arrow">→</span>'
    return f'<div class="jt-flow">{arrow.join(chips)}</div>'


@st.dialog("Cara Pakai JALA", width="large")
def _tour() -> None:
    i = max(0, min(len(STEPS) - 1, st.session_state.get("tour_step", 0)))
    s = STEPS[i]
    cid, name, score = _example()

    acts = "".join(f'<li class="jt-act"><span class="jt-n">{n}</span><div>{x}</div></li>'
                   for n, x in enumerate(s["do"], start=1))
    example = (f'<div class="jt-card example"><div class="k">Kelompok contoh</div>'
               f'<div class="v">Tombol di bawah akan membuka: <b>{html.escape(str(name))}</b></div>'
               f'<div class="s">{html.escape(str(cid))}, skor {score}%</div></div>') if s["cluster"] else ""
    flow = _flow(i) if i in (0, len(STEPS) - 1) else ""

    progress = (i + 1) / len(STEPS) * 100
    st.markdown(
        _CSS + guide.CSS
        + f'<div class="jt-head"><div class="jt-icon">{s["icon"]}</div><div>'
          f'<div class="jt-meta"><span class="j-pill teal">{s["tag"]}</span>'
          f'<span class="jt-count">Langkah {i + 1} dari {len(STEPS)}</span></div>'
          f'<div class="jt-title">{s["title"]}</div><p class="jt-lead">{s["lead"]}</p></div></div>'
        + f'<div class="jt-progress" role="progressbar" aria-label="Kemajuan panduan" aria-valuemin="1" aria-valuemax="{len(STEPS)}" aria-valuenow="{i + 1}"><span style="width:{progress:.2f}%"></span></div>'
        + _rail(i)
        + f'<div class="jt-grid"><div class="jt-main"><div class="jt-label">Yang bisa Anda lakukan di sini</div>'
          f'<ul class="jt-acts">{acts}</ul></div>'
          f'<div class="jt-side"><div class="jt-card goal"><div class="k">Setelah langkah ini, Anda akan</div>'
          f'<div class="v">{s["goal"]}</div></div>{example}</div></div>'
        + flow
        + f'<div class="jt-tip"><span>💡</span><div><b>Perlu diingat.</b> {s["tip"]}</div></div>',
        unsafe_allow_html=True,
    )
    with st.expander("Arti istilah yang dipakai"):
        st.markdown(guide.glossary_html(), unsafe_allow_html=True)
    st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1.5])
    c1.button("← Sebelumnya", key="tour_prev", disabled=i == 0, on_click=_go, args=(-1,), width="stretch")
    if i < len(STEPS) - 1:
        c2.button("Berikutnya →", key="tour_next", on_click=_go, args=(1,), width="stretch")
    elif c2.button("Selesai", key="tour_done", width="stretch"):
        st.session_state["tour_step"] = 0
        st.rerun()
    if s["page"] and c3.button("Buka halaman ini ↗", key="tour_open_page", type="primary", width="stretch"):
        layout.goto(s["page"], cluster=cid if s["cluster"] else None)
    if i == 0 and st.button("Lewati panduan", key="tour_skip", type="tertiary"):
        st.rerun()


def show() -> None:
    _tour()


def sidebar_button() -> None:
    """Tombol 'Cara Pakai' di sidebar; membuka dialog di langkah terakhir yang dilihat."""
    if st.button("❓ Cara Pakai", key="tour_open", width="stretch"):
        show()


def maybe_auto_show() -> None:
    """Buka otomatis sekali per sesi (kecuali ?tour=0)."""
    if st.session_state.get("tour_seen"):
        return
    st.session_state["tour_seen"] = True
    if st.query_params.get("tour") != "0":
        show()
