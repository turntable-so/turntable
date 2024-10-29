"use client";
import { InputRule as F } from "@tiptap/core";
import { Extension as C } from "@tiptap/core";
import { Color as G } from "@tiptap/extension-color";
import _ from "@tiptap/extension-highlight";
import Q from "@tiptap/extension-horizontal-rule";
import De from "@tiptap/extension-image";
import qe from "@tiptap/extension-link";
import Y from "@tiptap/extension-placeholder";
import { TaskItem as We } from "@tiptap/extension-task-item";
import { TaskList as Ge } from "@tiptap/extension-task-list";
import V from "@tiptap/extension-text-style";
import X from "@tiptap/extension-underline";
import Ve from "@tiptap/starter-kit";
import { Markdown as J } from "tiptap-markdown";
var x = C.create({
    name: "CustomKeymap",
    addCommands() {
      return {
        selectTextWithinNodeBoundaries:
          () =>
          ({ editor: e, commands: o }) => {
            const { state: t } = e,
              { tr: r } = t,
              n = r.selection.$from.start(),
              i = r.selection.$to.end();
            return o.setTextSelection({ from: n, to: i });
          },
      };
    },
    addKeyboardShortcuts() {
      return {
        "Mod-a": ({ editor: e }) => {
          const { state: o } = e,
            { tr: t } = o,
            r = t.selection.from,
            n = t.selection.to,
            i = t.selection.$from.start(),
            s = t.selection.$to.end();
          return r > i || n < s
            ? (e.chain().selectTextWithinNodeBoundaries().run(), !0)
            : !1;
        },
      };
    },
  }),
  p = x;
import { useCurrentEditor as b } from "@tiptap/react";
import E from "react-moveable";
import { jsx as T } from "react/jsx-runtime";
var I = () => {
  const { editor: e } = b();
  if (!e?.isActive("image")) return null;
  const o = () => {
    const t = document.querySelector(".ProseMirror-selectednode");
    if (t) {
      const r = e.state.selection,
        n = e.commands.setImage;
      n({
        src: t.src,
        width: Number(t.style.width.replace("px", "")),
        height: Number(t.style.height.replace("px", "")),
      }),
        e.commands.setNodeSelection(r.from);
    }
  };
  return T(E, {
    target: document.querySelector(".ProseMirror-selectednode"),
    container: null,
    origin: !1,
    edge: !1,
    throttleDrag: 0,
    keepRatio: !0,
    resizable: !0,
    throttleResize: 0,
    onResize: ({ target: t, width: r, height: n, delta: i }) => {
      i[0] && (t.style.width = `${r}px`), i[1] && (t.style.height = `${n}px`);
    },
    onResizeEnd: () => {
      o();
    },
    scalable: !0,
    throttleScale: 0,
    renderDirections: ["w", "e"],
    onScale: ({ target: t, transform: r }) => {
      t.style.transform = r;
    },
  });
};
import A from "@tiptap/extension-image";
var k = A.extend({
    name: "image",
    addAttributes() {
      return {
        ...this.parent?.(),
        width: { default: null },
        height: { default: null },
      };
    },
  }),
  S = k;
import {
  markInputRule as H,
  mergeAttributes as P,
  markPasteRule as v,
  Mark as w,
} from "@tiptap/core";
import tt from "@tiptap/extension-character-count";
import rt from "@tiptap/extension-code-block-lowlight";
import it from "@tiptap/extension-youtube";
import at from "tiptap-extension-global-drag-handle";
var M = /(?:^|\s)((?:==)((?:[^~=]+))(?:==))$/,
  N = /(?:^|\s)((?:==)((?:[^~=]+))(?:==))/g,
  ae = w.create({
    name: "ai-highlight",
    addOptions() {
      return { HTMLAttributes: {} };
    },
    addAttributes() {
      return {
        color: {
          default: null,
          parseHTML: (e) =>
            e.getAttribute("data-color") || e.style.backgroundColor,
          renderHTML: (e) =>
            e.color
              ? {
                  "data-color": e.color,
                  style: `background-color: ${e.color}; color: inherit`,
                }
              : {},
        },
      };
    },
    parseHTML() {
      return [{ tag: "mark" }];
    },
    renderHTML({ HTMLAttributes: e }) {
      return ["mark", P(this.options.HTMLAttributes, e), 0];
    },
    addCommands() {
      return {
        setAIHighlight:
          (e) =>
          ({ commands: o }) =>
            o.setMark(this.name, e),
        toggleAIHighlight:
          (e) =>
          ({ commands: o }) =>
            o.toggleMark(this.name, e),
        unsetAIHighlight:
          () =>
          ({ commands: e }) =>
            e.unsetMark(this.name),
      };
    },
    addKeyboardShortcuts() {
      return { "Mod-Shift-h": () => this.editor.commands.toggleAIHighlight() };
    },
    addInputRules() {
      return [H({ find: M, type: this.type })];
    },
    addPasteRules() {
      return [v({ find: N, type: this.type })];
    },
  }),
  me = (e) => {
    const o = e.state.tr;
    o.removeMark(
      0,
      e.state.doc.nodeSize - 2,
      e.state.schema.marks["ai-highlight"],
    ),
      e.view.dispatch(o);
  },
  de = (e, o) => {
    e.chain()
      .setAIHighlight({ color: o ?? "#c1ecf970" })
      .run();
  };
