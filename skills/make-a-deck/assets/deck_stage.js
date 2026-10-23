/**
 * <deck-stage> — fixed-size slide shell that letterboxes to any viewport.
 *
 * Each direct child <section> is one slide, authored at a fixed pixel canvas
 * (1920×1080 by default) so layout never reflows: the whole stage is scaled by
 * a single CSS transform. Authoring at a fixed size is the point — a deck that
 * reflows is a web page, and slides projected at an unknown aspect ratio must
 * letterbox rather than rewrap.
 *
 *   <deck-stage width="1920" height="1080">
 *     <section data-screen-label="01 Title">…</section>
 *   </deck-stage>
 *   <script src="deck_stage.js"></script>
 *
 * Provides: scale-to-fit letterboxing, keyboard + tap/click navigation, a slide
 * counter, localStorage position, print-to-PDF (one slide per page), and an
 * optional speaker-notes panel from
 * <script type="application/json" id="speaker-notes">["…", "…"]</script>.
 *
 * Keys: → ↓ Space PageDown = next · ← ↑ PageUp = prev · Home/End = first/last
 *       F = fullscreen · S = speaker notes · P = print
 */
(() => {
  "use strict";

  const STYLE = `
    deck-stage {
      position: fixed; inset: 0; display: block; overflow: hidden;
      background: #111; --deck-scale: 1;
    }
    deck-stage > section {
      position: absolute; top: 50%; left: 50%;
      width: var(--deck-w); height: var(--deck-h);
      transform: translate(-50%, -50%) scale(var(--deck-scale));
      transform-origin: center center;
      overflow: hidden; background: #fff;
      display: none;
    }
    deck-stage > section[data-active] { display: block; }

    .deck-counter {
      position: fixed; right: 16px; bottom: 14px; z-index: 10;
      font: 500 13px/1 ui-monospace, SFMono-Regular, Menlo, monospace;
      color: rgba(255,255,255,.65); background: rgba(0,0,0,.45);
      padding: 6px 10px; border-radius: 999px; pointer-events: none;
      -webkit-user-select: none; user-select: none;
    }
    .deck-notes {
      position: fixed; left: 0; right: 0; bottom: 0; z-index: 11;
      max-height: 38vh; overflow: auto; padding: 20px 28px;
      background: rgba(17,17,17,.96); color: #EDEDED;
      font: 15px/1.6 ui-sans-serif, system-ui, sans-serif;
      border-top: 1px solid rgba(255,255,255,.14);
    }
    .deck-notes[hidden] { display: none; }

    @media print {
      @page { size: landscape; margin: 0; }
      deck-stage { position: static; background: #fff; }
      deck-stage > section {
        display: block !important; position: relative;
        top: auto; left: auto; transform: none;
        page-break-after: always; break-after: page;
      }
      .deck-counter, .deck-notes { display: none !important; }
    }
  `;

  class DeckStage extends HTMLElement {
    connectedCallback() {
      // Guard against a double upgrade if the script is included twice.
      if (this._ready) return;
      this._ready = true;

      this.width = Number(this.getAttribute("width")) || 1920;
      this.height = Number(this.getAttribute("height")) || 1080;
      this.style.setProperty("--deck-w", this.width + "px");
      this.style.setProperty("--deck-h", this.height + "px");

      this.slides = [...this.children].filter((el) => el.tagName === "SECTION");
      if (!this.slides.length) return;

      this.storageKey = "deck:" + (location.pathname || "index");
      this.notes = this._readNotes();

      this._buildChrome();
      this._bind();

      this.go(this._restore(), { replace: true });
      this._fit();
    }

    // ---- navigation ------------------------------------------------------

    get index() {
      return this._index ?? 0;
    }

    go(n, { replace = false } = {}) {
      const next = Math.max(0, Math.min(this.slides.length - 1, n));
      this.slides.forEach((s, i) =>
        i === next ? s.setAttribute("data-active", "") : s.removeAttribute("data-active"),
      );
      this._index = next;
      this._counter.textContent = `${next + 1} / ${this.slides.length}`;
      this._renderNotes();
      if (!replace) this._persist();
      this.dispatchEvent(
        new CustomEvent("deck:change", { detail: { index: next }, bubbles: true }),
      );
    }

    next() { this.go(this.index + 1); }
    prev() { this.go(this.index - 1); }

    // ---- scaling ---------------------------------------------------------

    /**
     * Letterbox: one scale factor, the smaller of the two axis ratios, so the
     * slide always fits entirely and keeps its aspect ratio. Never scale past
     * the authored size — upscaling a 1920px canvas on a 4K display softens
     * text for no gain.
     */
    _fit() {
      const scale = Math.min(
        window.innerWidth / this.width,
        window.innerHeight / this.height,
        1,
      );
      this.style.setProperty("--deck-scale", String(scale));
    }

    // ---- persistence -----------------------------------------------------

    _persist() {
      try {
        localStorage.setItem(this.storageKey, String(this.index));
      } catch {
        // Private browsing or a disabled store: position just won't survive.
      }
    }

    _restore() {
      const fromHash = Number(location.hash.replace("#", ""));
      if (Number.isInteger(fromHash) && fromHash > 0) return fromHash - 1;
      try {
        return Number(localStorage.getItem(this.storageKey)) || 0;
      } catch {
        return 0;
      }
    }

    // ---- speaker notes ---------------------------------------------------

    _readNotes() {
      const tag = document.getElementById("speaker-notes");
      if (!tag) return null;
      try {
        const parsed = JSON.parse(tag.textContent);
        return Array.isArray(parsed) ? parsed : null;
      } catch {
        console.warn("[deck-stage] #speaker-notes is not valid JSON; ignoring.");
        return null;
      }
    }

    _renderNotes() {
      if (!this._notesEl) return;
      this._notesEl.textContent = this.notes?.[this.index] ?? "";
    }

    // ---- chrome and events ----------------------------------------------

    _buildChrome() {
      const style = document.createElement("style");
      style.textContent = STYLE;
      document.head.appendChild(style);

      this._counter = document.createElement("div");
      this._counter.className = "deck-counter";
      document.body.appendChild(this._counter);

      if (this.notes) {
        this._notesEl = document.createElement("div");
        this._notesEl.className = "deck-notes";
        this._notesEl.hidden = true;
        document.body.appendChild(this._notesEl);
      }
    }

    _bind() {
      addEventListener("resize", () => this._fit());

      addEventListener("keydown", (e) => {
        if (e.metaKey || e.ctrlKey || e.altKey) return;
        const key = e.key;
        if (["ArrowRight", "ArrowDown", " ", "PageDown"].includes(key)) {
          e.preventDefault();
          this.next();
        } else if (["ArrowLeft", "ArrowUp", "PageUp"].includes(key)) {
          e.preventDefault();
          this.prev();
        } else if (key === "Home") {
          e.preventDefault();
          this.go(0);
        } else if (key === "End") {
          e.preventDefault();
          this.go(this.slides.length - 1);
        } else if (key === "f" || key === "F") {
          document.fullscreenElement
            ? document.exitFullscreen()
            : document.documentElement.requestFullscreen?.();
        } else if ((key === "s" || key === "S") && this._notesEl) {
          this._notesEl.hidden = !this._notesEl.hidden;
        } else if (key === "p" || key === "P") {
          print();
        }
      });

      // Click/tap: right two-thirds advances, left third goes back. Ignore
      // clicks on genuinely interactive content so embedded demos still work.
      this.addEventListener("click", (e) => {
        if (e.target.closest("a, button, input, select, textarea, [data-no-nav]")) return;
        e.clientX > innerWidth / 3 ? this.next() : this.prev();
      });
    }
  }

  customElements.define("deck-stage", DeckStage);
})();
