# 1. Import library
import json
from pathlib import Path

import joblib
import pandas as pd
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
BASE = Path(__file__).parent

# 2. Load model dan metadata hasil notebook (web tidak melakukan training)
model = joblib.load(BASE / "model" / "rf_churn.joblib")
meta = json.loads((BASE / "model" / "meta.json").read_text(encoding="utf-8"))
FITUR = meta["feature_order"]
TURUNAN = ("Avg_Open_To_Buy", "Avg_Utilization_Ratio")

# 3. Catatan analisis pribadi (opsional, isi dengan interpretasi sendiri)
CATATAN = {"a": "", "b": "", "fi": ""}

# 4. Urutan tampilan opsi kategori
URUTAN = {
    "Education_Level": ["Unknown", "Uneducated", "High School", "College",
                        "Graduate", "Post-Graduate", "Doctorate"],
    "Income_Category": ["Less than $40K", "$40K - $60K", "$60K - $80K",
                        "$80K - $120K", "$120K +", "Unknown"],
    "Card_Category": ["Blue", "Silver", "Gold", "Platinum"],
}


def urutkan(kolom, opsi):
    if kolom not in URUTAN:
        return sorted(opsi)
    acuan = URUTAN[kolom]
    return sorted(opsi, key=lambda o: acuan.index(o) if o in acuan else 99)


# 5. Label, keterangan, dan pengelompokan form
LABEL = {
    "Customer_Age": ("Usia", "Usia nasabah dalam tahun"),
    "Gender": ("Jenis kelamin", ""),
    "Dependent_count": ("Jumlah tanggungan", "Anggota keluarga yang ditanggung"),
    "Education_Level": ("Pendidikan", ""),
    "Marital_Status": ("Status pernikahan", ""),
    "Income_Category": ("Kategori pendapatan", "Pendapatan per tahun dalam USD"),
    "Card_Category": ("Jenis kartu", "Blue adalah kartu paling dasar"),
    "Months_on_book": ("Lama jadi nasabah", "Dalam bulan"),
    "Total_Relationship_Count": ("Jumlah produk bank", "Total produk yang dipakai nasabah"),
    "Months_Inactive_12_mon": ("Bulan tidak aktif", "Dalam 12 bulan terakhir"),
    "Contacts_Count_12_mon": ("Jumlah kontak ke bank", "Dalam 12 bulan terakhir"),
    "Credit_Limit": ("Limit kredit", "Dalam USD"),
    "Total_Revolving_Bal": ("Saldo revolving", "Saldo belum lunas, dalam USD"),
    "Total_Trans_Amt": ("Total nominal transaksi", "12 bulan terakhir, dalam USD"),
    "Total_Trans_Ct": ("Jumlah transaksi", "12 bulan terakhir"),
    "Total_Amt_Chng_Q4_Q1": ("Perubahan nominal Q4 ke Q1", "Rasio nominal kuartal 4 dibanding kuartal 1"),
    "Total_Ct_Chng_Q4_Q1": ("Perubahan jumlah Q4 ke Q1", "Rasio jumlah transaksi kuartal 4 dibanding kuartal 1"),
    "Avg_Open_To_Buy": ("Sisa limit", "Dihitung otomatis"),
    "Avg_Utilization_Ratio": ("Rasio penggunaan kartu", "Dihitung otomatis"),
}

# 6. Penjelasan tiap fitur (dipakai untuk tombol ? dan halaman Tentang)
INFO = {
    "Customer_Age": "Usia nasabah dalam tahun.",
    "Gender": "Jenis kelamin nasabah (M laki-laki, F perempuan).",
    "Dependent_count": "Jumlah orang yang ditanggung nasabah, misalnya anak atau orang tua.",
    "Education_Level": "Pendidikan terakhir nasabah. Unknown berarti datanya tidak tercatat.",
    "Marital_Status": "Status pernikahan nasabah.",
    "Income_Category": "Kisaran pendapatan tahunan nasabah dalam dolar AS.",
    "Card_Category": "Jenis kartu yang dipakai. Blue paling dasar, Platinum paling tinggi.",
    "Months_on_book": "Sudah berapa bulan nasabah menjadi nasabah bank.",
    "Total_Relationship_Count": "Total produk bank yang dipakai nasabah, misalnya kartu kredit, tabungan, dan deposito.",
    "Months_Inactive_12_mon": "Jumlah bulan tanpa aktivitas dalam 12 bulan terakhir.",
    "Contacts_Count_12_mon": "Berapa kali nasabah menghubungi bank dalam 12 bulan terakhir.",
    "Credit_Limit": "Batas maksimal kredit yang boleh dipakai nasabah.",
    "Total_Revolving_Bal": "Saldo tagihan yang belum dilunasi dan terbawa ke bulan berikutnya.",
    "Avg_Open_To_Buy": "Sisa limit yang masih bisa dipakai. Dihitung otomatis dari limit dikurangi saldo revolving.",
    "Total_Amt_Chng_Q4_Q1": "Perbandingan total nominal transaksi kuartal 4 terhadap kuartal 1. Di bawah 1 berarti nominal belanja menurun.",
    "Total_Trans_Amt": "Total nominal semua transaksi dalam 12 bulan terakhir.",
    "Total_Trans_Ct": "Jumlah transaksi dalam 12 bulan terakhir.",
    "Total_Ct_Chng_Q4_Q1": "Perbandingan jumlah transaksi kuartal 4 terhadap kuartal 1. Di bawah 1 berarti transaksi makin jarang.",
    "Avg_Utilization_Ratio": "Persentase limit yang terpakai. Dihitung otomatis dari saldo revolving dibagi limit.",
}

