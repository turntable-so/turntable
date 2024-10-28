"use client";
var s = Object.defineProperty;
var l = Object.getOwnPropertyDescriptor;
var g = Object.getOwnPropertyNames;
var d = Object.prototype.hasOwnProperty;
var f = (t, e) => {
    for (var r in e) s(t, r, { get: e[r], enumerable: !0 });
  },
  m = (t, e, r, o) => {
    if ((e && typeof e == "object") || typeof e == "function")
      for (const n of g(e))
        !d.call(t, n) &&
          n !== r &&
          s(t, n, {
            get: () => e[n],
            enumerable: !(o = l(e, n)) || o.enumerable,
          });
    return t;
  };
var p = (t) => m(s({}, "__esModule", { value: !0 }), t);
var w = {};
f(w, {
  getAllContent: () => x,
  getPrevText: () => h,
  getUrlFromString: () => y,
  isValidUrl: () => a,
});
module.exports = p(w);
var c = require("@tiptap/pm/model");
function a(t) {
  try {
    return new URL(t), !0;
  } catch {
    return !1;
  }
}
function y(t) {
  if (a(t)) return t;
  try {
    if (t.includes(".") && !t.includes(" "))
      return new URL(`https://${t}`).toString();
  } catch {
    return null;
  }
}
var h = (t, e) => {
    const r = [];
    t.state.doc.forEach((i, u) => (u >= e ? !1 : (r.push(i), !0)));
    const o = c.Fragment.fromArray(r),
      n = t.state.doc.copy(o);
    return t.storage.markdown.serializer.serialize(n);
  },
  x = (t) => {
    const e = t.state.doc.content,
      r = t.state.doc.copy(e);
    return t.storage.markdown.serializer.serialize(r);
  };
0 &&
  (module.exports = {
    getAllContent,
    getPrevText,
    getUrlFromString,
    isValidUrl,
  });
