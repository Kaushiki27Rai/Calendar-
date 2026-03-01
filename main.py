import tkinter as tk
from tkinter import ttk, messagebox
import calendar
import json
import os
from datetime import datetime, date, timedelta

# ── Constants ────────────────────────────────────────────────────────────────
DATA_FILE = "events.json"

COLORS = {
    "bg":         "#1A1D2E",
    "panel":      "#22263A",
    "card":       "#2A2F45",
    "border":     "#363B55",
    "accent":     "#7C5CBF",
    "accent2":    "#5B8AF0",
    "today":      "#5B8AF0",
    "today_text": "#FFFFFF",
    "text":       "#E2E4F0",
    "subtext":    "#8B90A8",
    "hover":      "#31374F",
    "danger":     "#E05C6A",
    "success":    "#4CAF82",
}

CATEGORIES = {
    "Study":    {"color": "#5B8AF0", "icon": "📚"},
    "Work":     {"color": "#F0915B", "icon": "💼"},
    "Personal": {"color": "#7C5CBF", "icon": "🌿"},
    "Health":   {"color": "#4CAF82", "icon": "❤️"},
    "Meetings": {"color": "#E05C6A", "icon": "🤝"},
}

PRIORITIES  = ["High", "Medium", "Low"]
STATUSES    = ["Pending", "In Progress", "Done"]
DAY_NAMES   = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MONTH_NAMES = [
    "January","February","March","April","May","June",
    "July","August","September","October","November","December"
]

FONT = "SF Pro Display" if os.name != "nt" else "Segoe UI"


# ── Helpers ───────────────────────────────────────────────────────────────────
def load_events():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, OSError):
            import shutil
            try:
                shutil.copy(DATA_FILE, DATA_FILE + ".broken")
            except Exception:
                pass
            return {}
    return {}

def save_events(events):
    with open(DATA_FILE, "w") as f:
        json.dump(events, f, indent=2)

def styled_btn(parent, text, bg, fg="#FFFFFF", cmd=None, padx=14, pady=6, size=11, bold=False):
    return tk.Button(
        parent, text=text, bg=bg, fg=fg,
        relief="flat", bd=0, padx=padx, pady=pady,
        cursor="hand2", activebackground=bg, activeforeground=fg,
        font=(FONT, size, "bold" if bold else "normal"),
        command=cmd
    )

# Light-background button with dark text — used for nav bar controls
def nav_btn(parent, text, cmd=None, padx=14, pady=5, size=11, bold=False):
    return tk.Button(
        parent, text=text,
        bg="#D8DCF0", fg="#1A1D2E",
        relief="flat", bd=0, padx=padx, pady=pady,
        cursor="hand2", activebackground="#C4C9E2", activeforeground="#1A1D2E",
        font=(FONT, size, "bold" if bold else "normal"),
        command=cmd
    )

def field_entry(parent, textvariable=None, width=None):
    kwargs = {"width": width} if width else {}
    return tk.Entry(
        parent,
        textvariable=textvariable,
        bg=COLORS["card"], fg=COLORS["text"],
        relief="flat", bd=0,
        insertbackground=COLORS["text"],
        font=(FONT, 12),
        highlightthickness=1,
        highlightcolor=COLORS["accent"],
        highlightbackground=COLORS["border"],
        **kwargs
    )

def section_label(parent, text):
    return tk.Label(
        parent, text=text,
        bg=COLORS["bg"], fg=COLORS["subtext"],
        font=(FONT, 9)
    )


