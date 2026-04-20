import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import numpy as np
import os, sys
 
DATA_DIR = "."
 
def load(name):
    try: return pd.read_csv(os.path.join(DATA_DIR, name))
    except Exception as e: print(f"Warning: could not load {name}: {e}"); return pd.DataFrame()
 
athletes       = load("athletes.csv")
coaches        = load("coaches.csv")
events         = load("events.csv")
medallists     = load("medallists.csv")
medals         = load("medals.csv")
medals_total   = load("medals_total.csv")
nocs           = load("nocs.csv")
teams          = load("teams.csv")
tech_officials = load("technical_officials.csv")
 
GOLD = "#FFD700"; SILVER = "#C0C0C0"; BRONZE = "#CD7F32"
BG = "#0D1B2A"; CARD = "#1B2B3B"; ACCENT = "#00A8E8"
TEXT = "#FFFFFF"; SUBTEXT = "#A0B4C8"
GREEN = "#2ECC71"; RED = "#E74C3C"; PURPLE = "#9B59B6"
 
plt.rcParams.update({
    "figure.facecolor": CARD, "axes.facecolor": CARD, "axes.edgecolor": SUBTEXT,
    "axes.labelcolor": TEXT, "xtick.color": SUBTEXT, "ytick.color": SUBTEXT,
    "text.color": TEXT, "grid.color": "#2A3D52", "grid.alpha": 0.5,
})
 
def make_card(parent, **kw):
    return tk.Frame(parent, bg=CARD, bd=0, highlightbackground=ACCENT, highlightthickness=1, **kw)
 
def section_label(parent, text, size=11, color=ACCENT):
    tk.Label(parent, text=text, bg=CARD, fg=color, font=("Helvetica", size, "bold")).pack(anchor="w", padx=10, pady=(8,2))
 
def stat_box(parent, label, value, color=GOLD):
    f = tk.Frame(parent, bg=CARD, padx=10, pady=4); f.pack(side="left", padx=6, pady=2)
    tk.Label(f, text=str(value), bg=CARD, fg=color, font=("Helvetica", 20, "bold")).pack()
    tk.Label(f, text=label, bg=CARD, fg=SUBTEXT, font=("Helvetica", 9)).pack()
 
 
