# Churn Watch: Prediksi Churn Nasabah Kartu Kredit dengan Random Forest

Tugas Akhir 06 mata kuliah Pembelajaran Mesin (Modul 06: Algoritma Random Forest), Program Studi Teknik Informatika, Universitas Bale Bandung.

Proyek ini memprediksi nasabah kartu kredit yang berisiko berhenti memakai kartunya (churn) menggunakan algoritma Random Forest. Isinya notebook eksperimen (jumlah pohon dan kedalaman pohon), analisis feature importance, dan aplikasi web Flask untuk mencoba model.

## Tautan

| Keterangan | Tautan |
|---|---|
| Dataset (Kaggle) | https://www.kaggle.com/datasets/sakshigoyal7/credit-card-customers |
| Aplikasi web (deploy) | ISI_LINK_DEPLOY |
| Video demo (YouTube) | ISI_LINK_YOUTUBE |

## Hasil Singkat

Dataset: 10.127 nasabah, 19 fitur, proporsi churn 16,07%. Data dibagi 80% latih dan 20% uji (stratified, random_state 42), ketidakseimbangan kelas ditangani dengan class_weight balanced.

Model terbaik: 50 pohon, max_depth tanpa batas.

| Metrik (data uji) | Nilai |
|---|---|
| Akurasi | 95,66% |
| Precision churn | 0,879 |
| Recall churn | 0,846 |
| F1-score churn | 0,862 |
| ROC AUC | 0,983 |

Skenario A (jumlah pohon, max_depth bawaan):

| n_estimators | Akurasi training | Akurasi testing | F1 churn |
|---|---|---|---|
| 10 | 99,72 | 94,18 | 81,27 |
| 50 | 99,86 | 95,66 | 86,21 |
| 100 | 99,88 | 95,41 | 85,54 |
| 200 | 99,90 | 95,26 | 85,00 |
| 500 | 99,93 | 95,21 | 84,96 |

Skenario B (kedalaman pohon, n_estimators 50):

| max_depth | Akurasi training | Akurasi testing |
|---|---|---|
| 3 | 83,69 | 83,91 |
| 5 | 89,83 | 89,49 |
| 10 | 97,74 | 94,52 |
| 20 | 99,81 | 95,51 |
| Tanpa batas | 99,86 | 95,66 |

Fitur paling berpengaruh: Total_Trans_Amt (0,207), Total_Trans_Ct (0,201), Total_Revolving_Bal (0,100), Total_Ct_Chng_Q4_Q1 (0,090), dan Avg_Utilization_Ratio (0,065).

## Fitur Aplikasi Web

- Beranda: ringkasan proyek dan lima fitur teratas.
- Prediksi: form tiga langkah (profil, kartu dan hubungan, aktivitas transaksi), tombol contoh nasabah, skor risiko dalam bentuk gauge, saran tindakan, indikator bantu, dan riwayat lima prediksi terakhir.
- Eksperimen: grafik interaktif skenario A dan B, feature importance, classification report, confusion matrix, dan analisis otomatis.
- Tentang: latar belakang, penjelasan dataset dan kamus fitur, cara kerja Random Forest, cara membaca hasil, FAQ, dan batasan.

Web hanya memuat model yang sudah disimpan, tidak melatih ulang saat dibuka.

## Struktur Folder

```
TA06_Churn_RF/
    data/
        BankChurners.csv               (diunduh sendiri dari Kaggle, tidak ikut di repo)
    model/
        rf_churn.joblib                (model hasil notebook)
        meta.json                      (hasil eksperimen untuk web)
    static/
        css/style.css
        js/main.js
        js/prediksi.js
        img/                           (grafik hasil notebook)
    templates/
        index.html
        prediksi.html
        eksperimen.html
        tentang.html
    TA06_RandomForest_Churn.ipynb
    app.py
    requirements.txt
    .gitignore
    README.md
```

## Cara Menjalankan

Syarat: Python 3.10 atau lebih baru dan Git.

1. Clone repo dan masuk ke foldernya.

```
git clone LINK_REPO_INI
cd NAMA_FOLDER_REPO
```

2. Buat virtual environment dan install library.

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Di Mac atau Linux, aktifkan dengan `source venv/bin/activate`.

3. Jalankan aplikasi web.

```
python app.py
```

Buka http://127.0.0.1:5000 di browser.

Folder `model/` sudah ikut di repo, jadi web bisa langsung dipakai tanpa training.

## Cara Melatih Ulang Model (opsional)

1. Unduh `BankChurners.csv` dari tautan Kaggle di atas, taruh di folder `data/`.
2. Jalankan `jupyter notebook`, buka `TA06_RandomForest_Churn.ipynb`, lalu klik Run All.
3. Notebook akan membuat ulang `model/rf_churn.joblib`, `model/meta.json`, dan grafik di `static/img/`.
4. Restart `python app.py`.

## Endpoint API

`POST /api/predict` menerima JSON berisi 17 isian nasabah (Customer_Age, Gender, Dependent_count, Education_Level, Marital_Status, Income_Category, Card_Category, Months_on_book, Total_Relationship_Count, Months_Inactive_12_mon, Contacts_Count_12_mon, Credit_Limit, Total_Revolving_Bal, Total_Amt_Chng_Q4_Q1, Total_Trans_Amt, Total_Trans_Ct, Total_Ct_Chng_Q4_Q1). Sisa limit dan rasio pemakaian dihitung otomatis oleh server.

Contoh respons:

```json
{
  "ok": true,
  "probabilitas": 0.48,
  "level": "sedang",
  "label": "Cenderung bertahan",
  "saran": "Risiko sedang. ...",
  "alasan": ["..."]
}
```

Tingkat risiko: rendah (di bawah 30%), sedang (30% sampai 60%), tinggi (60% ke atas).

## Catatan Penting

- Skor risiko adalah keluaran model dari data historis, bukan kepastian. Gunakan sebagai bahan pertimbangan, bukan keputusan final.
- Bagian "indikator bantu" di halaman Prediksi adalah aturan sederhana yang membandingkan input dengan nilai tengah data, bukan penjelasan internal model.
- File model (joblib) peka terhadap versi scikit-learn. Pakai versi yang sama dengan saat training, yaitu yang tertulis di `requirements.txt`.
- Dataset berasal dari Kaggle dan tidak disertakan di repo ini. Ikuti ketentuan penggunaan dataset dari sumbernya.

```

## Penulis

Selsa Shafana Alfiyani (NIM 301240041), Teknik Informatika, Universitas Bale Bandung.
Dosen pengampu: Mohammad Bayu Anggara, S.Kom., M.Kom.

## Referensi Utama

- Breiman, L. (2001). Random Forests. Machine Learning, 45(1), 5-32.
- Pedregosa, F., dkk. (2011). Scikit-learn: Machine Learning in Python. Journal of Machine Learning Research, 12, 2825-2830.