# ── Add Event Dialog ──────────────────────────────────────────────────────────
class EventDialog(tk.Toplevel):
    def __init__(self, parent, date_str=None, on_save=None):
        super().__init__(parent)
        self.on_save = on_save
        self.configure(bg=COLORS["bg"])
        self.title("Add Event")
        self.resizable(False, False)
        self.grab_set()
        self.focus_set()

        w, h = 460, 580
        self.update_idletasks()
        px, py = parent.winfo_rootx(), parent.winfo_rooty()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        self.geometry(f"{w}x{h}+{px+(pw-w)//2}+{py+(ph-h)//2}")

        self._build(date_str or datetime.today().strftime("%Y-%m-%d"))

    def _build(self, date_str):
        hdr = tk.Frame(self, bg=COLORS["panel"])
        hdr.pack(fill="x")
        tk.Label(hdr, text="✦  New Event", bg=COLORS["panel"], fg=COLORS["text"],
                 font=(FONT, 14, "bold")).pack(side="left", padx=24, pady=16)

        body = tk.Frame(self, bg=COLORS["bg"])
        body.pack(fill="both", expand=True, padx=28, pady=8)

        # Title
        title_row = tk.Frame(body, bg=COLORS["bg"])
        title_row.pack(fill="x", pady=(12, 0))
        section_label(title_row, "EVENT TITLE").pack(side="left", pady=(0,2))
        self.char_label = tk.Label(title_row, text="0/60", bg=COLORS["bg"],
                                   fg=COLORS["subtext"], font=(FONT, 8))
        self.char_label.pack(side="right", pady=(0,2))

        self.title_var = tk.StringVar()
        def _on_title_change(*_):
            val = self.title_var.get()
            if len(val) > 60:
                self.title_var.set(val[:60])
            self.char_label.config(
                text=f"{len(self.title_var.get())}/60",
                fg=COLORS["danger"] if len(self.title_var.get()) >= 55 else COLORS["subtext"]
            )
        self.title_var.trace_add("write", _on_title_change)
        e = field_entry(body, self.title_var)
        e.pack(fill="x", ipady=8)
        e.focus()

        # Date + Time
        row = tk.Frame(body, bg=COLORS["bg"])
        row.pack(fill="x", pady=(12, 0))
        left = tk.Frame(row, bg=COLORS["bg"])
        left.pack(side="left", fill="x", expand=True, padx=(0, 6))
        section_label(left, "DATE  (YYYY-MM-DD)").pack(anchor="w", pady=(0, 2))
        self.date_var = tk.StringVar(value=date_str)
        field_entry(left, self.date_var).pack(fill="x", ipady=8)

        right = tk.Frame(row, bg=COLORS["bg"])
        right.pack(side="left", fill="x", expand=True, padx=(6, 0))
        section_label(right, "TIME  (HH:MM  24h)").pack(anchor="w", pady=(0, 2))
        self.time_var = tk.StringVar()
        field_entry(right, self.time_var).pack(fill="x", ipady=8)

        # Category
        section_label(body, "CATEGORY").pack(anchor="w", pady=(14, 2))
        self.cat_var = tk.StringVar(value="Study")
        cat_frame = tk.Frame(body, bg=COLORS["bg"])
        cat_frame.pack(fill="x")
        for cat, meta in CATEGORIES.items():
            tk.Radiobutton(
                cat_frame, text=f"{meta['icon']} {cat}",
                variable=self.cat_var, value=cat,
                bg=COLORS["bg"], fg=meta["color"],
                selectcolor=COLORS["card"],
                activebackground=COLORS["bg"],
                font=(FONT, 10), relief="flat", bd=0
            ).pack(side="left", padx=(0, 8))

        # Priority + Status
        row2 = tk.Frame(body, bg=COLORS["bg"])
        row2.pack(fill="x", pady=(14, 0))

        pl = tk.Frame(row2, bg=COLORS["bg"])
        pl.pack(side="left", fill="x", expand=True, padx=(0, 6))
        section_label(pl, "PRIORITY").pack(anchor="w", pady=(0, 2))
        self.priority_var = tk.StringVar(value="Medium")
        ttk.Combobox(
            pl, textvariable=self.priority_var,
            values=PRIORITIES, state="readonly", width=14
        ).pack(fill="x", ipady=4)

        pr = tk.Frame(row2, bg=COLORS["bg"])
        pr.pack(side="left", fill="x", expand=True, padx=(6, 0))
        section_label(pr, "STATUS").pack(anchor="w", pady=(0, 2))
        self.status_var = tk.StringVar(value="Pending")
        ttk.Combobox(
            pr, textvariable=self.status_var,
            values=STATUSES, state="readonly", width=14
        ).pack(fill="x", ipady=4)

        # Notes
        section_label(body, "NOTES  (optional)").pack(anchor="w", pady=(14, 2))
        self.notes_text = tk.Text(
            body, bg=COLORS["card"], fg=COLORS["text"],
            relief="flat", bd=0,
            insertbackground=COLORS["text"],
            font=(FONT, 11),
            highlightthickness=1,
            highlightcolor=COLORS["accent"],
            highlightbackground=COLORS["border"],
            height=3, wrap="word"
        )
        self.notes_text.pack(fill="x", ipady=6)

        # Error label
        self.err_label = tk.Label(body, text="", bg=COLORS["bg"],
                                  fg=COLORS["danger"], font=(FONT, 9), wraplength=380, justify="left")
        self.err_label.pack(anchor="w", pady=(6, 0))

        # Keyboard shortcuts
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<Return>",  lambda e: self._save())

        # Buttons
        bf = tk.Frame(body, bg=COLORS["bg"])
        bf.pack(fill="x", pady=14)
        styled_btn(bf, "Cancel", COLORS["card"], COLORS["subtext"], self.destroy).pack(side="right", padx=(8, 0))
        styled_btn(bf, "  Save Event  ", COLORS["accent"], "#fff", self._save, bold=True).pack(side="right")
        tk.Label(bf, text="Enter ↵ to save  ·  Esc to cancel",
                 bg=COLORS["bg"], fg=COLORS["subtext"],
                 font=(FONT, 8)).pack(side="left")

    def _save(self):
        title    = self.title_var.get().strip()
        date_str = self.date_var.get().strip()
        time_str = self.time_var.get().strip()

        # Validate title
        if not title:
            self.err_label.config(text="⚠  Please enter an event title.")
            return

        # Validate date
        try:
            event_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            self.err_label.config(text="⚠  Date must be YYYY-MM-DD  e.g. 2026-04-15")
            return

        # Validate time + 1-minute-future rule
        now = datetime.now()
        if time_str:
            try:
                t = datetime.strptime(time_str, "%H:%M")
            except ValueError:
                self.err_label.config(text="⚠  Time must be HH:MM (24h)  e.g. 14:30")
                return
            event_dt  = datetime(event_date.year, event_date.month, event_date.day, t.hour, t.minute)
            min_allow = now + timedelta(minutes=1)
            if event_dt < min_allow:
                self.err_label.config(
                    text=f"⚠  Event must be at least 1 minute in the future.\n"
                         f"   Earliest allowed: {min_allow.strftime('%Y-%m-%d  %H:%M')}"
                )
                return
        else:
            if event_date < date.today():
                self.err_label.config(text="⚠  Cannot add events for past dates.")
                return

        event = {
            "title":    title,
            "date":     date_str,
            "time":     time_str,
            "category": self.cat_var.get(),
            "priority": self.priority_var.get(),
            "status":   self.status_var.get(),
            "notes":    self.notes_text.get("1.0", "end-1c").strip(),
        }
        if self.on_save:
            self.on_save(event)
        self.destroy()