import { Extension as q } from "@tiptap/core";
import { ReactRenderer as B } from "@tiptap/react";
import U from "@tiptap/suggestion";
import { Command as u } from "cmdk";
import { useAtom as L, useSetAtom as h } from "jotai";
import { atom as g } from "jotai";
import { forwardRef as K, createContext as O, useEffect as l } from "react";
import W from "tippy.js";
var d = g(""),
  f = g(null);
import { createStore as z } from "jotai";
var c = z();
import { jsxs as $, jsx as m } from "react/jsx-runtime";
var y = O({}),
  R = ({ query: e, range: o }) => {
    const t = h(d, { store: c }),
      r = h(f, { store: c });
    return (
      l(() => {
        t(e);
      }, [e, t]),
      l(() => {
        r(o);
      }, [o, r]),
      l(() => {
        const n = ["ArrowUp", "ArrowDown", "Enter"],
          i = (s) => {
            if (n.includes(s.key)) {
              s.preventDefault();
              const a = document.querySelector("#slash-command");
              return (
                a &&
                  a.dispatchEvent(
                    new KeyboardEvent("keydown", {
                      key: s.key,
                      cancelable: !0,
                      bubbles: !0,
                    }),
                  ),
                !1
              );
            }
          };
        return (
          document.addEventListener("keydown", i),
          () => {
            document.removeEventListener("keydown", i);
          }
        );
      }, []),
      m(y.Consumer, { children: (n) => m(n.Out, {}) })
    );
  },
  D = K(({ children: e, className: o, ...t }, r) => {
    const [n, i] = L(d);
    return m(y.Consumer, {
      children: (s) =>
        m(s.In, {
          children: $(u, {
            ref: r,
            onKeyDown: (a) => {
              a.stopPropagation();
            },
            id: "slash-command",
            className: o,
            ...t,
            children: [
              m(u.Input, {
                value: n,
                onValueChange: i,
                style: { display: "none" },
              }),
              e,
            ],
          }),
        }),
    });
  }),
  xe = u.List;
D.displayName = "EditorCommand";
var we = q.create({
    name: "slash-command",
    addOptions() {
      return {
        suggestion: {
          char: "/",
          command: ({ editor: e, range: o, props: t }) => {
            t.command({ editor: e, range: o });
          },
        },
      };
    },
    addProseMirrorPlugins() {
      return [U({ editor: this.editor, ...this.options.suggestion })];
    },
  }),
  He = () => {
    let e = null,
      o = null;
    return {
      onStart: (t) => {
        e = new B(R, { props: t, editor: t.editor });
        const { selection: r } = t.editor.state;
        if (r.$from.node(r.$from.depth).type.name === "codeBlock") return !1;
        o = W("body", {
          getReferenceClientRect: t.clientRect,
          appendTo: () => document.body,
          content: e.element,
          showOnCreate: !0,
          interactive: !0,
          trigger: "manual",
          placement: "bottom-start",
        });
      },
      onUpdate: (t) => {
        e?.updateProps(t),
          o?.[0]?.setProps({ getReferenceClientRect: t.clientRect });
      },
      onKeyDown: (t) =>
        t.event.key === "Escape" ? (o?.[0]?.hide(), !0) : e?.ref?.onKeyDown(t),
      onExit: () => {
        o?.[0]?.destroy(), e?.destroy();
      },
    };
  },
  ve = (e) => e,
  Pe = (e) => {
    if (
      ["ArrowUp", "ArrowDown", "Enter"].includes(e.key) &&
      document.querySelector("#slash-command")
    )
      return !0;
  };
var mt = Y.configure({
    placeholder: ({ node: e }) =>
      e.type.name === "heading"
        ? `Heading ${e.attrs.level}`
        : "Press '/' for commands",
    includeChildren: !0,
  }),
  dt = [
    X,
    V,
    G,
    _.configure({ multicolor: !0 }),
    J.configure({ html: !1, transformCopiedText: !0 }),
    p,
  ],
  ct = Q.extend({
    addInputRules() {
      return [
        new F({
          find: /^(?:---|—-|___\s|\*\*\*\s)$/u,
          handler: ({ state: e, range: o }) => {
            const t = {},
              { tr: r } = e,
              n = o.from,
              i = o.to;
            r.insert(n - 1, this.type.create(t)).delete(
              r.mapping.map(n),
              r.mapping.map(i),
            );
          },
        }),
      ];
    },
  });
export {
  I as a,
  S as b,
  M as c,
  N as d,
  ae as e,
  me as f,
  de as g,
  f as h,
  c as i,
  y as j,
  D as k,
  xe as l,
  we as m,
  He as n,
  ve as o,
  Pe as p,
  F as q,
  De as r,
  qe as s,
  We as t,
  Ge as u,
  Ve as v,
  tt as w,
  rt as x,
  it as y,
  at as z,
  mt as A,
  dt as B,
  ct as C,
};