STEP = {"Credit_Limit": 50, "Total_Revolving_Bal": 10, "Total_Trans_Amt": 10,
        "Total_Amt_Chng_Q4_Q1": 0.01, "Total_Ct_Chng_Q4_Q1": 0.01}
GRUP = [
    {"id": "profil", "judul": "Profil Nasabah",
     "fields": ["Customer_Age", "Gender", "Dependent_count", "Education_Level",
                "Marital_Status", "Income_Category"]},
    {"id": "kartu", "judul": "Kartu dan Hubungan",
     "fields": ["Card_Category", "Months_on_book", "Total_Relationship_Count",
                "Months_Inactive_12_mon", "Contacts_Count_12_mon",
                "Credit_Limit", "Total_Revolving_Bal"]},
    {"id": "transaksi", "judul": "Aktivitas Transaksi",
     "fields": ["Total_Trans_Amt", "Total_Trans_Ct",
                "Total_Amt_Chng_Q4_Q1", "Total_Ct_Chng_Q4_Q1"]},
]

SARAN = {
    "rendah": "Risiko rendah. Pertahankan hubungan lewat layanan rutin dan penawaran yang sesuai kebutuhan nasabah.",
    "sedang": "Risiko sedang. Pantau aktivitas transaksi dan tawarkan program loyalitas atau penyesuaian limit.",
    "tinggi": "Risiko tinggi. Segera hubungi nasabah dan tawarkan promo atau layanan khusus agar tidak berhenti memakai kartu.",
}


# 7. Bangun struktur form dari metadata
def bangun_form():
    hasil = []
    for g in GRUP:
        item = []
        for f in g["fields"]:
            label, hint = LABEL[f]
            if f in meta["cat_cols"]:
                item.append({"name": f, "label": label, "hint": hint, "info": INFO[f],
                             "tipe": "kat", "opsi": urutkan(f, meta["cat_cols"][f])})
            else:
                n = meta["num_cols"][f]
                item.append({"name": f, "label": label, "hint": hint, "info": INFO[f],
                             "tipe": "num", "min": n["min"], "max": n["max"],
                             "step": STEP.get(f, 1), "nilai": round(n["median"], 2)})
        hasil.append({"id": g["id"], "judul": g["judul"], "item": item})
    return hasil


# 8. Indikator bantu: aturan sederhana dari input, bukan penjelasan internal model
def cari_alasan(b):
    med = {k: v["median"] for k, v in meta["num_cols"].items()}
    a = []
    if b["Total_Trans_Ct"] < med["Total_Trans_Ct"]:
        a.append("Jumlah transaksi lebih rendah dari nasabah pada umumnya")
    if b["Total_Trans_Amt"] < med["Total_Trans_Amt"]:
        a.append("Total nominal transaksi lebih rendah dari nasabah pada umumnya")
    if b["Total_Ct_Chng_Q4_Q1"] < med["Total_Ct_Chng_Q4_Q1"]:
        a.append("Jumlah transaksi kuartal 4 menurun dibanding kuartal 1")
    if b["Months_Inactive_12_mon"] >= 3:
        a.append("Cukup banyak bulan tanpa aktivitas dalam 12 bulan terakhir")
    if b["Contacts_Count_12_mon"] >= 3:
        a.append("Sering menghubungi bank dalam 12 bulan terakhir")
    if b["Total_Relationship_Count"] <= 2:
        a.append("Produk bank yang dipakai hanya sedikit")
    if not a:
        a.append("Tidak ada indikator risiko yang menonjol dari data yang dimasukkan")
    return a[:4]