# ── Main App ──────────────────────────────────────────────────────────────────
class EventsCalendarApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Events Calendar")
        self.geometry("1200x760")
        self.minsize(1000, 640)
        self.configure(bg=COLORS["bg"])

        self.events        = load_events()
        self.today         = date.today()
        self.current_year  = self.today.year
        self.current_month = self.today.month
        self.selected_date = self.today.strftime("%Y-%m-%d")
        self.filter_cat    = tk.StringVar(value="All")

        self._apply_styles()
        self._build_ui()
        self._render_calendar()
        self._build_sidebar(self.selected_date)

    def _apply_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TCombobox",
            fieldbackground=COLORS["card"],
            background=COLORS["card"],
            foreground="#000000",
            arrowcolor=COLORS["text"],
            bordercolor=COLORS["border"],
            lightcolor=COLORS["card"],
            darkcolor=COLORS["card"],
        )
        style.map("TCombobox",
            fieldbackground=[("readonly", COLORS["card"])],
            foreground=[("readonly", "#000000")],
        )

    # ── Build UI ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Nav bar
        nav = tk.Frame(self, bg=COLORS["panel"], height=64)
        nav.pack(fill="x")
        nav.pack_propagate(False)

        logo_frame = tk.Frame(nav, bg=COLORS["panel"])
        logo_frame.pack(side="left", padx=24)
        tk.Label(logo_frame, text="◈  My Calendar", bg=COLORS["panel"], fg=COLORS["text"],
                 font=(FONT, 16, "bold")).pack(side="left")
        self.badge_label = tk.Label(logo_frame, text="",
                                    bg=COLORS["accent"], fg="#fff",
                                    font=(FONT, 8, "bold"), padx=6, pady=1)
        self.badge_label.pack(side="left", padx=(8, 0))

        nav_mid = tk.Frame(nav, bg=COLORS["panel"])
        nav_mid.pack(side="left", expand=True)
        nav_btn(nav_mid, "‹", self._prev_month, padx=12, pady=4, size=16).pack(side="left", padx=4)
        self.month_label = tk.Label(nav_mid, text="", bg=COLORS["panel"], fg=COLORS["text"],
                                    font=(FONT, 15, "bold"), width=18, anchor="center")
        self.month_label.pack(side="left", padx=8)
        nav_btn(nav_mid, "›", self._next_month, padx=12, pady=4, size=16).pack(side="left", padx=4)

        nav_btn(nav, "Today", self._go_today).pack(side="right", padx=8, pady=14)
        nav_btn(nav, "＋ Add Event", lambda: self._open_add_dialog(), bold=True
                ).pack(side="right", padx=(0, 4), pady=14)

        # Accent separator
        tk.Frame(self, bg=COLORS["accent"], height=2).pack(fill="x")

        # Filter bar
        fbar = tk.Frame(self, bg=COLORS["panel"], height=40)
        fbar.pack(fill="x")
        fbar.pack_propagate(False)
        tk.Label(fbar, text="Filter:", bg=COLORS["panel"], fg=COLORS["subtext"],
                 font=(FONT, 10)).pack(side="left", padx=(20, 6), pady=8)
        for cat in ["All"] + list(CATEGORIES.keys()):
            color = CATEGORIES[cat]["color"] if cat != "All" else COLORS["subtext"]
            icon  = CATEGORIES[cat]["icon"]  if cat != "All" else "🗂"
            tk.Radiobutton(
                fbar, text=f"{icon} {cat}",
                variable=self.filter_cat, value=cat,
                bg=COLORS["panel"], fg=color,
                selectcolor=COLORS["card"],
                activebackground=COLORS["panel"],
                font=(FONT, 10), relief="flat", bd=0,
                command=self._render_calendar
            ).pack(side="left", padx=6)

        # Main area
        main = tk.Frame(self, bg=COLORS["bg"])
        main.pack(fill="both", expand=True)

        # Calendar
        cal_section = tk.Frame(main, bg=COLORS["bg"])
        cal_section.pack(side="left", fill="both", expand=True, padx=(16, 8), pady=12)

        hdr_frame = tk.Frame(cal_section, bg=COLORS["bg"])
        hdr_frame.pack(fill="x", pady=(0, 4))
        for day in DAY_NAMES:
            tk.Label(hdr_frame, text=day, bg=COLORS["bg"], fg=COLORS["subtext"],
                     font=(FONT, 10, "bold"), anchor="center").pack(side="left", expand=True, fill="x")

        self.grid_frame = tk.Frame(cal_section, bg=COLORS["border"])
        self.grid_frame.pack(fill="both", expand=True)

        # Right panel
        right = tk.Frame(main, bg=COLORS["bg"], width=300)
        right.pack(side="right", fill="y", padx=(0, 12), pady=12)
        right.pack_propagate(False)

        self.sidebar = tk.Frame(right, bg=COLORS["panel"])
        self.sidebar.pack(fill="both", expand=True)

        self.metrics_frame = tk.Frame(right, bg=COLORS["card"])
        self.metrics_frame.pack(fill="x", pady=(8, 0))
        self._render_metrics()

        # Status bar
        self.status_bar = tk.Frame(self, bg=COLORS["panel"], height=26)
        self.status_bar.pack(side="bottom", fill="x")
        self.status_bar.pack_propagate(False)
        self.status_label = tk.Label(
            self.status_bar,
            text="",
            bg=COLORS["panel"], fg=COLORS["subtext"],
            font=(FONT, 9), anchor="w"
        )
        self.status_label.pack(side="left", padx=16)
        tk.Label(self.status_bar, text="Events Calendar  ·  Data auto-saved",
                 bg=COLORS["panel"], fg=COLORS["border"],
                 font=(FONT, 8)).pack(side="right", padx=16)
        self._update_badge()

    # ── Metrics ───────────────────────────────────────────────────────────────
    def _render_metrics(self):
        for w in self.metrics_frame.winfo_children():
            w.destroy()

        tk.Label(self.metrics_frame, text="📊  This Month",
                 bg=COLORS["card"], fg=COLORS["text"],
                 font=(FONT, 10, "bold")).pack(anchor="w", padx=12, pady=(10, 4))

        prefix      = f"{self.current_year}-{self.current_month:02d}-"
        month_evs   = [ev for k, evs in self.events.items()
                       if k.startswith(prefix) for ev in evs]
        total       = len(month_evs)
        done        = sum(1 for e in month_evs if e.get("status") == "Done")
        pending     = sum(1 for e in month_evs if e.get("status") == "Pending")

        summary = tk.Frame(self.metrics_frame, bg=COLORS["card"])
        summary.pack(fill="x", padx=12, pady=(0, 6))
        for label, val, color in [
            ("Total", total, COLORS["text"]),
            ("Done",  done,  COLORS["success"]),
            ("Pending", pending, COLORS["accent2"]),
        ]:
            col = tk.Frame(summary, bg=COLORS["card"])
            col.pack(side="left", expand=True)
            tk.Label(col, text=str(val), bg=COLORS["card"], fg=color,
                     font=(FONT, 14, "bold")).pack()
            tk.Label(col, text=label, bg=COLORS["card"], fg=COLORS["subtext"],
                     font=(FONT, 8)).pack()

        for cat, meta in CATEGORIES.items():
            count = sum(1 for e in month_evs if e.get("category") == cat)
            if count == 0:
                continue
            row = tk.Frame(self.metrics_frame, bg=COLORS["card"])
            row.pack(fill="x", padx=12, pady=1)
            tk.Label(row, text=f"{meta['icon']} {cat}",
                     bg=COLORS["card"], fg=meta["color"],
                     font=(FONT, 9), width=12, anchor="w").pack(side="left")
            bar_bg = tk.Frame(row, bg=COLORS["border"], height=6)
            bar_bg.pack(side="left", fill="x", expand=True, padx=(4, 8))
            pct = count / total if total else 0
            bar_fill_w = max(4, int(140 * pct))
            tk.Frame(bar_bg, bg=meta["color"], height=6, width=bar_fill_w).pack(side="left", fill="y")
            tk.Label(row, text=str(count), bg=COLORS["card"], fg=COLORS["subtext"],
                     font=(FONT, 9)).pack(side="right")

        tk.Frame(self.metrics_frame, bg=COLORS["card"], height=8).pack()

    # ── Sidebar ───────────────────────────────────────────────────────────────
    def _build_sidebar(self, date_str):
        for w in self.sidebar.winfo_children():
            w.destroy()

        d = datetime.strptime(date_str, "%Y-%m-%d")

        hdr = tk.Frame(self.sidebar, bg=COLORS["card"])
        hdr.pack(fill="x")
        tk.Label(hdr, text=d.strftime("%A"),
                 bg=COLORS["card"], fg=COLORS["subtext"],
                 font=(FONT, 10)).pack(anchor="w", padx=16, pady=(14, 0))
        tk.Label(hdr, text=d.strftime("%B %-d, %Y"),
                 bg=COLORS["card"], fg=COLORS["text"],
                 font=(FONT, 14, "bold")).pack(anchor="w", padx=16, pady=(0, 10))

        is_past = d.date() < date.today()
        if not is_past:
            styled_btn(hdr, "＋ Add to this day", COLORS["accent"], "#fff",
                       lambda: self._open_add_dialog(date_str), bold=True, pady=6
                       ).pack(anchor="w", padx=16, pady=(0, 12))
        else:
            tk.Label(hdr, text="📅  Past date — read only",
                     bg=COLORS["card"], fg=COLORS["subtext"],
                     font=(FONT, 9)).pack(anchor="w", padx=16, pady=(0, 12))

        events = self.events.get(date_str, [])

        # Scrollable container for event cards
        scroll_outer = tk.Frame(self.sidebar, bg=COLORS["panel"])
        scroll_outer.pack(fill="both", expand=True, padx=0, pady=6)

        canvas = tk.Canvas(scroll_outer, bg=COLORS["panel"], highlightthickness=0, bd=0)
        scrollbar = tk.Scrollbar(scroll_outer, orient="vertical", command=canvas.yview)
        body = tk.Frame(canvas, bg=COLORS["panel"])

        body.bind("<Configure>",
                  lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=body, anchor="nw")
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(canvas_window, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mouse wheel scroll
        def _on_mousewheel(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)
        body.bind("<MouseWheel>", _on_mousewheel)

        if not events:
            empty_frame = tk.Frame(body, bg=COLORS["panel"])
            empty_frame.pack(expand=True, pady=30, padx=10)
            tk.Label(empty_frame, text="✨",
                     bg=COLORS["panel"], fg=COLORS["subtext"],
                     font=(FONT, 28)).pack()
            tk.Label(empty_frame, text="Nothing scheduled",
                     bg=COLORS["panel"], fg=COLORS["text"],
                     font=(FONT, 12, "bold")).pack(pady=(6, 2))
            tk.Label(empty_frame, text="Enjoy the free day.",
                     bg=COLORS["panel"], fg=COLORS["subtext"],
                     font=(FONT, 10)).pack()
        else:
            for i, ev in enumerate(events):
                meta  = CATEGORIES.get(ev.get("category", "Study"), CATEGORIES["Study"])
                self._event_card(body, ev, date_str, i, meta["color"], meta["icon"])

    def _event_card(self, parent, ev, date_str, idx, color, icon):
        is_done = ev.get("status") == "Done"
        card_bg = "#232840" if is_done else COLORS["card"]

        card = tk.Frame(parent, bg=card_bg, cursor="hand2")
        card.pack(fill="x", pady=4)
        hover_bg = "#2E3452" if not is_done else "#272B3C"
        def _enter(e, f=card, h=hover_bg):
            f.config(bg=h)
            for child in f.winfo_children():
                try: child.config(bg=h)
                except: pass
        def _leave(e, f=card, b=card_bg):
            f.config(bg=b)
            for child in f.winfo_children():
                try: child.config(bg=b)
                except: pass
        card.bind("<Enter>", _enter)
        card.bind("<Leave>", _leave)
        tk.Frame(card, bg=color if not is_done else COLORS["success"], width=4).pack(side="left", fill="y")

        content = tk.Frame(card, bg=card_bg)
        content.pack(side="left", fill="both", expand=True, padx=10, pady=8)

        # Title row
        tr = tk.Frame(content, bg=card_bg)
        tr.pack(fill="x")

        title_text = ev['title']
        title_fg   = COLORS["subtext"] if is_done else COLORS["text"]
        tk.Label(tr, text=f"{icon} {title_text}",
                 bg=card_bg, fg=title_fg,
                 font=(FONT, 11, "bold" if not is_done else "normal"),
                 anchor="w").pack(side="left", fill="x", expand=True)
        tk.Button(tr, text="✕", bg=card_bg, fg=COLORS["subtext"],
                  relief="flat", bd=0, cursor="hand2", font=(FONT, 10),
                  command=lambda d=date_str, ix=idx: self._delete_event(d, ix)
                  ).pack(side="right")

        # ✔ Done / Undo button row
        action_row = tk.Frame(content, bg=card_bg)
        action_row.pack(fill="x", pady=(4, 2))

        if not is_done:
            done_btn = tk.Button(
                action_row, text="✔  Mark as Done",
                bg=COLORS["success"], fg="#FFFFFF",
                relief="flat", bd=0, padx=10, pady=3,
                cursor="hand2",
                font=(FONT, 9, "bold"),
                command=lambda d=date_str, ix=idx: self._toggle_done(d, ix, True)
            )
            done_btn.pack(side="left")
        else:
            undo_btn = tk.Button(
                action_row, text="↩  Undo Done",
                bg=COLORS["hover"], fg=COLORS["subtext"],
                relief="flat", bd=0, padx=10, pady=3,
                cursor="hand2",
                font=(FONT, 9),
                command=lambda d=date_str, ix=idx: self._toggle_done(d, ix, False)
            )
            undo_btn.pack(side="left")
            tk.Label(action_row, text="✔ Completed",
                     bg=card_bg, fg=COLORS["success"],
                     font=(FONT, 9, "bold")).pack(side="left", padx=(8, 0))

        # Chips
        chips = tk.Frame(content, bg=card_bg)
        chips.pack(fill="x", pady=(2, 0))
        self._chip(chips, ev.get("category", ""), color)
        pri       = ev.get("priority", "")
        pri_color = {"High": COLORS["danger"], "Medium": "#F0915B", "Low": COLORS["success"]}.get(pri, COLORS["subtext"])
        self._chip(chips, pri, pri_color)
        sta       = ev.get("status", "")
        sta_color = {"Done": COLORS["success"], "In Progress": COLORS["accent2"], "Pending": COLORS["subtext"]}.get(sta, COLORS["subtext"])
        self._chip(chips, sta, sta_color)

        if ev.get("time"):
            tk.Label(content, text=f"🕐 {ev['time']}",
                     bg=card_bg, fg=COLORS["subtext"],
                     font=(FONT, 9), anchor="w").pack(fill="x", pady=(3, 0))
        if ev.get("notes"):
            tk.Label(content, text=ev["notes"],
                     bg=card_bg, fg=COLORS["subtext"],
                     font=(FONT, 9), anchor="w",
                     wraplength=260, justify="left").pack(fill="x", pady=(2, 0))

    def _chip(self, parent, text, color):
        if not text:
            return
        f = tk.Frame(parent, bg=color)
        f.pack(side="left", padx=(0, 4))
        tk.Label(f, text=text, bg=color, fg="#FFFFFF",
                 font=(FONT, 7, "bold"), padx=5, pady=1).pack()

    # ── Calendar Grid ─────────────────────────────────────────────────────────
    def _render_calendar(self):
        self.today = date.today()  # refresh in case app left open past midnight
        self.month_label.config(
            text=f"{MONTH_NAMES[self.current_month-1]}  {self.current_year}"
        )
        for w in self.grid_frame.winfo_children():
            w.destroy()

        cal      = calendar.monthcalendar(self.current_year, self.current_month)
        today_str = self.today.strftime("%Y-%m-%d")
        fcat      = self.filter_cat.get()

        for r, week in enumerate(cal):
            for c, day in enumerate(week):
                if day == 0:
                    cell = tk.Frame(self.grid_frame, bg=COLORS["bg"], highlightthickness=0)
                else:
                    date_str = f"{self.current_year}-{self.current_month:02d}-{day:02d}"
                    is_today  = date_str == today_str
                    is_sel    = date_str == self.selected_date
                    is_past   = datetime.strptime(date_str, "%Y-%m-%d").date() < self.today
                    cell_bg   = COLORS["hover"] if is_sel else ("#1E2138" if is_past else COLORS["card"])

                    cell = tk.Frame(
                        self.grid_frame, bg=cell_bg,
                        highlightbackground=COLORS["accent"] if is_sel else COLORS["border"],
                        highlightthickness=1, cursor="hand2"
                    )
                    cell.bind("<Button-1>", lambda e, ds=date_str: self._select_date(ds))
                    cell.bind("<Enter>",    lambda e, f=cell: f.config(bg=COLORS["hover"]))
                    cell.bind("<Leave>",    lambda e, f=cell, bg=cell_bg: f.config(bg=bg))

                    # Day number
                    nr = tk.Frame(cell, bg=cell_bg)
                    nr.pack(fill="x", padx=6, pady=(6, 2))
                    nr.bind("<Button-1>", lambda e, ds=date_str: self._select_date(ds))

                    if is_today:
                        lbl = tk.Label(nr, text=str(day),
                                       bg=COLORS["today"], fg="#FFFFFF",
                                       font=(FONT, 11, "bold"), width=2, padx=4, pady=1)
                    else:
                        lbl = tk.Label(nr, text=str(day),
                                       bg=cell_bg,
                                       fg=COLORS["subtext"] if is_past else (COLORS["text"] if c < 5 else COLORS["subtext"]),
                                       font=(FONT, 11))
                    lbl.pack(side="left")
                    lbl.bind("<Button-1>", lambda e, ds=date_str: self._select_date(ds))

                    # Event chips (filtered)
                    all_evs = self.events.get(date_str, [])
                    shown   = [e for e in all_evs if fcat == "All" or e.get("category") == fcat]
                    for ev in shown[:2]:
                        meta    = CATEGORIES.get(ev.get("category", "Study"), CATEGORIES["Study"])
                        ev_done = ev.get("status") == "Done"
                        chip_bg = "#2A3020" if ev_done else meta["color"]
                        chip_fg = "#5A7A50" if ev_done else "#FFFFFF"
                        cf      = tk.Frame(cell, bg=chip_bg)
                        cf.pack(fill="x", padx=6, pady=1)
                        cf.bind("<Button-1>", lambda e, ds=date_str: self._select_date(ds))
                        clip    = ev["title"][:15] + ("…" if len(ev["title"]) > 15 else "")
                        prefix  = "✔ " if ev_done else f"{meta['icon']} "
                        cl      = tk.Label(cf, text=f"{prefix}{clip}",
                                           bg=chip_bg, fg=chip_fg,
                                           font=(FONT, 8), anchor="w")
                        cl.pack(fill="x", padx=3, pady=1)
                        cl.bind("<Button-1>", lambda e, ds=date_str: self._select_date(ds))

                    if len(shown) > 2:
                        ml = tk.Label(cell, text=f"+{len(shown)-2} more",
                                      bg=cell_bg, fg=COLORS["subtext"], font=(FONT, 8))
                        ml.pack(anchor="w", padx=8)
                        ml.bind("<Button-1>", lambda e, ds=date_str: self._select_date(ds))

                cell.grid(row=r, column=c, sticky="nsew", padx=1, pady=1)

        for r in range(len(cal)):
            self.grid_frame.rowconfigure(r, weight=1)
        for c in range(7):
            self.grid_frame.columnconfigure(c, weight=1)

        self._render_metrics()

    # ── Actions ───────────────────────────────────────────────────────────────
    def _update_status(self):
        total = sum(len(v) for v in self.events.values())
        done  = sum(1 for evs in self.events.values() for e in evs if e.get("status") == "Done")
        self.status_label.config(
            text=f"  {total} total events  ·  {done} completed  ·  {total - done} pending"
        )

    def _update_badge(self):
        today_str  = self.today.strftime("%Y-%m-%d")
        count      = len(self.events.get(today_str, []))
        if count > 0:
            self.badge_label.config(text=f"{count} today", bg=COLORS["accent"])
            self.badge_label.pack(side="left", padx=(8, 0))
        else:
            self.badge_label.pack_forget()

    def _select_date(self, date_str):
        self.selected_date = date_str
        self._render_calendar()
        self._build_sidebar(date_str)

    def _prev_month(self):
        if self.current_month == 1:
            self.current_month, self.current_year = 12, self.current_year - 1
        else:
            self.current_month -= 1
        self._render_calendar()

    def _next_month(self):
        if self.current_month == 12:
            self.current_month, self.current_year = 1, self.current_year + 1
        else:
            self.current_month += 1
        self._render_calendar()

    def _go_today(self):
        self.current_year   = self.today.year
        self.current_month  = self.today.month
        self.selected_date  = self.today.strftime("%Y-%m-%d")
        self._render_calendar()
        self._build_sidebar(self.selected_date)

    def _open_add_dialog(self, date_str=None):
        date_str = date_str or self.selected_date or self.today.strftime("%Y-%m-%d")
        EventDialog(self, date_str=date_str, on_save=self._save_event)

    def _save_event(self, event):
        ds = event["date"]
        if ds not in self.events:
            self.events[ds] = []
        self.events[ds].append(event)
        save_events(self.events)
        d = datetime.strptime(ds, "%Y-%m-%d")
        self.current_year, self.current_month = d.year, d.month
        self.selected_date = ds
        self._render_calendar()
        self._build_sidebar(ds)

    def _toggle_done(self, date_str, index, mark_done):
        self.events[date_str][index]["status"] = "Done" if mark_done else "Pending"
        save_events(self.events)
        self._render_calendar()
        self._build_sidebar(date_str)

    def _delete_event(self, date_str, index):
        ev_title = self.events[date_str][index].get("title", "this event")
        if messagebox.askyesno("Delete Event",
                               f"Delete ['{ev_title}']? This cannot be undone.",
                               parent=self):
            self.events[date_str].pop(index)
            if not self.events[date_str]:
                del self.events[date_str]
            save_events(self.events)
            self._render_calendar()
            self._build_sidebar(date_str)


# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = EventsCalendarApp()
    app.mainloop()