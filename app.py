import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import os

# ==========================
# LOAD HMDB REFERENCE TABLE
# ==========================
@st.cache_data
def load_hmdb(csv_path: str = "hmdb_reference.csv") -> pd.DataFrame | None:
    try:
        return pd.read_csv(csv_path)
    except FileNotFoundError:
        return None

hmdb_df = load_hmdb()

# ==========================
# LOAD LACTATE CSV
# ==========================
@st.cache_data
def load_lactate(csv_path: str = "Data/lactate.csv") -> pd.DataFrame | None:
    try:
        df = pd.read_csv(csv_path)
        # Ensure required columns exist
        if not all(col in df.columns for col in ["ppm", "intensity"]):
            st.error("Lactate CSV must contain 'ppm' and 'intensity' columns.")
            return None
        return df
    except FileNotFoundError:
        st.error(f"Lactate CSV not found in '{csv_path}'.")
        return None

lactate_df = load_lactate()

# ==========================
# PLOT FUNCTION WITH ZOOM
# ==========================
def plot_spectrum(sample_df: pd.DataFrame, title="Spectrum", zoom_regions=None):
    """
    Plot NMR spectrum with optional zoom-ins.
    
    Parameters:
        sample_df: DataFrame with 'ppm' and 'intensity' columns
        title: title of the spectrum
        zoom_regions: list of tuples [(ppm_min1, ppm_max1), (ppm_min2, ppm_max2)]
    """
    fig = plt.figure(figsize=(12, 4))
    if zoom_regions:
        gs = GridSpec(1, len(zoom_regions)+1, width_ratios=[2]+[1]*len(zoom_regions))
    else:
        gs = GridSpec(1, 1)
    
    # Sort by ppm descending
    sample_df = sample_df.sort_values("ppm", ascending=False)
    
    # Main spectrum
    ax_main = fig.add_subplot(gs[0])
    ax_main.plot(sample_df["ppm"], sample_df["intensity"], color='blue', linewidth=1.5)
    ax_main.set_xlabel("ppm")
    ax_main.set_ylabel("Intensity")
    ax_main.invert_xaxis()
    ax_main.set_title(title)
    ax_main.grid(True, linestyle='--', alpha=0.5)
    
    # Zoomed-in spectra
    if zoom_regions:
        for i, region in enumerate(zoom_regions):
            ppm_min, ppm_max = region
            ax_zoom = fig.add_subplot(gs[i+1])
            mask = (sample_df["ppm"] >= ppm_min) & (sample_df["ppm"] <= ppm_max)
            df_zoom = sample_df[mask]
            ax_zoom.plot(df_zoom["ppm"], df_zoom["intensity"], color='green', linewidth=1.5)
            ax_zoom.set_xlabel("ppm")
            ax_zoom.set_title(f"Zoom {i+1}")
            ax_zoom.invert_xaxis()
            ax_zoom.grid(True, linestyle='--', alpha=0.5)
            # Highlight zoom region on main spectrum
            ax_main.axvspan(ppm_min, ppm_max, color='gray', alpha=0.2)

    st.pyplot(fig)

# ==========================
# STREAMLIT UI
# ==========================
st.title("🧪 NMR Peak Extractor + HMDB Comparator")

# -------------------------
# Experiment metadata
# -------------------------
st.sidebar.header("NMR Experiment Metadata")
field_strength = st.sidebar.text_input("Magnetic Field Strength (MHz)", "600")
pulse_seq = st.sidebar.text_input("Pulse Sequence", "90°")
internal_std = st.sidebar.text_input("Internal Standard", "0.1 mM DSS")
num_scans = st.sidebar.number_input("Number of Scans (NS)", value=256)

st.write(f"**Field Strength:** {field_strength} MHz")
st.write(f"**Pulse Sequence:** {pulse_seq}")
st.write(f"**Internal Standard:** {internal_std}")
st.write(f"**Number of Scans:** {num_scans}")

# -------------------------
# Metabolite search
# -------------------------
st.sidebar.header("Search Metabolites")
search_name = st.sidebar.text_input("Enter metabolite name")

if search_name and hmdb_df is not None:
    matches = hmdb_df[hmdb_df['Name'].str.contains(search_name, case=False, na=False)]
    if not matches.empty:
        st.subheader(f"Results for '{search_name}'")
        for _, row in matches.iterrows():
            st.markdown(f"### {row['Name']} ({row['HMDB_ID']})")
            st.write(f"CAS: {row.get('CAS','')}, Formula: {row.get('Formula','')}")
            st.write(f"Predicted peaks: {row.get('predicted_ppm','')}")
            st.markdown(f"[View on HMDB](https://hmdb.ca/metabolites/{row['HMDB_ID']})")
            st.image(f"https://hmdb.ca/metabolites/{row['HMDB_ID']}.png", width=200)

        # Plot lactate spectrum if searched
        if search_name.lower() == "lactate" and lactate_df is not None:
            st.subheader(f"📊 Spectrum for '{search_name}'")
            # Example zoom regions (adjust to your peak ppm ranges)
            zoom_regions = [(4.04, 4.20), (1.25, 1.38)]
            plot_spectrum(lactate_df, title=f"{search_name} Spectrum", zoom_regions=zoom_regions)
    else:
        st.warning(f"No metabolite found with the name '{search_name}'.")
elif search_name:
    st.warning("⚠️ No local HMDB file found. Add `hmdb_reference.csv` to the app folder.")