# 9. Analisis otomatis untuk halaman Eksperimen (dihitung dari meta.json)
def buat_analisis():
    a = meta["scenario_a"]
    acc = [r["acc_test"] for r in a]
    top = max(a, key=lambda r: r["acc_test"])
    r100 = next((r for r in a if r["n_estimators"] == 100), a[0])
    r500 = a[-1]
    sel_semua = (acc[-1] - acc[0]) * 100
    sel_100 = (r500["acc_test"] - r100["acc_test"]) * 100
    teks_a = ("Dari %d ke %d pohon, akurasi testing berubah %+.2f poin persentase. "
              "Dari %d ke %d pohon, perubahannya %+.2f poin. "
              % (a[0]["n_estimators"], r500["n_estimators"], sel_semua,
                 r100["n_estimators"], r500["n_estimators"], sel_100))
    if abs(sel_100) < 0.5:
        teks_a += "Setelah 100 pohon peningkatannya sangat kecil, jadi menambah pohon tidak lagi memberi manfaat berarti. "
    else:
        teks_a += "Setelah 100 pohon masih ada perubahan yang cukup terlihat. "
    teks_a += "Akurasi testing tertinggi ada di %d pohon (%.2f%%)." % (top["n_estimators"], top["acc_test"] * 100)

    b = meta["scenario_b"]
    gap = max(b, key=lambda r: r["selisih"])
    best = next(r for r in b if r["max_depth"] == meta["best"]["max_depth"])
    teks_b = ("Selisih akurasi training dan testing paling besar ada di max_depth %s "
              "(%.2f poin persentase, training %.2f%%, testing %.2f%%). "
              % (gap["max_depth"], gap["selisih"] * 100, gap["acc_train"] * 100, gap["acc_test"] * 100))
    if gap["selisih"] > 0.05:
        teks_b += "Selisih sebesar ini menandakan model mulai overfitting di kedalaman tersebut. "
    else:
        teks_b += "Selisihnya masih kecil, jadi belum terlihat overfitting yang kuat. "
    teks_b += "Model terbaik memakai max_depth %s dengan selisih %.2f poin persentase." % (
        best["max_depth"], best["selisih"] * 100)

    t = meta["importance_top10"][:3]
    total = sum(r["Importance"] for r in t) * 100
    teks_fi = ("Tiga fitur teratas adalah %s, dengan total kontribusi %.1f%% dari seluruh nilai importance."
               % (", ".join(r["Feature"].replace("_", " ") for r in t), total))
    return {"a": teks_a, "b": teks_b, "fi": teks_fi}


# 10. Halaman
@app.route("/")
def index():
    return render_template("index.html", meta=meta)


@app.route("/prediksi")
def prediksi():
    return render_template("prediksi.html", grup=bangun_form(), contoh=meta["contoh"])


@app.route("/eksperimen")
def eksperimen():
    return render_template("eksperimen.html", meta=meta,
                           analisis=buat_analisis(), catatan=CATATAN)


@app.route("/tentang")
def tentang():
    kamus = []
    for f in FITUR:
        kamus.append({"kode": f, "label": LABEL[f][0], "arti": INFO[f]})
    return render_template("tentang.html", meta=meta, kamus=kamus)


# 11. API prediksi
@app.route("/api/predict", methods=["POST"])
def api_predict():
    data = request.get_json(silent=True) or {}
    try:
        baris = {}
        for f in FITUR:
            if f in meta["cat_cols"]:
                nilai = str(data[f])
                if nilai not in meta["cat_cols"][f]:
                    raise ValueError("nilai " + f + " tidak dikenal")
                baris[f] = nilai
            elif f not in TURUNAN:
                baris[f] = float(data[f])

        limit = baris["Credit_Limit"]
        rev = baris["Total_Revolving_Bal"]
        baris["Avg_Open_To_Buy"] = max(limit - rev, 0.0)
        baris["Avg_Utilization_Ratio"] = min(rev / limit, 1.0) if limit > 0 else 0.0
        X = pd.DataFrame([baris])[FITUR]
    except (KeyError, ValueError, TypeError) as e:
        return jsonify({"ok": False, "pesan": "Data tidak lengkap atau tidak valid: " + str(e)}), 400

    proba = float(model.predict_proba(X)[0][1])
    level = "rendah" if proba < 0.30 else "sedang" if proba < 0.60 else "tinggi"
    label = "Berpotensi berhenti (churn)" if proba >= 0.5 else "Cenderung bertahan"
    return jsonify({"ok": True, "probabilitas": round(proba, 4),
                    "level": level, "label": label, "saran": SARAN[level],
                    "alasan": cari_alasan(baris)})


if __name__ == "__main__":
    app.run(debug=True)