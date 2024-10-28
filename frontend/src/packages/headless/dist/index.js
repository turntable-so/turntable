"use client";
import {} from "@tiptap/core";
import { useCurrentEditor as No } from "@tiptap/react";
import { EditorProvider as B } from "@tiptap/react";
import { Provider as M } from "jotai";
import { useRef as I, useMemo as N, forwardRef as h } from "react";
import { jsx as d } from "react/jsx-runtime";
import S from "tunnel-rat";
import {
  B as c,
  i as l,
  h as s,
  j as u,
  k as v,
  l as x,
} from "./chunk-RCJTUCCX.js";
var g = ({ children: e }) => {
    const o = I(S()).current;
    return d(M, {
      store: l,
      children: d(u.Provider, { value: o, children: e }),
    });
  },
  f = h(({ className: e, children: o, initialContent: i, ...r }, n) => {
    const t = N(() => [...c, ...(r.extensions ?? [])], [r.extensions]);
    return d("div", {
      ref: n,
      className: e,
      children: d(B, { ...r, content: i, extensions: t, children: o }),
    });
  });
f.displayName = "EditorContent";
import {
  useCurrentEditor as L,
  isNodeSelection as T,
  BubbleMenu as w,
} from "@tiptap/react";
import {
  useMemo as D,
  useRef as H,
  useEffect as O,
  forwardRef as W,
} from "react";
import { jsx as E } from "react/jsx-runtime";
var C = W(({ children: e, tippyOptions: o, ...i }, r) => {
  const { editor: n } = L(),
    t = H(null);
  O(() => {
    !t.current ||
      !o?.placement ||
      (t.current.setProps({ placement: o.placement }),
      t.current.popperInstance?.update());
  }, [o?.placement]);
  const p = D(
    () => ({
      shouldShow: ({ editor: m, state: y }) => {
        const { selection: a } = y,
          { empty: R } = a;
        return !(!m.isEditable || m.isActive("image") || R || T(a));
      },
      tippyOptions: {
        onCreate: (m) => {
          t.current = m;
        },
        moveTransition: "transform 0.15s ease-out",
        ...o,
      },
      ...i,
    }),
    [i, o],
  );
  return n
    ? E("div", { ref: r, children: E(w, { editor: n, ...p, children: e }) })
    : null;
});
C.displayName = "EditorBubble";
import { Slot as J } from "@radix-ui/react-slot";
import { useCurrentEditor as F } from "@tiptap/react";
import { forwardRef as A } from "react";
import { jsx as k } from "react/jsx-runtime";
var b = A(({ children: e, asChild: o, onSelect: i, ...r }, n) => {
  const { editor: t } = F(),
    p = o ? J : "div";
  return t ? k(p, { ref: n, ...r, onClick: () => i?.(t), children: e }) : null;
});
b.displayName = "EditorBubbleItem";
import { useCurrentEditor as G } from "@tiptap/react";
import { CommandEmpty as q, CommandItem as z } from "cmdk";
import { useAtomValue as K } from "jotai";
import { forwardRef as V } from "react";
import { jsx as U } from "react/jsx-runtime";
var P = V(({ children: e, onCommand: o, ...i }, r) => {
  const { editor: n } = G(),
    t = K(s);
  return !n || !t
    ? null
    : U(z, {
        ref: r,
        ...i,
        onSelect: () => o({ editor: n, range: t }),
        children: e,
      });
});
P.displayName = "EditorCommandItem";
var Q = q;
export {
  C as EditorBubble,
  b as EditorBubbleItem,
  v as EditorCommand,
  Q as EditorCommandEmpty,
  P as EditorCommandItem,
  x as EditorCommandList,
  f as EditorContent,
  g as EditorRoot,
  No as useEditor,
};
