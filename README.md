# Trailer Attachment Dashboard

This project is a **Streamlit dashboard** for analyzing trailer attachment status in freight operations. It provides insights into trailer loads across multiple sites, regions, and dates, including counts of AZNG and AZNU trailers, attached and not-attached trailers.

---

## Features

- Filter by **Date Range** and **Region**
- View **Trailer Attachment Status** (attached / not attached)
- Count of **AZNG and AZNU trailers** per site, region, and date
- KPIs: total loads, not-attached % loads, total VRIDs, AZNG vs AZNU counts
- Detailed table for load-level analysis
- Works with **OTR runner type only**

---

## Files

- `lazy_schedulecount.py` – Main Streamlit dashboard
- `lazy_fmc_processed.csv` – Sample dataset (replace with actual data)
- `R_codes.csv` – Mapping of site codes to regions

---

## How to Run

1. Clone the repository:
```bash
git clone https://github.com/YourUsername/trailer_dashboard.git
