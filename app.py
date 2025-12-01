import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
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
        # Ensure columns exist
        if not all(col in df.columns for col in ["ppm", "intensity"]):
            st.error("Lactate CSV must contain 'ppm' and 'intensity' columns.")
            return None
        return df
    except FileNotFoundError:
        st.error(f"Lactate CSV not found in '{csv_path}'.")
        return None

lactate_df = load_lactate()

# ==========================
# PLOT FUNCTION
# ==========================
def plot_spectrum(sample_df: pd.DataFrame, title="Spectrum"):
    fig, ax = plt.subplots(figsize=(10, 4))
    
    # Sort by ppm descending (NMR convention)
    sample_df = sample_df.sort_values("ppm", ascending=False)
    
    # Plot as a line
    ax.plot(sample_df["ppm"], sample_df["intensity"], color='blue', linewidth=1.5)
    
    ax.set_xlabel("ppm")
    ax.set_ylabel("Intensity")
    ax.invert_xaxis()  # NMR convention: decreasing ppm
    ax.set_title(title)
    ax.grid(True, linestyle='--', alpha=0.5)
    
    st.pyplot(fig)



# ==========================
# STREAMLIT UI
# ==========================
st.title("🧪 NMR Peak Extractor + HMDB Comparator")

# Experiment metadata (optional)
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
            plot_spectrum(lactate_df, title=f"{search_name} Spectrum")
    else:
        st.warning(f"No metabolite found with the name '{search_name}'.")
elif search_name:
    st.warning("⚠️ No local HMDB file found. Add `hmdb_reference.csv` to the app folder.")
