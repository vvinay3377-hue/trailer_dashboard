import pandas as pd
import streamlit as st

st.set_page_config(page_title="Trailer Attachment Dashboard", layout="wide")
st.title("Trailer Attachment Analysis")

# ---------------- LOAD DATA ----------------
file_path = "lazy_fmc_processed.csv"
df = pd.read_csv(file_path)

df["site"] = df["Lane"].astype(str).str[:4]

region_code = "R_codes.csv"
df_r = pd.read_csv(region_code)

df["origin_region"] = df["site"].map(
    df_r.groupby("origin")["origin_region"].first()
)

df = df[df["runner_type"] == "OTR"]

df["trailer_status"] = df["Trailer Id"].apply(
    lambda x: "not_attached" if pd.isna(x) or str(x).strip() == "" else "trailer_attached"
)


df["Scheduled Truck Arrival - 2 date"] = pd.to_datetime(
    df["Scheduled Truck Arrival - 2 date"],
    errors="coerce"
)

# ---------------- FILTERS ----------------
min_date = df["Scheduled Truck Arrival - 2 date"].min().date()
max_date = df["Scheduled Truck Arrival - 2 date"].max().date()

col1, col2 = st.columns(2)

with col1:
    start_date, end_date = st.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

with col2:
    selected_region = st.multiselect(
        "Region",
        sorted(df["origin_region"].dropna().unique())
    )

# Apply filters on raw data
filtered_df = df[
    (df["Scheduled Truck Arrival - 2 date"].dt.date >= start_date) &
    (df["Scheduled Truck Arrival - 2 date"].dt.date <= end_date)
]

if selected_region:
    filtered_df = filtered_df[filtered_df["origin_region"].isin(selected_region)]

# ---------------- AGGREGATION ----------------
summary = (
    filtered_df.groupby([
        "Scheduled Truck Arrival - 2 date",
        "origin_region",
        "site",
        
        "trailer_status"
    ])
    .size()
    .unstack(fill_value=0)
    .reset_index()
)

summary["total_loads"] = (
    summary.get("trailer_attached", 0) +
    summary.get("not_attached", 0)
)

summary["not_attached_pct"] = (
    summary.get("not_attached", 0) / summary["total_loads"]
)

# ---------------- KPIs ----------------
total_loads = int(summary["total_loads"].sum())
total_not_attached = int(summary.get("not_attached", 0).sum())
risk_pct = (total_not_attached / total_loads * 100) if total_loads else 0

k1, k2, k3 = st.columns(3)

k1.metric("Total Loads", total_loads)
k2.metric("Not Attached Loads", total_not_attached)
k3.metric("Not Attached %", f"{risk_pct:.2f}%")

# ---------------- TABLE ----------------
st.subheader("Detailed View")
st.dataframe(summary, use_container_width=True)

# ---------------- AZNG / AZNU CLASSIFICATION ----------------
def classify_trailer(row):
    if row["Equipment Type"] == "FIFTY_THREE_FOOT_TRUCK":
        return "AZNG"
    if row["Equipment Type"] == "FIFTY_THREE_FOOT_CONTAINER":
        return "AZNU"
    return "OTHER"

filtered_df["trailer_type"] = filtered_df.apply(classify_trailer, axis=1)

# ---------------- SITE / REGION / DATE WISE AZNG vs AZNU VRID DASHBOARD ----------------
st.subheader("Site × Region × Date VRID Summary (AZNG vs AZNU)")

# Aggregate counts per site, region, date, and trailer type
vrid_site_summary = (
    filtered_df.groupby(
        ["Scheduled Truck Arrival - 2 date", "origin_region", "site", "trailer_type"]
    )
    .size()
    .unstack(fill_value=0)  # trailer_type becomes columns: AZNG, AZNU, OTHER, NO_TRAILER
    .reset_index()
)

# Ensure AZNG / AZNU columns exist
for col in ["AZNG", "AZNU"]:
    if col not in vrid_site_summary.columns:
        vrid_site_summary[col] = 0

# Total VRIDs per row
vrid_site_summary["total_vrids"] = vrid_site_summary[["AZNG", "AZNU"]].sum(axis=1)

# Display KPIs for this filtered view
total_vrids = int(vrid_site_summary["total_vrids"].sum())
total_azng = int(vrid_site_summary["AZNG"].sum())
total_aznu = int(vrid_site_summary["AZNU"].sum())

c1, c2, c3 = st.columns(3)
c1.metric("Total VRIDs", total_vrids)
c2.metric("AZNG VRIDs", total_azng)
c3.metric("AZNU VRIDs", total_aznu)

# Show detailed table
st.dataframe(vrid_site_summary, use_container_width=True)

# Optional: Stacked bar chart by site
site_chart = (
    vrid_site_summary.groupby("site")[["AZNG", "AZNU"]]
    .sum()
    .reset_index()
)
st.subheader("Site-wise AZNG vs AZNU VRIDs")
st.bar_chart(site_chart.set_index("site"))

