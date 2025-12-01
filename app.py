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

# -------------------------
# Metabolite search box
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
    else:
        st.warning("No metabolite found with this name.")

# ==========================
# FUNCTIONS
# ==========================
def estimate_j_coupling(ppm_list: list[float]) -> list[float]:
    """Crude J-coupling estimator (placeholder)."""
    return [np.nan for _ in ppm_list]

def match_to_hmdb(sample_df: pd.DataFrame, hmdb_df: pd.DataFrame, tol: float = 0.02) -> pd.DataFrame:
    """Match sample metabolite peak list to HMDB based on ppm proximity."""
    results = []
    sample_peaks = sample_df["ppm"].values

    for _, row in hmdb_df.iterrows():
        hmdb_peaks = [float(x) for x in str(row["ppm_list"]).split(";")]
        matches = sum(any(abs(sp - hp) <= tol for hp in hmdb_peaks) for sp in sample_peaks)
        score = matches / len(hmdb_peaks) if hmdb_peaks else 0
        results.append({
            "Metabolite": row["Name"],
            "HMDB_ID": row["HMDB_ID"],
            "CAS": row.get("CAS", ""),
            "Formula": row.get("Formula", ""),
            "Match score": round(score, 3),
            "HMDB peaks": row["ppm_list"],
            "Predicted peaks": row.get("predicted_ppm", ""),
            "Structure": f"https://hmdb.ca/metabolites/{row['HMDB_ID']}.png",
            "Link": f"https://hmdb.ca/metabolites/{row['HMDB_ID']}"
        })
    
    results_df = pd.DataFrame(results)
    return results_df.sort_values("Match score", ascending=False).reset_index(drop=True)

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
        # Detect ppm column
        possible_ppm_cols = ["ppm", "Shift", "Chemical Shift"]
        ppm_col = next((c for c in sample_df.columns if c in possible_ppm_cols), None)
        if ppm_col is None:
            st.error("Uploaded CSV is missing required column: 'ppm' or equivalent ('Shift', 'Chemical Shift').")
        else:
            sample_df.rename(columns={ppm_col: "ppm"}, inplace=True)
            st.subheader("📌 Sample Peaks")
            st.dataframe(sample_df)

            # Plot spectrum
            st.subheader("📊 Spectrum")
            plot_spectrum(sample_df)

            # Estimate J values
            st.subheader("📐 Estimated J-Couplings")
            J_vals = estimate_j_coupling(sample_df["ppm"].values)
            j_df = pd.DataFrame({"ppm": sample_df["ppm"], "estimated_J_Hz": J_vals})
            st.dataframe(j_df)

            # HMDB comparison
            if hmdb_df is not None:
                st.subheader("🔍 HMDB Comparison Results")
                ppm_tol = st.sidebar.slider("Peak matching tolerance (ppm)", 0.005, 0.05, 0.02)
                results_df = match_to_hmdb(sample_df, hmdb_df, tol=ppm_tol)

                # Display table with clickable HMDB link
                st.dataframe(results_df[["Metabolite", "HMDB_ID", "CAS", "Formula", "Match score", "HMDB peaks", "Predicted peaks"]])

                # Display structure images for top hits
                for idx, row in results_df.iterrows():
                    st.markdown(f"### {row['Metabolite']} ({row['HMDB_ID']})")
                    st.write(f"CAS: {row['CAS']}, Formula: {row['Formula']}")
                    st.write(f"Match score: {row['Match score']}")
                    st.write(f"HMDB peaks: {row['HMDB peaks']}")
                    st.write(f"Predicted peaks: {row['Predicted peaks']}")
                    st.markdown(f"[View on HMDB]({row['Link']})", unsafe_allow_html=True)
                    st.image(row['Structure'], width=200)
            else:
                st.warning("⚠️ No local HMDB file found. Add `hmdb_reference.csv` to the app folder.")
