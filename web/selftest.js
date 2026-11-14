// Web UI self-test. Open selftest.html (served by server.py or any static server).
// Drives index.html#selftest in an iframe and checks the flows that were tested by hand.
// The page title becomes "PASS n/n" or "FAIL k/n" so tools/web_selftest.py (or a person) can read the result.
import { STRINGS } from "./i18n.js";

const log = (s) => { document.getElementById("log").textContent += s + "\n"; };
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function canvasFile(name, w, h, color = "#3a7") {
  const c = document.createElement("canvas");
  c.width = w; c.height = h;
  const g = c.getContext("2d");
  g.fillStyle = color; g.fillRect(0, 0, w, h);
  g.fillStyle = "#fff"; g.fillRect(w / 3, h / 3, w / 3, h / 3);
  const blob = await new Promise((r) => c.toBlob(r, "image/png"));
  return new File([blob], name, { type: "image/png" });
}

async function main() {
  const frame = document.getElementById("app");
  await new Promise((r) => frame.addEventListener("load", r, { once: true }));
  const w = frame.contentWindow, d = frame.contentDocument;
  for (let i = 0; i < 50 && !w.scrollfold; i++) await sleep(100);
  const A = w.scrollfold;
  const $ = (id) => d.getElementById(id);
  const status = () => $("status").textContent;
  const isError = () => $("status").classList.contains("error");
  const pickRatio = (k) => [...d.querySelectorAll("input[name=ratio]")].find((x) => x.value === k).click();
  const setLang = (lang) => { if (A.state.lang !== lang) $("lang-btn").click(); };
  const tx = (key) => STRINGS[A.state.lang][key];
  const server = !!A.state.server;

  const tests = [
    ["English UI after switching", async () => {
      setLang("en");
      if ($("save").textContent !== (server ? tx("save_server") : tx("save_zip"))) throw new Error("save label");
    }],
    ["accepted formats shown before picking", async () => {
      if (!$("accepts").textContent.includes("PNG")) throw new Error($("accepts").textContent);
      if (server !== $("accepts").textContent.includes("TIFF")) throw new Error("server formats mismatch");
    }],
    ["empty file -> specific inline error", async () => {
      await A.load(new File([], "empty.png"));
      if (!isError() || status() !== tx("empty")) throw new Error(status());
    }],
    ["text file -> not an image", async () => {
      await A.load(new File(["hello"], "fake.png", { type: "image/png" }));
      if (!isError() || !status().startsWith(tx(server ? "not_image" : "not_image_static").slice(0, 20))) throw new Error(status());
    }],
    ["19px wide with 20 strips -> suggests 19", async () => {
      await A.load(await canvasFile("narrow.png", 19, 400));
      pickRatio("original");
      $("count").value = 20; $("count").dispatchEvent(new Event("change"));
      if (!isError() || !status().includes("19 strips or fewer")) throw new Error(status());
    }],
    ["10:1 panorama -> auto 20 strips of 1:2", async () => {
      await A.load(await canvasFile("pano.png", 8000, 800));
      pickRatio("1:2");
      if ($("count").value !== "20") throw new Error("count " + $("count").value);
      if (isError() || !status().includes("400×800")) throw new Error(status());
    }],
    ["strips are 20 JPEGs within X limits", async () => {
      $("optimize").checked = true;
      let n = 0;
      for await (const s of A.strips()) {
        n++;
        if (s.blob.type !== "image/jpeg" || s.blob.size > 5 * 1024 * 1024) throw new Error(s.name);
        const bm = await createImageBitmap(s.blob);
        if (bm.width !== 400 || bm.height !== 800) throw new Error(`${bm.width}x${bm.height}`);
      }
      if (n !== 20) throw new Error("n=" + n);
    }],
    ["tall photo with blur pad keeps the whole picture", async () => {
      await A.load(await canvasFile("tall.png", 900, 1600));
      pickRatio("1:2"); A.setFit("blur");
      $("count").value = 4; $("count").dispatchEvent(new Event("change"));
      if (!status().includes("800×1600")) throw new Error(status());
    }],
    ["cancel stops making strips", async () => {
      await A.load(await canvasFile("pano.png", 8000, 800));
      A.state.cancel = false;
      let n = 0, cancelled = false;
      try {
        for await (const _ of A.strips()) { n++; if (n === 3) A.state.cancel = true; }
      } catch (e) { cancelled = e.name === "Cancelled" && e.done === 3; }
      A.state.cancel = false;
      if (!cancelled) throw new Error("not cancelled at 3, n=" + n);
    }],
    ["Save + Esc cancels, focus returns to Save", async () => {
      $("save").click();
      w.dispatchEvent(new w.KeyboardEvent("keydown", { key: "Escape" }));
      for (let i = 0; i < 100 && A.state.busy; i++) await sleep(50);
      if (!status().startsWith("Cancelled")) throw new Error(status());
      if (!$("cancel").hidden) throw new Error("cancel still visible");
      if (d.activeElement !== $("save")) throw new Error("focus on " + d.activeElement?.id);
    }],
    ["Korean UI", async () => {
      setLang("ko");
      if ($("save").textContent !== (server ? STRINGS.ko.save_server : STRINGS.ko.save_zip)) throw new Error("ko label");
      setLang("en");
    }],
  ];

  let fails = 0;
  for (const [name, fn] of tests) {
    try { await fn(); log(`PASS  ${name}`); }
    catch (e) { fails++; log(`FAIL  ${name}: ${e.message}`); }
  }
  // Cancelled saves in local mode may have made one strip; that folder is reported in the status line.
  log(`\n${tests.length - fails}/${tests.length} passed (${server ? "local server mode" : "browser-only mode"})`);
  document.title = fails ? `FAIL ${fails}/${tests.length}` : `PASS ${tests.length}/${tests.length}`;
}
main();
