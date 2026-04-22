"""
RECKONER - Electricity Tariff Reckoner
Python/tkinter port of the original VB.NET EPSM application.
Calculates residential electricity bills based on ECG tariff bands (GHS).
"""

import tkinter as tk
from tkinter import ttk, messagebox

# ── Tariff constants (Residential) ──────────────────────────────────────────
NEL          = 2   / 100   # National Electrification Levy
STREET_LIGHT = 3   / 100   # Street Lighting Levy
VAT          = 12.5 / 100
NHIL_GETFUND = 5   / 100

LEVIES_BASE  = NEL + STREET_LIGHT                        # 0.05  (no VAT band)
LEVIES_FULL  = NEL + STREET_LIGHT + VAT + NHIL_GETFUND  # 0.225 (VAT band)

SERVICE_LIFELINE = 2.13
SERVICE_MID      = 10.7309
SERVICE_HIGH     = 12.4282   # kept for possible future use

RATE_LIFELINE = 41.9065 / 100   # ≤ 30 kWh
RATE_MID      = 89.0422 / 100   # 31–300 kWh
RATE_UPPER    = 115.5595 / 100  # 301–900 kWh
RATE_PEAK     = 128.3995 / 100  # > 900 kWh


# ── Billing logic ────────────────────────────────────────────────────────────

def calc_residential(units: float) -> tuple[float, float, float]:
    """
    Returns (energy_charge, levies_and_charges, total_bill) in GHS.
    Mirrors the original VB tier logic, with corrected variable reads.
    """
    units = max(0.0, units)

    if units <= 30:
        energy   = units * RATE_LIFELINE + SERVICE_LIFELINE
        levies   = 0.0          # lifeline customers: levies not applied
        total    = energy

    elif units <= 300:
        energy   = units * RATE_MID
        levies   = SERVICE_MID + LEVIES_BASE * energy
        total    = energy + levies

    elif units <= 900:
        tier1    = 300 * RATE_MID
        tier2    = (units - 300) * RATE_UPPER
        energy   = tier1 + tier2
        levies   = SERVICE_MID + LEVIES_BASE * energy
        total    = energy + levies

    else:  # > 900
        tier1    = 300 * RATE_MID
        tier2    = 600 * RATE_UPPER           # 300→900
        tier3    = (units - 900) * RATE_PEAK
        energy   = tier1 + tier2 + tier3
        levies   = SERVICE_MID + LEVIES_BASE * energy
        total    = energy + levies

    return round(energy, 2), round(levies, 2), round(total, 2)


def calc_non_residential(units: float) -> tuple[float, float, float]:
    """Non-residential uses full levy stack including VAT + NHIL/GETFUND."""
    units = max(0.0, units)

    if units <= 30:
        energy = units * RATE_LIFELINE + SERVICE_LIFELINE
        levies = 0.0
        total  = energy
    elif units <= 300:
        energy = units * RATE_MID
        levies = SERVICE_MID + LEVIES_FULL * energy
        total  = energy + levies
    elif units <= 900:
        tier1  = 300 * RATE_MID
        tier2  = (units - 300) * RATE_UPPER
        energy = tier1 + tier2
        levies = SERVICE_MID + LEVIES_FULL * energy
        total  = energy + levies
    else:
        tier1  = 300 * RATE_MID
        tier2  = 600 * RATE_UPPER
        tier3  = (units - 900) * RATE_PEAK
        energy = tier1 + tier2 + tier3
        levies = SERVICE_MID + LEVIES_FULL * energy
        total  = energy + levies

    return round(energy, 2), round(levies, 2), round(total, 2)


def units_from_amount_residential(target: float) -> float:
    """Binary-search inverse: find units whose bill ≈ target amount."""
    lo, hi = 0.0, 10_000.0
    for _ in range(60):
        mid = (lo + hi) / 2
        _, _, total = calc_residential(mid)
        if total < target:
            lo = mid
        else:
            hi = mid
    return round((lo + hi) / 2, 2)


def units_from_amount_non_residential(target: float) -> float:
    lo, hi = 0.0, 10_000.0
    for _ in range(60):
        mid = (lo + hi) / 2
        _, _, total = calc_non_residential(mid)
        if total < target:
            lo = mid
        else:
            hi = mid
    return round((lo + hi) / 2, 2)


