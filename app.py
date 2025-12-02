import streamlit as st
import pandas as pd
import plotly.graph_objects as go
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
        if not all(col in df.columns for col in ["ppm", "intensity"]):
            st.error("Lactate CSV must contain 'ppm' and 'intensity' columns.")
            return None
        return df
    except FileNotFoundError:
        st.error(f"Lactate CSV not found in '{csv_path}'.")
        return None

lactate_df = load_lactate()

# ==========================
# LOAD CREATINE CSV
# ==========================
@st.cache_data
def load_creatine(csv_path="Data/creatine.csv") -> pd.DataFrame | None:
    try:
        df = pd.read_csv(csv_path)
        if not all(col in df.columns for col in ["ppm", "intensity"]):
            st.error("creatine CSV must contain 'ppm' and 'intensity' columns.")
            return None
        return df
    except FileNotFoundError:
        st.error(f"creatine CSV not found in '{csv_path}'.")
        return None

creatine_df = load_creatine()

# ==========================
# PLOT FUNCTION WITH PLOTLY (INTERACTIVE)
# ==========================
def plot_spectrum_interactive(sample_df: pd.DataFrame, title="Spectrum"):
    sample_df = sample_df.sort_values("ppm", ascending=False)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=sample_df["ppm"],
            y=sample_df["intensity"],
            mode='lines',
            line=dict(color='blue', width=2),
            name='Intensity'
        )
    )
    fig.update_layout(
        title=title,
        xaxis=dict(title='ppm', autorange='reversed'),
        yaxis=dict(title='Intensity'),
        hovermode='x unified',
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

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
water_supp = st.sidebar.text_input("Water Suppression Method", "WATERGATE")
solvent = st.sidebar.text_input("Solvent", "D2O")
sample_pH = st.sidebar.text_input("Sample pH", "")
buffer_used = st.sidebar.text_input("Buffer", "")
relax_delay = st.sidebar.text_input("Relaxation Delay (s)", "2.0")

# -------------------------
# Display Experiment Metadata in a tidy line format
# -------------------------
st.markdown("### 🧪 Experiment Metadata")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"**Field Strength:** {field_strength} MHz")
    st.markdown(f"**Pulse Sequence:** {pulse_seq}")
    st.markdown(f"**Internal Standard:** {internal_std}")
with col2:
    st.markdown(f"**Number of Scans:** {num_scans}")
    st.markdown(f"**Water Suppression:** {water_supp}")
    st.markdown(f"**Solvent:** {solvent}")
with col3:
    st.markdown(f"**pH:** {sample_pH}")
    st.markdown(f"**Buffer:** {buffer_used}")
    st.markdown(f"**Relaxation Delay:** {relax_delay} s")
# Add a horizontal line separator
st.markdown("---")

# -------------------------
# Metabolite search
# -------------------------
st.sidebar.header("Search Metabolites")
search_name = st.sidebar.text_input("Enter metabolite name").lower()
# ==========================
# ==========================
# ==========================
# Display Lactate
# ==========================
if search_name == "lactate" and lactate_df is not None:
    col1, col2 = st.columns([2, 1])  # left larger for spectrum, right smaller for image
    # Spectrum
    with col1:
        plot_spectrum_interactive(lactate_df, title="Lactate Spectrum")
    # Formula image
    with col2:
        img_path = "Data/Lactic_acid.png"
        if os.path.exists(img_path):
            st.image(img_path, caption="Lactic Acid (C3H6O3)", use_column_width=True)
        else:
            st.warning(f"⚠️ Formula image not found at '{img_path}'")
    st.markdown("""
    🔗 **NMR Prediction:**  
    https://www.nmrdb.org/new_predictor/index.shtml?v=v2.173.0
    """)
    st.markdown("""
    🔗 **HMDB:**  
    https://hmdb.ca/metabolites/HMDB0000190
    """)

# ==========================
# Display Creatine
# ==========================
if search_name == "creatine" and creatine_df is not None:
    col1, col2 = st.columns([2, 1])  # spectrum left, image right
    # Spectrum
    with col1:
        plot_spectrum_interactive(creatine_df, title="Creatine Spectrum")
    # Formula image
    with col2:
        img_path = "Data/creatine.jpg"
        if os.path.exists(img_path):
            st.image(img_path, caption="Creatine (C4H9N3O2)", use_column_width=True)
        else:
            st.warning(f"⚠️ Formula image not found at '{img_path}'")
    st.markdown("""
    🔗 **NMR Prediction:**  
    https://www.nmrdb.org/new_predictor/index.shtml?v=v2.173.0
    """)
    st.markdown("""
    🔗 **HMDB 1D NMR Spectrum:**  
    https://hmdb.ca/spectra/nmr_one_d/1064
    """)
