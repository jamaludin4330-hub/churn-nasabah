// menu mobile
const toggle = document.querySelector(".nav-toggle");
const links = document.querySelector(".nav-links");
if (toggle && links) {
  toggle.addEventListener("click", () => links.classList.toggle("buka"));
}

// muncul saat di-scroll
const pengamat = new IntersectionObserver((entri) => {
  entri.forEach((e) => {
    if (!e.isIntersecting) return;
    e.target.classList.add("show");
    e.target.querySelectorAll(".bar-fill").forEach((b) => { b.style.width = b.dataset.w + "%"; });
    e.target.querySelectorAll("[data-count]").forEach(hitungNaik);
    pengamat.unobserve(e.target);
  });
}, { threshold: 0.15 });
document.querySelectorAll(".reveal").forEach((el) => pengamat.observe(el));

// angka naik
function hitungNaik(el) {
  const target = parseFloat(el.dataset.count);
  const desimal = parseInt(el.dataset.decimals || "0", 10);
  const akhiran = el.dataset.suffix || "";
  const mulai = performance.now();
  const durasi = 1200;
  function frame(t) {
    const p = Math.min((t - mulai) / durasi, 1);
    const nilai = target * (1 - Math.pow(1 - p, 3));
    el.textContent = nilai.toLocaleString("en-US", {
      minimumFractionDigits: desimal, maximumFractionDigits: desimal }) + akhiran;
    if (p < 1) requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
}

// tombol tanda tanya untuk penjelasan fitur
document.querySelectorAll(".info-btn").forEach((b) => {
  b.addEventListener("click", () => {
    const t = document.getElementById(b.dataset.target);
    if (!t) return;
    t.classList.toggle("hidden");
    b.classList.toggle("on");
  });
});