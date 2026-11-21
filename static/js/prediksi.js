(function () {
  const form = document.getElementById("form-churn");
  if (!form) return;

  const panels = Array.from(document.querySelectorAll(".panel"));
  const stepEls = Array.from(document.querySelectorAll(".step-item"));
  const bar = document.getElementById("progress-bar");
  const btnBack = document.getElementById("btn-back");
  const btnNext = document.getElementById("btn-next");
  const btnPredict = document.getElementById("btn-predict");
  const kosong = document.getElementById("hasil-kosong");
  const isi = document.getElementById("hasil-isi");
  const arc = document.getElementById("g-val");
  const persenEl = document.getElementById("g-persen");
  const badge = document.getElementById("badge");
  const teks = document.getElementById("teks-hasil");
  const saran = document.getElementById("saran");
  const galat = document.getElementById("galat");
  const listRiwayat = document.getElementById("list-riwayat");
  const ARC = 251.3;
  let idx = 0;
  let riwayat = [];

  const fmt = (n) => Number(n).toLocaleString("en-US");

  // sinkron nilai slider dengan angka dan warna isi slider
  function sinkron(el) {
    const out = document.getElementById("out-" + el.name);
    const kecil = parseFloat(el.step) < 1;
    if (out) out.textContent = kecil ? Number(el.value).toFixed(2) : fmt(el.value);
    const rentang = Number(el.max) - Number(el.min);
    const persen = rentang > 0 ? ((el.value - el.min) / rentang) * 100 : 0;
    el.style.setProperty("--isi", persen + "%");
  }

  // sisa limit dan rasio penggunaan dihitung otomatis
  function turunan() {
    const limit = Number(form.elements["Credit_Limit"].value);
    const rev = form.elements["Total_Revolving_Bal"];
    rev.max = Math.min(Number(rev.dataset.max), limit);
    if (Number(rev.value) > Number(rev.max)) rev.value = rev.max;
    sinkron(rev);
    const sisa = Math.max(limit - Number(rev.value), 0);
    const rasio = limit > 0 ? Number(rev.value) / limit : 0;
    document.getElementById("t-sisa").textContent = fmt(Math.round(sisa));
    document.getElementById("t-rasio").textContent = (rasio * 100).toFixed(1) + "%";
  }

  function semuaSlider() {
    return Array.from(form.querySelectorAll("input[type=range]"));
  }

  function isiForm(data) {
    if (data.Credit_Limit !== undefined) {
      form.elements["Credit_Limit"].value = data.Credit_Limit;
      turunan();
    }
    Object.keys(data).forEach((k) => {
      const el = form.elements[k];
      if (el) el.value = data[k];
    });
    semuaSlider().forEach(sinkron);
    turunan();
  }

  function resetForm() {
    Array.from(form.elements).forEach((el) => {
      if (el.tagName === "SELECT") el.selectedIndex = 0;
      else if (el.dataset && el.dataset.default !== undefined) el.value = el.dataset.default;
    });
    semuaSlider().forEach((el) => { el.max = el.dataset.max; sinkron(el); });
    turunan();
    kosong.classList.remove("hidden");
    isi.classList.add("hidden");
    galat.classList.add("hidden");
    tampilLangkah(0);
  }

  function ambilData() {
    const data = {};
    Array.from(form.elements).forEach((el) => {
      if (!el.name) return;
      data[el.name] = el.type === "range" ? Number(el.value) : el.value;
    });
    return data;
  }

  // wizard 3 langkah
  function tampilLangkah(i) {
    idx = i;
    panels.forEach((p, n) => p.classList.toggle("active", n === i));
    stepEls.forEach((s, n) => {
      s.classList.toggle("active", n === i);
      s.classList.toggle("done", n < i);
    });
    bar.style.width = ((i + 1) / panels.length) * 100 + "%";
    btnBack.classList.toggle("hidden", i === 0);
    btnNext.classList.toggle("hidden", i === panels.length - 1);
    btnPredict.classList.toggle("hidden", i !== panels.length - 1);
  }

  btnNext.addEventListener("click", () => tampilLangkah(Math.min(idx + 1, panels.length - 1)));
  btnBack.addEventListener("click", () => tampilLangkah(Math.max(idx - 1, 0)));
  stepEls.forEach((s, n) => s.addEventListener("click", () => tampilLangkah(n)));

  form.addEventListener("input", (e) => {
    if (e.target.type === "range") sinkron(e.target);
    turunan();
  });

  // tombol contoh dan reset
  document.querySelectorAll("[data-preset]").forEach((b) => {
    b.addEventListener("click", () => {
      const jenis = b.dataset.preset;
      if (jenis === "reset") resetForm();
      else isiForm(CONTOH[jenis]);
    });
  });

  // animasi angka persen
  function naik(target) {
    const mulai = performance.now();
    function frame(t) {
      const p = Math.min((t - mulai) / 1100, 1);
      persenEl.textContent = Math.round(target * (1 - Math.pow(1 - p, 3))) + "%";
      if (p < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }

  function tampilHasil(j) {
    kosong.classList.add("hidden");
    isi.classList.remove("hidden");
    galat.classList.add("hidden");
    arc.style.strokeDashoffset = ARC;
    requestAnimationFrame(() => {
      arc.style.strokeDashoffset = ARC * (1 - j.probabilitas);
    });
    naik(j.probabilitas * 100);
    badge.className = "badge lvl-" + j.level;
    badge.textContent = "Risiko " + j.level;
    teks.textContent = j.label;
    saran.textContent = j.saran;
    if (window.innerWidth < 900) isi.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  function catat(data, j) {
    riwayat.unshift({ data: data, hasil: j, jam: new Date().toLocaleTimeString("id-ID", { hour: "2-digit", minute: "2-digit" }) });
    riwayat = riwayat.slice(0, 5);
    listRiwayat.innerHTML = "";
    riwayat.forEach((r) => {
      const li = document.createElement("li");
      const b = document.createElement("button");
      b.type = "button";
      b.innerHTML = "<span>" + r.jam + " - Risiko " + r.hasil.level + "</span><b>" +
        Math.round(r.hasil.probabilitas * 100) + "%</b>";
      b.addEventListener("click", () => { isiForm(r.data); tampilHasil(r.hasil); });
      li.appendChild(b);
      listRiwayat.appendChild(li);
    });
    document.getElementById("riwayat").classList.remove("hidden");
  }

  document.getElementById("hapus-riwayat").addEventListener("click", () => {
    riwayat = [];
    listRiwayat.innerHTML = "";
    document.getElementById("riwayat").classList.add("hidden");
  });

  // kirim ke API
  btnPredict.addEventListener("click", async () => {
    const data = ambilData();
    btnPredict.disabled = true;
    btnPredict.textContent = "Memproses";
    try {
      const res = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      const j = await res.json();
      if (!res.ok || !j.ok) throw new Error(j.pesan || "Terjadi kesalahan");
      tampilHasil(j);
      catat(data, j);
    } catch (err) {
      galat.textContent = err.message;
      galat.classList.remove("hidden");
    } finally {
      btnPredict.disabled = false;
      btnPredict.textContent = "Prediksi Sekarang";
    }
  });

  // awal
  semuaSlider().forEach(sinkron);
  turunan();
  tampilLangkah(0);
})();