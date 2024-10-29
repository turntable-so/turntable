"use client";
var u = Object.defineProperty;
var b = Object.getOwnPropertyDescriptor;
var P = Object.getOwnPropertyNames;
var S = Object.prototype.hasOwnProperty;
var x = (n, e) => {
    for (var o in e) u(n, o, { get: e[o], enumerable: !0 });
  },
  A = (n, e, o, t) => {
    if ((e && typeof e == "object") || typeof e == "function")
      for (const a of P(e))
        !S.call(n, a) &&
          a !== o &&
          u(n, a, {
            get: () => e[a],
            enumerable: !(t = b(e, a)) || t.enumerable,
          });
    return n;
  };
var C = (n) => A(u({}, "__esModule", { value: !0 }), n);
var V = {};
x(V, {
  UploadImagesPlugin: () => h,
  createImageUpload: () => y,
  handleImageDrop: () => D,
  handleImagePaste: () => U,
});
module.exports = C(V);
var p = require("@tiptap/pm/state"),
  m = require("@tiptap/pm/view"),
  l = new p.PluginKey("upload-image"),
  h = ({ imageClass: n }) =>
    new p.Plugin({
      key: l,
      state: {
        init() {
          return m.DecorationSet.empty;
        },
        apply(e, o) {
          o = o.map(e.mapping, e.doc);
          const t = e.getMeta(this);
          if (t?.add) {
            const { id: a, pos: c, src: i } = t.add,
              r = document.createElement("div");
            r.setAttribute("class", "img-placeholder");
            const d = document.createElement("img");
            d.setAttribute("class", n), (d.src = i), r.appendChild(d);
            const s = m.Decoration.widget(c + 1, r, { id: a });
            o = o.add(e.doc, [s]);
          } else
            t?.remove &&
              (o = o.remove(
                o.find(void 0, void 0, (a) => a.id == t.remove.id),
              ));
          return o;
        },
      },
      props: {
        decorations(e) {
          return this.getState(e);
        },
      },
    });
function M(n, e) {
  const t = l.getState(n).find(void 0, void 0, (a) => a.id == e);
  return t.length ? t[0]?.from : null;
}
var y =
    ({ validateFn: n, onUpload: e }) =>
    (o, t, a) => {
      if (!n?.(o)) return;
      const i = {},
        r = t.state.tr;
      r.selection.empty || r.deleteSelection();
      const d = new FileReader();
      d.readAsDataURL(o),
        (d.onload = () => {
          r.setMeta(l, { add: { id: i, pos: a, src: d.result } }),
            t.dispatch(r);
        }),
        e(o).then(
          (s) => {
            const { schema: I } = t.state,
              f = M(t.state, i);
            if (f == null) return;
            const E = typeof s == "object" ? d.result : s,
              g = I.nodes.image?.create({ src: E });
            if (!g) return;
            const F = t.state.tr
              .replaceWith(f, f, g)
              .setMeta(l, { remove: { id: i } });
            t.dispatch(F);
          },
          () => {
            const s = t.state.tr.delete(a, a).setMeta(l, { remove: { id: i } });
            t.dispatch(s);
          },
        );
    },
  U = (n, e, o) => {
    if (e.clipboardData?.files.length) {
      e.preventDefault();
      const [t] = Array.from(e.clipboardData.files),
        a = n.state.selection.from;
      return t && o(t, n, a), !0;
    }
    return !1;
  },
  D = (n, e, o, t) => {
    if (!o && e.dataTransfer?.files.length) {
      e.preventDefault();
      const [a] = Array.from(e.dataTransfer.files),
        c = n.posAtCoords({ left: e.clientX, top: e.clientY });
      return a && t(a, n, c?.pos ?? -1), !0;
    }
    return !1;
  };
0 &&
  (module.exports = {
    UploadImagesPlugin,
    createImageUpload,
    handleImageDrop,
    handleImagePaste,
  });
