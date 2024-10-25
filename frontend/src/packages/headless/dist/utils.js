"use client";
import { Fragment as a } from "@tiptap/pm/model";
function i(t) {
  try {
    return new URL(t), !0;
  } catch {
    return !1;
  }
}
function l(t) {
  if (i(t)) return t;
  try {
    if (t.includes(".") && !t.includes(" "))
      return new URL(`https://${t}`).toString();
  } catch {
    return null;
  }
}
var g = (t, e) => {
    const r = [];
    t.state.doc.forEach((s, c) => (c >= e ? !1 : (r.push(s), !0)));
    const n = a.fromArray(r),
      o = t.state.doc.copy(n);
    return t.storage.markdown.serializer.serialize(o);
  },
  d = (t) => {
    const e = t.state.doc.content,
      r = t.state.doc.copy(e);
    return t.storage.markdown.serializer.serialize(r);
  };
export {
  d as getAllContent,
  g as getPrevText,
  l as getUrlFromString,
  i as isValidUrl,
};