class OlympicsApp:
    def __init__(self, root):
        self.root = root
        root.title("Paris 2024 Olympics – Analytics Dashboard")
        root.configure(bg=BG); root.geometry("1024x648"); root.minsize(600, 400)
 
        hdr = tk.Frame(root, bg="#0A1628", pady=10); hdr.pack(fill="x")
        try:
            from PIL import Image, ImageTk
            logo_img = Image.open("logo.png").resize((40,60), Image.Resampling.LANCZOS)
            self.logo_tk = ImageTk.PhotoImage(logo_img)
            tk.Label(hdr, image=self.logo_tk, bg="#0A1628").pack(side="left", padx=(20,10))
        except Exception: pass
        tk.Label(hdr, text="PARIS 2024 OLYMPICS", bg="#0A1628", fg=GOLD, font=("Helvetica", 20, "bold")).pack(side="left", padx=10)
 
        style = ttk.Style(); style.theme_use("clam")
        style.configure("TNotebook", background=BG, borderwidth=0, tabmargins=[0,0,0,0])
        style.configure("TNotebook.Tab", background=CARD, foreground=SUBTEXT, padding=[14,4,14,4], font=("Helvetica",10,"bold"), borderwidth=0)
        style.map("TNotebook.Tab",
            background=[("selected","#2A3D52"),("active",CARD)],
            foreground=[("selected",TEXT),("active",TEXT)],
            padding=[("selected",[14,4,14,4]),("active",[14,4,14,4])],
            relief=[("selected","flat"),("active","flat"),("!selected","flat")],
            borderwidth=[("selected",0),("active",0),("!selected",0)])
        style.configure("TCombobox", fieldbackground=BG, background=BG, foreground=TEXT, selectbackground=ACCENT)
        style.configure("Treeview", background=CARD, foreground=TEXT, fieldbackground=CARD, rowheight=24)
        style.configure("Treeview.Heading", background=BG, foreground=GOLD, font=("Helvetica",9,"bold"))
        style.map("Treeview", background=[("selected",ACCENT)])
        style.configure("Vertical.TScrollbar", background=CARD, troughcolor=BG)
        style.configure("Horizontal.TScrollbar", background=CARD, troughcolor=BG)
 
        nb = ttk.Notebook(root); nb.pack(fill="both", expand=True); self.notebook = nb
 
        for label, builder in [
            ("🏠 Overview", self.build_overview), ("🥇 Medals", self.build_medals),
            ("🏃 Athletes", self.build_athletes), ("🔍 Country Explorer", self.build_explorer),
            ("⚔️  Compare Countries", self.build_compare), ("📊 Data Browser", self.build_table),
        ]:
            frame = tk.Frame(nb, bg=BG); nb.add(frame, text=f"  {label}  ")
            try: builder(frame)
            except Exception as e:
                tk.Label(frame, text=f"Error building tab:\n{e}", bg=BG, fg=RED, font=("Helvetica",11)).pack(expand=True)
                import traceback; traceback.print_exc()
 
        sb = tk.Frame(root, bg="#0A1628", height=26); sb.pack(fill="x", side="bottom")
        tk.Label(sb, text="  |  ".join([f"Athletes: {len(athletes):,}", f"Countries: {len(medals_total)}",
            f"Medals: {int(medals_total['Total'].sum()):,}", f"Events: {len(events)}"]),
            bg="#0A1628", fg=SUBTEXT, font=("Helvetica",9)).pack(side="left", padx=14, pady=4)
        tk.Label(sb, text="Paris 2024  © Data from Olympics.com", bg="#0A1628", fg=SUBTEXT, font=("Helvetica",9)).pack(side="right", padx=14)
 
    def build_overview(self, tab):
        self.selected_country = None
        kpi_frame = make_card(tab); kpi_frame.pack(fill="x", padx=14, pady=(14,6))
        tk.Label(kpi_frame, text="🏅  Paris 2024 Olympics  –  At a Glance", bg=CARD, fg=GOLD, font=("Helvetica",14,"bold")).pack(anchor="w", padx=12, pady=(8,4))
        row = tk.Frame(kpi_frame, bg=CARD); row.pack(fill="x", padx=6, pady=6)
        stat_box(row, "Countries", len(medals_total), ACCENT)
        stat_box(row, "Total Medals", int(medals_total["Total"].sum()), GOLD)
        stat_box(row, "Gold Medals", int(medals_total["Gold Medal"].sum()), "#FFD700")
        stat_box(row, "Athletes", len(athletes), GREEN)
        stat_box(row, "Disciplines", len(events["sport"].unique()) if not events.empty else "—", PURPLE)
 
        row2 = tk.Frame(tab, bg=BG); row2.pack(fill="both", expand=True, padx=14, pady=6)
        self.overview_c1 = make_card(row2); self.overview_c1.pack(side="left", fill="both", expand=True, padx=(0,6))
        self.overview_c2 = make_card(row2); self.overview_c2.pack(side="left", fill="both", expand=True, padx=(6,0))
        self.draw_overview_charts()
 
    def draw_overview_charts(self):
        for w in self.overview_c1.winfo_children(): w.destroy()
        for w in self.overview_c2.winfo_children(): w.destroy()
 
        section_label(self.overview_c1, "🥇  Top 10 Countries – Total Medals")
        self.top10 = medals_total.nlargest(10, "Total").iloc[::-1]
        fig1 = Figure(figsize=(5,4), tight_layout=True); ax1 = fig1.add_subplot(111)
        colors = [GOLD if c == self.selected_country else ACCENT for c in self.top10["country"]]
        self.bars_overview = ax1.barh(self.top10["country"], self.top10["Total"], color=colors, alpha=0.85)
        ax1.set_xlabel("Medal Count"); ax1.grid(axis="x", alpha=0.3)
        for bar, val in zip(self.bars_overview, self.top10["Total"]):
            ax1.text(val+0.5, bar.get_y()+bar.get_height()/2, str(val), va="center", color=TEXT, fontsize=8, fontweight="bold")
            bar.set_picker(5)
        canvas1 = FigureCanvasTkAgg(fig1, self.overview_c1)
        canvas1.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)
        canvas1.mpl_connect('pick_event', self.on_overview_click)
 
        section_label(self.overview_c2, "🌍  Medal Share – Top 5 Nations" if not self.selected_country else f"📊  {self.selected_country} – Medal Breakdown")
        if self.selected_country:
            r = medals_total[medals_total["country"] == self.selected_country]
            if not r.empty:
                vals = [int(r["Gold Medal"].values[0]), int(r["Silver Medal"].values[0]), int(r["Bronze Medal"].values[0])]
                lbls, colors_pie = ["Gold","Silver","Bronze"], [GOLD,SILVER,BRONZE]
            else:
                vals, lbls, colors_pie = [1,1,1], ["N/A","N/A","N/A"], [SUBTEXT,SUBTEXT,SUBTEXT]
        else:
            self.top5 = medals_total.nlargest(5, "Total")
            vals = self.top5["Total"].tolist(); lbls = self.top5["country"].tolist()
            colors_pie = [GOLD, ACCENT, GREEN, PURPLE, RED]
 
        fig2 = Figure(figsize=(5,4), tight_layout=True); ax2 = fig2.add_subplot(111)
        self.wedges_overview, texts, autotexts = ax2.pie(vals, labels=lbls, autopct="%1.1f%%",
            colors=colors_pie[:len(vals)], startangle=140, wedgeprops=dict(edgecolor=BG, linewidth=1.5))
        for t in texts: t.set_color(TEXT)
        for a in autotexts: a.set_color(BG); a.set_fontsize(8)
        for wedge in self.wedges_overview: wedge.set_picker(True)
        canvas2 = FigureCanvasTkAgg(fig2, self.overview_c2)
        canvas2.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)
        canvas2.mpl_connect('pick_event', self.on_overview_click)
 
    def on_overview_click(self, event):
        artist = event.artist; clicked_country = None
        try:
            if artist in self.bars_overview:
                clicked_country = self.top10.iloc[self.bars_overview.index(artist)]['country']
            elif hasattr(self, 'wedges_overview') and artist in self.wedges_overview:
                if not self.selected_country:
                    clicked_country = self.top5.iloc[self.wedges_overview.index(artist)]['country']
        except: return
        if clicked_country:
            self.selected_country = None if self.selected_country == clicked_country else clicked_country
        else: self.selected_country = None
        self.draw_overview_charts()
 
    def build_medals(self, tab):
        self.selected_country_medals = None; self.medals_top_n = 15
        ctrl_frame = make_card(tab); ctrl_frame.pack(fill="x", padx=14, pady=(14,6))
        tk.Label(ctrl_frame, text="Show top:", bg=CARD, fg=SUBTEXT, font=("Helvetica",10)).pack(side="left", padx=(12,4))
        top_var = tk.StringVar(value="15")
        tk.Entry(ctrl_frame, textvariable=top_var, bg=BG, fg=TEXT, insertbackground=TEXT, width=6, font=("Helvetica",10), relief="flat", bd=2).pack(side="left", padx=4)
        tk.Label(ctrl_frame, text="countries", bg=CARD, fg=SUBTEXT, font=("Helvetica",10)).pack(side="left", padx=(0,12))
        def on_top_change(*_):
            try:
                n = int(top_var.get())
                if 0 < n <= len(medals_total): self.medals_top_n = n; self.draw_medals_charts()
            except ValueError: pass
        top_var.trace_add("write", on_top_change)
 
        row1 = tk.Frame(tab, bg=BG); row1.pack(fill="both", expand=True, padx=14, pady=6)
        self.medals_c1 = make_card(row1); self.medals_c1.pack(side="left", fill="both", expand=True, padx=(0,6))
        self.medals_c3 = make_card(row1); self.medals_c3.pack(side="left", fill="both", expand=True, padx=(6,0))
        self.draw_medals_charts()
 
    def draw_medals_charts(self):
        for w in self.medals_c1.winfo_children(): w.destroy()
        for w in self.medals_c3.winfo_children(): w.destroy()
 
        section_label(self.medals_c1, f"🏅  Gold / Silver / Bronze – Top {self.medals_top_n} Countries")
        top15 = medals_total.nlargest(self.medals_top_n, "Total")
        fig1 = Figure(figsize=(4,3), tight_layout=True); ax1 = fig1.add_subplot(111)
        x = np.arange(len(top15)); w = 0.6
        cg = [GOLD if c == self.selected_country_medals else "#FFB700" for c in top15["country"]]
        cs = [SILVER if c == self.selected_country_medals else "#8A8A8A" for c in top15["country"]]
        cb = [BRONZE if c == self.selected_country_medals else "#A0654B" for c in top15["country"]]
        bars1 = ax1.bar(x, top15["Gold Medal"], w, label="Gold", color=cg, alpha=0.9)
        bars2 = ax1.bar(x, top15["Silver Medal"], w, label="Silver", color=cs, alpha=0.9, bottom=top15["Gold Medal"])
        bars3 = ax1.bar(x, top15["Bronze Medal"], w, label="Bronze", color=cb, alpha=0.9, bottom=top15["Gold Medal"]+top15["Silver Medal"])
        ax1.set_xticks(x); ax1.set_xticklabels(top15["country_code"], rotation=45, ha="right", fontsize=8)
        ax1.legend(facecolor=CARD, labelcolor=TEXT); ax1.set_ylabel("Medals"); ax1.grid(axis="y", alpha=0.3)
        for bar in list(bars1)+list(bars2)+list(bars3): bar.set_picker(5)
        for i in range(len(top15)):
            g, s, b = top15["Gold Medal"].iloc[i], top15["Silver Medal"].iloc[i], top15["Bronze Medal"].iloc[i]
            if g > 0: ax1.text(i, g/2, str(g), ha="center", va="center", color=BG, fontsize=6, fontweight="bold")
            if s > 0: ax1.text(i, g+s/2, str(s), ha="center", va="center", color=BG, fontsize=6, fontweight="bold")
            if b > 0: ax1.text(i, g+s+b/2, str(b), ha="center", va="center", color=BG, fontsize=6, fontweight="bold")
        for i, total in enumerate(top15["Total"]): ax1.text(i, total+2, str(total), ha="center", color=TEXT, fontsize=8, fontweight="bold")
        self.medals_top15 = top15; self.medals_bars1 = list(bars1); self.medals_bars2 = list(bars2); self.medals_bars3 = list(bars3)
        canvas1 = FigureCanvasTkAgg(fig1, self.medals_c1)
        canvas1.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)
        canvas1.mpl_connect('pick_event', self.on_medals_click)
 
        section_label(self.medals_c3, "📅  Daily Medal Awards Timeline")
        if not medallists.empty:
            mc = medallists.copy()
            mc["medal_date"] = pd.to_datetime(mc["medal_date"], errors="coerce")
            mc = mc.dropna(subset=["discipline","event","medal_type","medal_date"])
            mc["discipline"] = mc["discipline"].str.strip(); mc["event"] = mc["event"].str.strip(); mc["medal_type"] = mc["medal_type"].str.strip()
            if self.selected_country_medals:
                daily = mc[mc["country"] == self.selected_country_medals].drop_duplicates(subset=["medal_date","discipline","event","medal_type"]).groupby("medal_date").size().reset_index(name="count")
            else:
                daily = mc.drop_duplicates(subset=["medal_date","discipline","event","medal_type"]).groupby("medal_date").size().reset_index(name="count")
            fig3 = Figure(figsize=(6,4), tight_layout=True, dpi=100); ax3 = fig3.add_subplot(111)
            cl = GOLD if self.selected_country_medals else "#00A8E8"
            ax3.fill_between(daily["medal_date"], daily["count"], alpha=0.3, color=cl)
            ax3.plot(daily["medal_date"], daily["count"], color=cl, linewidth=3, marker='o', markersize=6, markerfacecolor=GOLD, markeredgecolor=cl, markeredgewidth=1.5)
            for date, count in zip(daily["medal_date"], daily["count"]):
                ax3.text(date, count+0.3, str(int(count)), ha="center", va="bottom", color=TEXT, fontsize=8, fontweight="bold")
            ax3.set_ylabel("Medals Awarded", fontsize=10); ax3.set_xlabel("Date", fontsize=10); ax3.grid(alpha=0.4, which='both')
            ax3.xaxis.set_major_formatter(mdates.DateFormatter('%b %d')); ax3.xaxis.set_major_locator(mdates.DayLocator(interval=1))
            fig3.autofmt_xdate(rotation=45, ha='right')
            FigureCanvasTkAgg(fig3, self.medals_c3).get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)
 
    def on_medals_click(self, event):
        artist = event.artist; all_bars = self.medals_bars1 + self.medals_bars2 + self.medals_bars3
        try:
            if artist in all_bars:
                clicked = self.medals_top15.iloc[all_bars.index(artist) % len(self.medals_top15)]['country']
                self.selected_country_medals = None if self.selected_country_medals == clicked else clicked
        except: return
        self.draw_medals_charts()
 
    def build_athletes(self, tab):
        self.selected_country_athletes = None; self.selected_gender_athletes = None
        make_card(tab).pack(fill="x", padx=14, pady=(14,6))
        row1 = tk.Frame(tab, bg=BG); row1.pack(fill="both", expand=True, padx=14, pady=6)
        self.athletes_c1 = make_card(row1); self.athletes_c1.pack(side="left", fill="both", expand=True, padx=(0,6))
        self.athletes_c2 = make_card(row1); self.athletes_c2.pack(side="left", fill="both", expand=True, padx=(6,6))
        self.athletes_c3 = make_card(row1); self.athletes_c3.pack(side="left", fill="both", expand=True, padx=(6,0))
        self.draw_athletes_charts()
 
    def draw_athletes_charts(self):
        for c in [self.athletes_c1, self.athletes_c2, self.athletes_c3]:
            for w in c.winfo_children(): w.destroy()
 
        import ast, re
        def parse_disciplines(val):
            if pd.isna(val): return []
            val = str(val).strip()
            try:
                result = ast.literal_eval(val)
                return [str(x).strip() for x in result] if isinstance(result, list) else [str(result).strip()]
            except: pass
            if ',' in val: return [x.strip().strip("'\"") for x in val.split(',') if x.strip()]
            cleaned = val.strip("[]'\""); return [cleaned] if cleaned else []
 
        fa = athletes
        if self.selected_country_athletes: fa = fa[fa["country"] == self.selected_country_athletes]
        if self.selected_gender_athletes: fa = fa[fa["gender"] == self.selected_gender_athletes]
        disc_counts = fa["disciplines"].dropna().apply(parse_disciplines).explode().value_counts().head(12)
 
        section_label(self.athletes_c1, "🏃  Top Disciplines by Athlete Count")
        fig1 = Figure(figsize=(5,3.5), tight_layout=True); ax1 = fig1.add_subplot(111)
        ax1.barh(disc_counts.index[::-1], disc_counts.values[::-1], color=ACCENT, alpha=0.85)
        ax1.set_xlabel("Athletes"); ax1.grid(axis="x", alpha=0.3)
        for i, v in enumerate(disc_counts.values[::-1]): ax1.text(v+0.5, i, str(v), va="center", color=TEXT, fontsize=8, fontweight="bold")
        FigureCanvasTkAgg(fig1, self.athletes_c1).get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)
 
        section_label(self.athletes_c2, "🌐  Top 10 Countries by Athletes")
        fc = athletes if not self.selected_gender_athletes else athletes[athletes["gender"] == self.selected_gender_athletes]
        top_ath = fc["country"].value_counts().head(10)
        fig2 = Figure(figsize=(5,3.5), tight_layout=True); ax2 = fig2.add_subplot(111)
        colors = [GOLD if c == self.selected_country_athletes else GREEN for c in top_ath.index]
        bars = ax2.bar(top_ath.index, top_ath.values, color=colors, alpha=0.85)
        ax2.set_xticklabels(top_ath.index, rotation=45, ha="right", fontsize=8); ax2.set_ylabel("Athlete Count"); ax2.grid(axis="y", alpha=0.3)
        for bar in bars: bar.set_picker(5)
        for i, v in enumerate(top_ath.values): ax2.text(i, v+0.5, str(v), ha="center", color=TEXT, fontsize=8, fontweight="bold")
        self.athletes_top10 = top_ath; self.athletes_bars = bars
        canvas2 = FigureCanvasTkAgg(fig2, self.athletes_c2)
        canvas2.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)
        canvas2.mpl_connect('pick_event', self.on_athletes_click)
 
        section_label(self.athletes_c3, "⚧  Athlete Gender Split")
        af = athletes if not self.selected_country_athletes else athletes[athletes["country"] == self.selected_country_athletes]
        if self.selected_gender_athletes: af = af[af["gender"] == self.selected_gender_athletes]
        genders = af["gender"].value_counts()
        title_suffix = f" ({self.selected_country_athletes})" if self.selected_country_athletes else ""
        fig3 = Figure(figsize=(4,3.5), tight_layout=True); ax3 = fig3.add_subplot(111)
        base_colors = [ACCENT, "#FF6B9D"]
        colors_pie = [GOLD if g == self.selected_gender_athletes else c for g, c in zip(genders.index, base_colors)] if self.selected_gender_athletes else base_colors[:len(genders)]
        def autopct_with_count(pct):
            return f'{pct:.1f}%\n({int(round(pct*sum(genders)/100.0))})'
        wedges, texts, autos = ax3.pie(genders, labels=genders.index, autopct=autopct_with_count,
            colors=colors_pie, startangle=90, wedgeprops=dict(width=0.5, edgecolor=BG))
        for t in texts: t.set_color(TEXT)
        for a in autos: a.set_color(BG); a.set_fontsize(7)
        ax3.set_title(f"Male vs Female{title_suffix}", color=TEXT, fontsize=10, pad=6)
        for wedge in wedges: wedge.set_picker(True)
        self.gender_wedges = wedges; self.gender_labels = list(genders.index)
        canvas3 = FigureCanvasTkAgg(fig3, self.athletes_c3)
        canvas3.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)
        canvas3.mpl_connect('pick_event', self.on_gender_click)
 
    def on_athletes_click(self, event):
        artist = event.artist
        try:
            if artist in self.athletes_bars:
                clicked = self.athletes_top10.index[list(self.athletes_bars).index(artist)]
                self.selected_country_athletes = None if self.selected_country_athletes == clicked else clicked
        except: return
        self.draw_athletes_charts()
 
    def on_gender_click(self, event):
        artist = event.artist
        try:
            if hasattr(self, 'gender_wedges') and artist in self.gender_wedges:
                clicked_gender = self.gender_labels[self.gender_wedges.index(artist)]
                self.selected_gender_athletes = None if self.selected_gender_athletes == clicked_gender else clicked_gender
        except: return
        self.draw_athletes_charts()
 
    def build_explorer(self, tab):
        ctrl = make_card(tab); ctrl.pack(fill="x", padx=14, pady=(14,6))
        tk.Label(ctrl, text="🔍  Country Medal Explorer", bg=CARD, fg=GOLD, font=("Helvetica",13,"bold")).pack(side="left", padx=10, pady=8)
        countries = medals_total["country"].tolist(); self.explorer_country = countries[0]; self.selected_medal_type = None
 
        tk.Label(ctrl, text="Search:", bg=CARD, fg=TEXT, font=("Helvetica",10)).pack(side="left", padx=(20,4))
        search_var = tk.StringVar()
        search_entry = tk.Entry(ctrl, textvariable=search_var, bg=BG, fg=TEXT, insertbackground=TEXT, width=24, font=("Helvetica",10), relief="flat", bd=4)
        search_entry.pack(side="left")
 
        dropdown_window = tk.Toplevel(self.root); dropdown_window.withdraw(); dropdown_window.overrideredirect(True); dropdown_window.configure(bg=CARD)
        dropdown = tk.Listbox(dropdown_window, bg=CARD, fg=TEXT, selectbackground="#2A3D52", selectforeground=TEXT, font=("Helvetica",10), height=6, width=30, relief="flat", bd=2, highlightbackground=SUBTEXT, highlightthickness=1)
        dropdown.pack()
        for c in countries: dropdown.insert(tk.END, c)
 
        def show_dropdown(*_):
            q = search_var.get().lower()
            filtered = [c for c in countries if q in c.lower()] if q else countries
            dropdown.delete(0, tk.END)
            for c in filtered: dropdown.insert(tk.END, c)
            if filtered:
                x = search_entry.winfo_rootx(); y = search_entry.winfo_rooty() + search_entry.winfo_height() + 2
                dropdown_window.geometry(f"300x{min(150, len(filtered)*24)}+{x}+{y}"); dropdown_window.deiconify()
            else: dropdown_window.withdraw()
            search_entry.focus_set()
        search_var.trace_add("write", show_dropdown)
 
        def on_dropdown_select(_):
            sel = dropdown.curselection()
            if sel: self.explorer_country = dropdown.get(sel[0]); search_var.set(self.explorer_country); dropdown_window.withdraw(); self.selected_medal_type = None; self.update_explorer()
        dropdown.bind("<<ListboxSelect>>", on_dropdown_select)
 
        def on_search_enter(_):
            q = search_var.get().lower(); filtered = [c for c in countries if q in c.lower()]
            if filtered: self.explorer_country = filtered[0]; search_var.set(self.explorer_country); dropdown_window.withdraw(); self.selected_medal_type = None; self.update_explorer()
        search_entry.bind("<Return>", on_search_enter)
        search_entry.bind("<FocusOut>", lambda _: ctrl.after(200, lambda: dropdown_window.withdraw()))
 
        detail = tk.Frame(tab, bg=BG); detail.pack(fill="both", expand=True, padx=14, pady=6)
        kpi_card = make_card(detail); kpi_card.pack(fill="x", pady=(0,2))
        self.kpi_row = tk.Frame(kpi_card, bg=CARD); self.kpi_row.pack(fill="x", padx=6, pady=(2,2))
        chart_row = tk.Frame(detail, bg=BG); chart_row.pack(fill="both", expand=True, pady=(4,0))
        self.c_chart = make_card(chart_row); self.c_chart.pack(side="left", fill="both", expand=True, padx=(0,6))
        self.d_chart = make_card(chart_row); self.d_chart.pack(side="left", fill="both", expand=True, padx=(6,0))
        self.update_explorer()
 
    def update_explorer(self, *_):
        chosen = self.explorer_country; row = medals_total[medals_total["country"] == chosen].iloc[0]
        for w in self.kpi_row.winfo_children(): w.destroy()
        stat_box(self.kpi_row, "Gold", int(row["Gold Medal"]), GOLD); stat_box(self.kpi_row, "Silver", int(row["Silver Medal"]), SILVER)
        stat_box(self.kpi_row, "Bronze", int(row["Bronze Medal"]), BRONZE); stat_box(self.kpi_row, "Total", int(row["Total"]), ACCENT)
        for w in self.c_chart.winfo_children(): w.destroy()
        for w in self.d_chart.winfo_children(): w.destroy()
 
        section_label(self.c_chart, f"🏅 Medal Breakdown – {chosen}")
        fig1 = Figure(figsize=(4,5.5), tight_layout=True); ax1 = fig1.add_subplot(111)
        vals = [int(row["Gold Medal"]), int(row["Silver Medal"]), int(row["Bronze Medal"])]; lbls = ["Gold","Silver","Bronze"]
        medal_colors = [GOLD if self.selected_medal_type=="Gold" else "#FFB700", SILVER if self.selected_medal_type=="Silver" else "#8A8A8A", BRONZE if self.selected_medal_type=="Bronze" else "#A0654B"]
        bars = ax1.bar(lbls, vals, color=medal_colors, alpha=0.9, edgecolor=BG)
        ax1.set_ylabel("Medals"); ax1.grid(axis="y", alpha=0.3)
        for i, v in enumerate(vals): ax1.text(i, v+0.1, str(v), ha="center", color=TEXT, fontsize=12, fontweight="bold")
        for bar in bars: bar.set_picker(5)
        self.explorer_bars = bars; self.explorer_medal_labels = lbls
        canvas1 = FigureCanvasTkAgg(fig1, self.c_chart)
        canvas1.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)
        canvas1.mpl_connect('pick_event', self.on_explorer_medal_click)
 
        section_label(self.d_chart, f"🏃 Medals by Discipline – {chosen}")
        if not medallists.empty:
            country_code = row["country_code"]
            cm = medallists[medallists["country_code"] == country_code].copy()
            cm = cm.dropna(subset=["discipline","event","medal_type"])
            cm["event"] = cm["event"].str.strip(); cm["discipline"] = cm["discipline"].str.strip(); cm["medal_type"] = cm["medal_type"].str.strip()
            if self.selected_medal_type:
                cm = cm[cm["medal_type"].str.contains(self.selected_medal_type, case=False, na=False)]
            cm = cm.drop_duplicates(subset=["discipline","event","medal_type"]).groupby("discipline").size().sort_values(ascending=False)
            if not cm.empty:
                display_labels = [l[:20]+"..." if len(l)>20 else l for l in cm.index[::-1]]
                bar_color = {None: PURPLE, "Gold": GOLD, "Silver": SILVER, "Bronze": BRONZE}.get(self.selected_medal_type, PURPLE)
                fig2 = Figure(figsize=(6,5.5), tight_layout=True); ax2 = fig2.add_subplot(111)
                ax2.barh(display_labels, cm.values[::-1], color=bar_color, alpha=0.85)
                ax2.set_xlabel("Medals"); ax2.grid(axis="x", alpha=0.3)
                for i, v in enumerate(cm.values[::-1]): ax2.text(v+0.2, i, str(v), va="center", color=TEXT, fontsize=9, fontweight="bold")
                FigureCanvasTkAgg(fig2, self.d_chart).get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)
            else: tk.Label(self.d_chart, text="No discipline data for selected medal type", bg=CARD, fg=SUBTEXT).pack(expand=True)
        else: tk.Label(self.d_chart, text="No data available", bg=CARD, fg=SUBTEXT).pack(expand=True)
 
    def on_explorer_medal_click(self, event):
        artist = event.artist
        try:
            if hasattr(self, 'explorer_bars') and artist in self.explorer_bars:
                clicked_medal = self.explorer_medal_labels[list(self.explorer_bars).index(artist)]
                self.selected_medal_type = None if self.selected_medal_type == clicked_medal else clicked_medal
                self.update_explorer()
        except: return
 
    def build_compare(self, tab):
        all_countries = sorted(medals_total["country"].dropna().unique().tolist())
        ctrl = make_card(tab); ctrl.pack(fill="x", padx=14, pady=(14,6))
        tk.Label(ctrl, text="⚔️  Country vs Country", bg=CARD, fg=GOLD, font=("Helvetica",13,"bold")).pack(side="left", padx=12, pady=8)
 
        def make_country_search(parent, default, attr):
            tk.Label(parent, text=f"Country {'A' if attr=='cmp_a_var' else 'B'}:", bg=CARD, fg=TEXT, font=("Helvetica",10)).pack(side="left", padx=(20,4))
            sv = tk.StringVar(); sv.set(default)
            entry = tk.Entry(parent, textvariable=sv, bg=BG, fg=TEXT, insertbackground=TEXT, width=24, font=("Helvetica",10), relief="flat", bd=4)
            entry.pack(side="left", padx=4)
            dw = tk.Toplevel(self.root); dw.withdraw(); dw.overrideredirect(True); dw.configure(bg=CARD)
            lb = tk.Listbox(dw, bg=CARD, fg=TEXT, selectbackground="#2A3D52", selectforeground=TEXT, font=("Helvetica",10), height=6, width=30, relief="flat", bd=2, highlightbackground=SUBTEXT, highlightthickness=1)
            lb.pack()
            for c in all_countries: lb.insert(tk.END, c)
            var = tk.StringVar(value=default); setattr(self, attr, var); sv.set(default)
            def show(*_):
                q = sv.get().lower(); filtered = [c for c in all_countries if q in c.lower()] if q else all_countries
                lb.delete(0, tk.END)
                for c in filtered: lb.insert(tk.END, c)
                if filtered:
                    x = entry.winfo_rootx(); y = entry.winfo_rooty() + entry.winfo_height() + 2
                    dw.geometry(f"300x{min(150, len(filtered)*24)}+{x}+{y}"); dw.deiconify()
                else: dw.withdraw()
                entry.focus_set()
            sv.trace_add("write", show)
            def on_select(_):
                sel = lb.curselection()
                if sel: var.set(lb.get(sel[0])); sv.set(var.get()); dw.withdraw(); self.draw_compare()
            lb.bind("<<ListboxSelect>>", on_select)
            def on_enter(_):
                q = sv.get().lower(); filtered = [c for c in all_countries if q in c.lower()]
                if filtered: var.set(filtered[0]); sv.set(var.get()); dw.withdraw(); self.draw_compare()
            entry.bind("<Return>", on_enter)
            entry.bind("<FocusOut>", lambda _: ctrl.after(200, lambda: dw.withdraw()))
 
        make_country_search(ctrl, "United States of America", "cmp_a_var")
        make_country_search(ctrl, "China", "cmp_b_var")
 
        self.cmp_kpi_frame = make_card(tab); self.cmp_kpi_frame.pack(fill="x", padx=14, pady=(0,4))
        self.cmp_charts_frame = tk.Frame(tab, bg=BG); self.cmp_charts_frame.pack(fill="both", expand=True, padx=14, pady=(0,10))
        self.draw_compare()
 
    def _parse_list_field(self, val):
        import ast
        if pd.isna(val): return []
        try:
            result = ast.literal_eval(str(val))
            if isinstance(result, list): return [str(x).strip() for x in result]
        except: pass
        return [str(val).strip()]
 
    def draw_compare(self):
        ca = self.cmp_a_var.get(); cb = self.cmp_b_var.get()
        for w in self.cmp_kpi_frame.winfo_children(): w.destroy()
        for w in self.cmp_charts_frame.winfo_children(): w.destroy()
        COLOR_A = "#00A8E8"; COLOR_B = "#FF6B4A"
 
        def medal_row(country):
            r = medals_total[medals_total["country"] == country]
            if r.empty: return 0,0,0,0
            r = r.iloc[0]; return int(r.get("Gold Medal",0)), int(r.get("Silver Medal",0)), int(r.get("Bronze Medal",0)), int(r.get("Total",0))
 
        def athlete_count(c): return 0 if athletes.empty else int((athletes["country"]==c).sum())
        def coach_count(c): return 0 if coaches.empty else int((coaches["country"]==c).sum())
        def discipline_count(c):
            if athletes.empty: return 0
            sub = athletes[athletes["country"]==c]["disciplines"].dropna()
            discs = set()
            for v in sub: discs.update(self._parse_list_field(v))
            return len(discs)
        def top_disciplines(c, n=8):
            if athletes.empty: return pd.Series(dtype=int)
            sub = athletes[athletes["country"]==c]["disciplines"].dropna()
            all_d = []
            for v in sub: all_d.extend(self._parse_list_field(v))
            return pd.Series(all_d).value_counts().head(n)
 
        ga,sa,ba,ta = medal_row(ca); gb,sb,bb,tb = medal_row(cb)
        ath_a,ath_b = athlete_count(ca), athlete_count(cb)
        cch_a,cch_b = coach_count(ca), coach_count(cb)
        dis_a,dis_b = discipline_count(ca), discipline_count(cb)
 
        def kpi_block(parent, label, va, vb, color_a=COLOR_A, color_b=COLOR_B):
            f = tk.Frame(parent, bg=CARD, padx=8, pady=4); f.pack(side="left", padx=6)
            tk.Label(f, text=label, bg=CARD, fg=SUBTEXT, font=("Helvetica",8)).pack()
            row = tk.Frame(f, bg=CARD); row.pack()
            tk.Label(row, text=str(va), bg=CARD, fg=color_a, font=("Helvetica",16,"bold")).pack(side="left", padx=4)
            tk.Label(row, text="vs", bg=CARD, fg=SUBTEXT, font=("Helvetica",9)).pack(side="left")
            tk.Label(row, text=str(vb), bg=CARD, fg=color_b, font=("Helvetica",16,"bold")).pack(side="left", padx=4)
 
        tk.Label(self.cmp_kpi_frame, text=f"  {ca}  vs  {cb}", bg=CARD, fg=GOLD, font=("Helvetica",11,"bold")).pack(anchor="w", padx=12, pady=(6,2))
        krow = tk.Frame(self.cmp_kpi_frame, bg=CARD); krow.pack(fill="x", padx=8, pady=(0,6))
        kpi_block(krow, "🥇 Gold", ga, gb, GOLD, GOLD); kpi_block(krow, "🥈 Silver", sa, sb, SILVER, SILVER)
        kpi_block(krow, "🥉 Bronze", ba, bb, BRONZE, BRONZE); kpi_block(krow, "🏅 Total", ta, tb)
        kpi_block(krow, "🏃 Athletes", ath_a, ath_b); kpi_block(krow, "🎽 Coaches", cch_a, cch_b); kpi_block(krow, "🎯 Disciplines", dis_a, dis_b)
 
        chart_row = tk.Frame(self.cmp_charts_frame, bg=BG); chart_row.pack(fill="both", expand=True)
 
        c1 = make_card(chart_row); c1.pack(side="left", fill="both", expand=True, padx=(0,6))
        section_label(c1, "📊  Overall Performance Radar")
        fig1 = Figure(figsize=(5,4), tight_layout=True); ax1 = fig1.add_subplot(111, projection='polar')
        categories = ['Gold','Silver','Bronze','Athletes','Disciplines']
        va_vals = [ga,sa,ba,ath_a,dis_a]; vb_vals = [gb,sb,bb,ath_b,dis_b]
        mx = max(max(va_vals), max(vb_vals), 1)
        van = [v/mx*100 for v in va_vals]+[va_vals[0]/mx*100]; vbn = [v/mx*100 for v in vb_vals]+[vb_vals[0]/mx*100]
        angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False).tolist(); angles += angles[:1]
        ax1.plot(angles, van, 'o-', linewidth=2.5, color=COLOR_A, markersize=7, label=ca[:16]); ax1.fill(angles, van, alpha=0.15, color=COLOR_A)
        ax1.plot(angles, vbn, 's-', linewidth=2.5, color=COLOR_B, markersize=7, label=cb[:16]); ax1.fill(angles, vbn, alpha=0.15, color=COLOR_B)
        ax1.set_xticks(angles[:-1]); ax1.set_xticklabels(categories, color=TEXT, size=9)
        ax1.set_ylim(0,100); ax1.set_yticks([20,40,60,80,100]); ax1.set_yticklabels(['20','40','60','80','100'], color=SUBTEXT, size=7)
        ax1.grid(True, color=SUBTEXT, alpha=0.3); ax1.legend(loc='upper right', bbox_to_anchor=(1.3,1.1), facecolor=CARD, labelcolor=TEXT, fontsize=8)
        FigureCanvasTkAgg(fig1, c1).get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)
 
        c2 = make_card(chart_row); c2.pack(side="left", fill="both", expand=True, padx=(6,6))
        section_label(c2, "🦋  Shared Disciplines – Butterfly")
        disc_a = top_disciplines(ca, 10); disc_b = top_disciplines(cb, 10)
        shared = sorted(set(disc_a.index) & set(disc_b.index))
        fig2 = Figure(figsize=(5,4), tight_layout=True); ax2 = fig2.add_subplot(111)
        if shared:
            va2 = [disc_a.get(d,0) for d in shared]; vb2 = [disc_b.get(d,0) for d in shared]; y = np.arange(len(shared))
            ax2.barh(y, [-v for v in va2], color=COLOR_A, alpha=0.85, label=ca[:14])
            ax2.barh(y, vb2, color=COLOR_B, alpha=0.85, label=cb[:14], hatch="////")
            ax2.set_yticks(y); ax2.set_yticklabels([d[:18] for d in shared], fontsize=8)
            ax2.set_xlabel("Athletes"); ax2.grid(axis="x", alpha=0.3); ax2.axvline(x=0, color=TEXT, linewidth=0.8)
            ax2.legend(facecolor=CARD, labelcolor=TEXT, fontsize=8, loc="best")
        else: ax2.text(0.5,0.5, "No shared disciplines", ha="center", va="center", transform=ax2.transAxes, color=SUBTEXT, fontsize=10)
        FigureCanvasTkAgg(fig2, c2).get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)
 
        c3 = make_card(chart_row); c3.pack(side="left", fill="both", expand=True, padx=(6,0))
        section_label(c3, "🎯  KSI Medal Score  (Gold×3 + Silver×2 + Bronze×1)")
        ksi_a = ga*3+sa*2+ba; ksi_b = gb*3+sb*2+bb
        fig3 = Figure(figsize=(4,4), tight_layout=True); ax3 = fig3.add_subplot(111)
        bars3 = ax3.bar([ca[:16],cb[:16]], [ksi_a,ksi_b], color=[COLOR_A,COLOR_B], alpha=0.9, edgecolor=BG, linewidth=1.2, width=0.45)
        ax3.set_ylabel("KSI Score"); ax3.grid(axis="y", alpha=0.3)
        for bar, val in zip(bars3, [ksi_a,ksi_b]):
            ax3.text(bar.get_x()+bar.get_width()/2, val+max(ksi_a,ksi_b)*0.02, str(val), ha="center", va="bottom", color=TEXT, fontsize=14, fontweight="bold")
        ax3.set_title(f"🏆 {(ca if ksi_a>ksi_b else cb)[:14]} leads" if ksi_a!=ksi_b else "🤝 It's a tie!", color=GOLD if ksi_a!=ksi_b else GREEN, fontsize=9, pad=4)
        FigureCanvasTkAgg(fig3, c3).get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)
 
    def build_table(self, tab):
        ctrl = make_card(tab); ctrl.pack(fill="x", padx=14, pady=(14,6))
        tk.Label(ctrl, text="📊  Data Browser", bg=CARD, fg=GOLD, font=("Helvetica",13,"bold")).pack(side="left", padx=10, pady=8)
        datasets = {
            "Medal Totals": medals_total, "Medallists": medallists,
            "Athletes": athletes[["name","gender","country","disciplines","height","weight"]],
            "Coaches": coaches[["name","gender","country","disciplines"]],
            "Events": events, "Teams": teams[["team","team_gender","country","discipline","num_athletes"]],
            "Officials": tech_officials[["name","gender","disciplines","organisation"]],
        }
        ds_var = tk.StringVar(value="Medal Totals")
        combo = ttk.Combobox(ctrl, textvariable=ds_var, values=list(datasets.keys()), width=20, state="readonly"); combo.pack(side="left", padx=10)
        rows_label = tk.Label(ctrl, text="", bg=CARD, fg=SUBTEXT, font=("Helvetica",9)); rows_label.pack(side="left", padx=20)
        tk.Label(ctrl, text="Filter:", bg=CARD, fg=TEXT, font=("Helvetica",10)).pack(side="left", padx=(20,4))
        filter_var = tk.StringVar()
        tk.Entry(ctrl, textvariable=filter_var, bg=BG, fg=TEXT, insertbackground=TEXT, width=20, font=("Helvetica",10), relief="flat", bd=4).pack(side="left")
 
        def export_csv():
            df = datasets[ds_var.get()]; os.makedirs("./outputs", exist_ok=True)
            out = f"./outputs/{ds_var.get().replace(' ','_')}_export.csv"; df.to_csv(out, index=False)
            messagebox.showinfo("Exported", f"Saved to:\n{out}")
        tk.Button(ctrl, text="⬇ Export CSV", bg=ACCENT, fg=BG, relief="flat", font=("Helvetica",9,"bold"), padx=10, pady=4, command=export_csv).pack(side="right", padx=10)
 
        tree_frame = tk.Frame(tab, bg=BG); tree_frame.pack(fill="both", expand=True, padx=14, pady=(0,14))
        tree = ttk.Treeview(tree_frame, show="headings", height=20)
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y"); hsb.pack(side="bottom", fill="x"); tree.pack(fill="both", expand=True)
 
        def load_table(*_):
            df = datasets[ds_var.get()].copy(); q = filter_var.get().lower()
            if q:
                mask = df.astype(str).apply(lambda col: col.str.lower().str.contains(q)).any(axis=1); df = df[mask]
            rows_label.config(text=f"{len(df):,} rows"); tree.delete(*tree.get_children())
            cols = list(df.columns); tree["columns"] = cols
            for col in cols: tree.heading(col, text=col); tree.column(col, width=max(120, len(col)*10), anchor="w")
            for _, row in df.head(500).iterrows(): tree.insert("", "end", values=[str(v)[:60] for v in row.values])
 
        combo.bind("<<ComboboxSelected>>", load_table); filter_var.trace_add("write", load_table); load_table()
 
 
if __name__ == "__main__":
    root = tk.Tk(); app = OlympicsApp(root); root.mainloop()