# ── GUI ──────────────────────────────────────────────────────────────────────

BG        = "#FFC080"   # original VB form background (orange-ish)
HEADER_BG = "#C0C0FF"   # original label background (lilac)
RED_BTN   = "#FF8080"
FONT_TITLE = ("Century Gothic", 15, "bold")
FONT_H     = ("Century Gothic", 12, "bold")
FONT_LBL   = ("Century Gothic", 10, "bold")
FONT_RADIO = ("Century Gothic", 11, "bold")


class ReckonerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("EPSM – Tariff Reckoner")
        self.resizable(False, False)
        self.configure(bg=BG)

        self._build_ui()

    # ── UI Construction ──────────────────────────────────────────────────────

    def _build_ui(self):
        pad = {"padx": 12, "pady": 6}

        # ── Title ────────────────────────────────────────────────────────────
        title_frame = tk.Frame(self, bg=HEADER_BG)
        title_frame.pack(fill="x", padx=20, pady=(18, 4))
        tk.Label(title_frame, text="Tariff Reckoner", font=FONT_TITLE,
                 bg=HEADER_BG).pack(pady=6)

        # "Click here" instruction button
        tk.Button(title_frame, text="Click here for instructions",
                  font=FONT_LBL, bg=RED_BTN, relief="raised",
                  command=self._show_instructions).pack(pady=(0, 6))

        # ── Two-column body ──────────────────────────────────────────────────
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=20, pady=6)

        left  = tk.Frame(body, bg=BG)
        left.pack(side="left", fill="y", padx=(0, 30))
        right = tk.Frame(body, bg=BG)
        right.pack(side="left", fill="y")

        # ── Customer Type ────────────────────────────────────────────────────
        tk.Label(left, text="Customer Type", font=FONT_H,
                 bg=HEADER_BG).pack(anchor="w", pady=(0, 4))

        self.customer_var = tk.StringVar(value="residential")
        tk.Radiobutton(left, text="Residential", variable=self.customer_var,
                       value="residential", font=FONT_RADIO,
                       bg=BG, activebackground=BG).pack(anchor="w")
        tk.Radiobutton(left, text="Non-Residential", variable=self.customer_var,
                       value="non_residential", font=FONT_RADIO,
                       bg=BG, activebackground=BG).pack(anchor="w")

        tk.Frame(left, height=16, bg=BG).pack()

        # ── Computation Reference ────────────────────────────────────────────
        tk.Label(left, text="Computation Reference", font=FONT_H,
                 bg=HEADER_BG).pack(anchor="w", pady=(0, 4))

        self.mode_var = tk.StringVar(value="cons_to_amt")
        tk.Radiobutton(left, text="Consumption → Amount",
                       variable=self.mode_var, value="cons_to_amt",
                       font=FONT_RADIO, bg=BG, activebackground=BG,
                       command=self._update_labels).pack(anchor="w")
        tk.Radiobutton(left, text="Amount → Consumption",
                       variable=self.mode_var, value="amt_to_cons",
                       font=FONT_RADIO, bg=BG, activebackground=BG,
                       command=self._update_labels).pack(anchor="w")

        tk.Frame(left, height=16, bg=BG).pack()

        # Calculate button
        tk.Button(left, text="Calculate", font=("Century Gothic", 12, "bold"),
                  bg="#80C080", width=14, relief="raised",
                  command=self._calculate).pack(pady=4)

        tk.Button(left, text="Clear", font=FONT_LBL,
                  bg="#D0D0D0", width=14,
                  command=self._clear).pack(pady=2)

        # ── Input / Output fields (right column) ─────────────────────────────
        tk.Label(right, text="Computation", font=FONT_H,
                 bg=HEADER_BG).pack(anchor="w", pady=(0, 10))

        fields = tk.Frame(right, bg=BG)
        fields.pack(anchor="w")

        # Input label changes depending on mode
        self.lbl_input = tk.Label(fields, text="Consumption (kWh)",
                                  font=FONT_LBL, bg=BG)
        self.lbl_input.grid(row=0, column=0, sticky="w", pady=4, padx=(0, 10))
        self.entry_input = tk.Entry(fields, width=14, font=FONT_LBL)
        self.entry_input.grid(row=0, column=1, pady=4)

        tk.Label(fields, text="Levies & Charges (GHS)",
                 font=FONT_LBL, bg=BG).grid(row=1, column=0, sticky="w", pady=4)
        self.entry_levies = tk.Entry(fields, width=14, font=FONT_LBL,
                                     state="readonly")
        self.entry_levies.grid(row=1, column=1, pady=4)

        # Output label changes depending on mode
        self.lbl_output = tk.Label(fields, text="Amount (GHS)",
                                   font=FONT_LBL, bg=BG)
        self.lbl_output.grid(row=2, column=0, sticky="w", pady=4)
        self.entry_output = tk.Entry(fields, width=14, font=FONT_LBL,
                                      state="readonly")
        self.entry_output.grid(row=2, column=1, pady=4)

        # ── Tariff breakdown info box ─────────────────────────────────────────
        tk.Frame(right, height=10, bg=BG).pack()
        info_frame = tk.LabelFrame(right, text=" Tariff Bands (Residential) ",
                                   font=FONT_LBL, bg=BG, padx=8, pady=4)
        info_frame.pack(fill="x", pady=4)
        info_text = (
            "≤ 30 kWh  : GHS 0.4191/kWh  (Lifeline)\n"
            "31–300    : GHS 0.8904/kWh\n"
            "301–900   : GHS 1.1556/kWh\n"
            "> 900     : GHS 1.2840/kWh\n"
            "Levies: NEL 2% + Street 3%"
        )
        tk.Label(info_frame, text=info_text, font=("Courier New", 9),
                 bg=BG, justify="left").pack(anchor="w")

        # ── Status bar ───────────────────────────────────────────────────────
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(self, textvariable=self.status_var, font=("Arial", 9),
                 bg="#404040", fg="white", anchor="w").pack(
                     fill="x", side="bottom", padx=0, pady=0)

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _update_labels(self):
        if self.mode_var.get() == "cons_to_amt":
            self.lbl_input.config(text="Consumption (kWh)")
            self.lbl_output.config(text="Amount (GHS)")
        else:
            self.lbl_input.config(text="Amount (GHS)")
            self.lbl_output.config(text="Consumption (kWh)")
        self._clear_outputs()

    def _set_output(self, levies: float, output: float):
        for widget, val in ((self.entry_levies, levies),
                            (self.entry_output, output)):
            widget.config(state="normal")
            widget.delete(0, "end")
            widget.insert(0, f"{val:.2f}")
            widget.config(state="readonly")

    def _clear_outputs(self):
        for widget in (self.entry_levies, self.entry_output):
            widget.config(state="normal")
            widget.delete(0, "end")
            widget.config(state="readonly")

    def _clear(self):
        self.entry_input.delete(0, "end")
        self._clear_outputs()
        self.status_var.set("Ready")

    def _show_instructions(self):
        messagebox.showinfo(
            "Instructions",
            "1. Select your preferred computation direction.\n"
            "2. Select your customer type.\n"
            "3. Enter a value in the input field.\n"
            "4. Press Calculate."
        )

    # ── Core calculation ─────────────────────────────────────────────────────

    def _calculate(self):
        raw = self.entry_input.get().strip()
        if not raw:
            messagebox.showwarning("Input required", "Please enter a value.")
            return
        try:
            value = float(raw)
            if value < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid input",
                                 "Please enter a valid non-negative number.")
            return

        customer  = self.customer_var.get()
        mode      = self.mode_var.get()
        calc_fn   = (calc_residential if customer == "residential"
                     else calc_non_residential)

        if mode == "cons_to_amt":
            energy, levies, total = calc_fn(value)
            self._set_output(levies, total)
            self.status_var.set(
                f"Energy charge: GHS {energy:.2f}  |  "
                f"Levies: GHS {levies:.2f}  |  Total: GHS {total:.2f}"
            )
        else:   # amount → consumption
            inv_fn = (units_from_amount_residential if customer == "residential"
                      else units_from_amount_non_residential)
            units = inv_fn(value)
            energy, levies, _ = calc_fn(units)
            self._set_output(levies, units)
            self.status_var.set(
                f"Estimated consumption: {units:.2f} kWh  |  "
                f"Energy: GHS {energy:.2f}  |  Levies: GHS {levies:.2f}"
            )


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = ReckonerApp()
    app.mainloop()