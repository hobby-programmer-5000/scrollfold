// Run: node --test web/i18n.test.mjs
// Web UI text: same keys/placeholders in en and ko; every key used by app.js / index.html exists.
import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { STRINGS } from "./i18n.js";
import * as S from "./split.js";

const here = (f) => new URL(f, import.meta.url);
const ph = (s) => new Set([...s.matchAll(/\{(\w+)\}/g)].map((m) => m[1]));

test("en and ko have the same keys and placeholders", () => {
  const en = STRINGS.en, ko = STRINGS.ko;
  assert.deepEqual(Object.keys(en).sort(), Object.keys(ko).sort());
  for (const k of Object.keys(en)) assert.deepEqual(ph(en[k]), ph(ko[k]), `placeholders differ for ${k}`);
});

test("every key used by the page exists", () => {
  const js = readFileSync(here("./app.js"), "utf8");
  const html = readFileSync(here("./index.html"), "utf8");
  const used = new Set([
    ...[...js.matchAll(/t\(state\.lang,\s*"([\w:]+)"/g)].map((m) => m[1]),
    ...[...html.matchAll(/data-i18n="([\w:]+)"/g)].map((m) => m[1]),
    ...Object.keys(S.RATIOS).map((k) => "hint_" + k),
    ...S.FIT_MODES.map((m) => "fit_" + m),
    "ratio_original",
  ]);
  // Error kinds thrown by split.js are shown with t(lang, e.kind, ...).
  const kinds = [...readFileSync(here("./split.js"), "utf8").matchAll(/new SplitError\([^;]*?, "(\w+)"/g)].map((m) => m[1]);
  for (const k of kinds) used.add(k);
  for (const k of [...used]) if (k.endsWith("_")) used.delete(k); // prefixes like "fit_" + mode, listed in full above
  assert.ok(used.size > 25);
  const missing = [...used].filter((k) => !(k in STRINGS.en));
  assert.deepEqual(missing, []);
});
