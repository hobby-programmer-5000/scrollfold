// Run: node --test web/
import test from "node:test";
import assert from "node:assert/strict";
import * as S from "./split.js";

test("equal widths, centered trim (same as test_core)", () => {
  const b = S.stripBoxes(2003, 100, 20);
  assert.equal(b.length, 20);
  assert.deepEqual(new Set(b.map((x) => x[2] - x[0])), new Set([100]));
  assert.equal(b[0][0], 1);
  assert.equal(b.at(-1)[2], 2001);
});

test("count limits and too narrow", () => {
  assert.throws(() => S.stripBoxes(1000, 10, 0), S.SplitError);
  assert.throws(() => S.stripBoxes(1000, 10, 21), S.SplitError);
  assert.throws(() => S.stripBoxes(10, 10, 20), S.SplitError);
});

test("suggestCount matches core.py", () => {
  assert.equal(S.suggestCount(16000, 494, [3, 4]), 20);
  assert.equal(S.suggestCount(1500, 400, [3, 4]), 5);
  assert.equal(S.suggestCount(900, 1600, [3, 4]), 1);
  assert.equal(S.suggestCount(900, 1600, null), 20);
});

test("crop gives 3:4 strips; tall image cut top/bottom", () => {
  for (const n of [20, 7]) {
    const p = S.plan(16000, 494, n, [3, 4], "crop");
    const sw = S.stripBoxes(p.w, p.h, n)[0];
    assert.ok(Math.abs((sw[2] - sw[0]) / p.h - 0.75) < 0.01);
  }
  const t = S.plan(900, 1600, 2, [3, 4], "crop");
  assert.deepEqual([t.w, t.h], [900, 600]);
});

test("pad keeps source whole and centered", () => {
  const p = S.plan(900, 1600, 4, [3, 4], "blur");
  assert.ok(Math.abs(p.w / p.h - 3) < 0.01);
  assert.deepEqual(p.offset, [(p.w - 900) / 2, 0]);
});

test("safeName and strip names", () => {
  assert.equal(S.safeName('a:b*c?'), "a_b_c_");
  assert.equal(S.safeName("CON"), "_CON");
  assert.equal(S.safeName(" . "), "image");
  assert.equal(S.safeName("그림"), "그림");
  assert.equal(S.stripName(3, 20, "jpg"), "03.jpg");
});

test("zip has right structure and CRC", () => {
  assert.equal(S.crc32(new TextEncoder().encode("123456789")), 0xcbf43926);
  const z = S.makeZip([{ name: "01.png", data: new Uint8Array([1, 2, 3]) }]);
  const v = new DataView(z.buffer);
  assert.equal(v.getUint32(0, true), 0x04034b50);
  assert.equal(v.getUint32(z.length - 22, true), 0x06054b50);
});
