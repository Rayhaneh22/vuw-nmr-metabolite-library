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

st.write(f"**Field Strength:** {field_strength} MHz")
st.write(f"**Pulse Sequence:** {pulse_seq}")
st.write(f"**Internal Standard:** {internal_std}")
st.write(f"**Number of Scans:** {num_scans}")
st.write(f"**Water Suppression:** {water_supp}")
st.write(f"**Solvent:** {solvent}")
st.write(f"**pH:** {sample_pH}")
st.write(f"**Buffer:** {buffer_used}")
st.write(f"**Relaxation Delay:** {relax_delay} s")

# -------------------------
# Metabolite search
# -------------------------
st.sidebar.header("Search Metabolites")
search_name = st.sidebar.text_input("Enter metabolite name").lower()
# ==========================
# Display Lactate
# ==========================
if search_name == "lactate" and lactate_df is not None:
    with st.container():
        col1, col2 = st.columns([1, 2])
        # Formula image
        with col1:
            img_path = "Data/Lactic_acid.png"
            if os.path.exists(img_path):
                st.image(img_path, caption="Lactic Acid (C3H6O3)", use_column_width=True)
            else:
                st.warning(f"⚠️ Formula image not found at '{img_path}'")
        # Spectrum
        with col2:
            plot_spectrum_interactive(lactate_df, title="Lactate Spectrum")
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
    with st.container():
        col1, col2 = st.columns([1, 2])
        # Formula image
        with col1:
            img_path = "Data/creatine.jpg"
            if os.path.exists(img_path):
                st.image(img_path, caption="Creatine (C4H9N3O2)", use_column_width=True)
            else:
                st.warning(f"⚠️ Formula image not found at '{img_path}'")
        # Spectrum
        with col2:
            plot_spectrum_interactive(creatine_df, title="Creatine Spectrum")
    st.markdown("""
    🔗 **NMR Prediction:**  
    https://www.nmrdb.org/new_predictor/index.shtml?v=v2.173.0
    """)
    st.markdown("""
    🔗 **HMDB 1D NMR Spectrum:**  
    https://hmdb.ca/spectra/nmr_one_d/1064
    """)
