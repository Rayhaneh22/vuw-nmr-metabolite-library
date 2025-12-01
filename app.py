import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ==========================
# LOAD HMDB REFERENCE TABLE
# ==========================
@st.cache_data
def load_hmdb(csv_path: str = "hmdb_reference.csv") -> pd.DataFrame | None:
    """Load HMDB reference table as a DataFrame."""
    try:
        df = pd.read_csv(csv_path)
        return df
    except FileNotFoundError:
        return None

hmdb_df = load_hmdb()

# ==========================
# FUNCTIONS
# ==========================
def plot_spectrum(sample_df: pd.DataFrame, title="Spectrum") -> None:
    """Plot simple stem NMR spectrum from ppm and intensity columns."""
    if "intensity" not in sample_df.columns:
        sample_df["intensity"] = 1  # default for display if no intensity
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.stem(sample_df["ppm"], sample_df["intensity"], basefmt=" ", linefmt='C0-', markerfmt='C0o')
    ax.set_xlabel("ppm")
    ax.set_ylabel("Intensity")
    ax.invert_xaxis()  # NMR convention
    ax.set_title(title)
    st.pyplot(fig)

# ==========================
# STREAMLIT UI
# ==========================
st.title("🧪 NMR Peak Extractor + HMDB Comparator")

# -------------------------
# EXPERIMENT METADATA
# -------------------------
st.sidebar.header("NMR Experiment Metadata")
field_strength = st.sidebar.text_input("Magnetic Field Strength (MHz)", "600")
pulse_seq = st.sidebar.text_input("Pulse Sequence", "90°")
internal_std = st.sidebar.text_input("Internal Standard", "0.1 mM DSS")
num_scans = st.sidebar.number_input("Number of Scans (NS)", value=256)
st.sidebar.markdown("Add any other metadata in your CSV if needed.")

st.write(f"**Field Strength:** {field_strength} MHz")
st.write(f"**Pulse Sequence:** {pulse_seq}")
st.write(f"**Internal Standard:** {internal_std}")
st.write(f"**Number of Scans:** {num_scans}")

# -------------------------
# FILE UPLOAD
# -------------------------
uploaded_file = st.file_uploader("Upload your metabolite CSV", type=['csv'])
if uploaded_file:
    try:
        sample_df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Error reading CSV file: {e}")
    else:
        # Ensure required columns
        required_cols = ["ppm", "intensity"]
        if not all(col in sample_df.columns for col in required_cols):
            st.error(f"CSV must contain columns: {', '.join(required_cols)}")
        else:
            st.subheader("📌 Uploaded Sample Peaks")
            st.dataframe(sample_df)

            # -------------------------
            # METABOLITE SEARCH
            # -------------------------
            st.sidebar.header("Search Metabolites")
            search_name = st.sidebar.text_input("Enter metabolite name")

            if search_name and hmdb_df is not None:
                matches = hmdb_df[hmdb_df['Name'].str.contains(search_name, case=False, na=False)]
                if not matches.empty:
                    st.subheader(f"Results for '{search_name}'")
                    for idx, row in matches.iterrows():
                        st.markdown(f"### {row['Name']} ({row['HMDB_ID']})")
                        st.write(f"CAS: {row.get('CAS','')}, Formula: {row.get('Formula','')}")
                        st.write(f"Predicted peaks: {row.get('predicted_ppm','')}")
                        st.markdown(f"[View on HMDB](https://hmdb.ca/metabolites/{row['HMDB_ID']})")
                        st.image(f"https://hmdb.ca/metabolites/{row['HMDB_ID']}.png", width=200)

                    # Plot the spectrum from uploaded CSV
                    st.subheader(f"📊 Spectrum for '{search_name}'")
                    plot_spectrum(sample_df, title=f"{search_name} Spectrum")
                else:
                    st.warning(f"No metabolite found with the name '{search_name}'.")
            elif search_name:
                st.warning("⚠️ No local HMDB file found. Add `hmdb_reference.csv` to the app folder.")
