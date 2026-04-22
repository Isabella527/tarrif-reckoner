# ⚡ EPSM Tariff Reckoner
<img width="1398" height="786" alt="tr" src="https://github.com/user-attachments/assets/928dcb4d-3a37-41aa-9e38-79778571b22f" />


A desktop-based electricity billing system that computes energy charges and levies using Ghana ECG tariff bands.

Built with **Python + Tkinter**, this project recreates and improves a legacy VB.NET billing tool with a cleaner interface, better structure, and more transparent tariff modeling.

---

##  Overview

The **EPSM Tariff Reckoner** is designed to simulate real-world electricity billing by applying tiered pricing and regulatory levies.  

It supports both:
- Forward calculation (**consumption → cost**)
- Reverse estimation (**cost → consumption**)

This makes it useful not just as a calculator, but also as a **planning and analysis tool**.

---

##  Features

- Residential & Non-Residential billing modes  
-  Bidirectional computation  
- Consumption → Cost  
- Cost → Consumption  
-  Tier-based tariff system  
-  Automatic levy computation  
- VAT  
- NHIL / GETFund  
- National Electrification Levy (NEL)  
- Street Lighting Levy  
-  Interactive GUI built with Tkinter  
-  Fast and lightweight (no external dependencies)

---

##  How It Works

Electricity billing is calculated using a **progressive tier system**, where different portions of consumption are billed at different rates.

### Tariff Bands (Residential)

| Band        | Range (kWh) | Rate (GHS/kWh) |
|------------|------------|---------------|
| Lifeline   | ≤ 30       | 0.4191        |
| Mid        | 31–300     | 0.8904        |
| Upper      | 301–900    | 1.1556        |
| Peak       | > 900      | 1.2840        |

### Levies & Charges

- **NEL**: 2%  
- **Street Lighting**: 3%  
- **VAT + NHIL/GETFund** (applied to non-residential)

### Calculation Logic

- Charges are computed **per tier**, not at a flat rate  
- Levies are applied as **percentage-based additions**  
- Reverse computation (Amount → Consumption) is solved using a **binary search approximation**

---

##  Preview

<img width="501" height="395" alt="pic3" src="https://github.com/user-attachments/assets/2eaf18b5-5f6d-4989-93c0-ee0d5241f96c" />


---
### 📌 Key Concepts

Tiered billing systems used in real-world utilities
Binary search inversion for estimating consumption
Event-driven GUI programming with Tkinter
Separation of logic and interface for maintainability

### Example Use Cases
Estimate your monthly electricity bill
Reverse-calculate consumption from a known bill
Analyze cost differences across usage levels
Educational tool for understanding utility pricing systems

### Future Improvements
Export bill as PDF
Historical usage tracking
Web-based version (Flask / React)
Mobile-friendly interface
TinyML integration for smart energy devices

### 👩🏽‍💻 Author
Isabella Opoku-Ware

##  Installation

```bash
git clone https://github.com/yourusername/tariff-reckoner.git
cd tariff-reckoner
pip install -r requirements.txt
python src/reckoner.py



