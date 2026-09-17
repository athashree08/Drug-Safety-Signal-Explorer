import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Drug Safety Signal Explorer",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- STYLING ---
st.markdown("""
<style>
    /* Typography */
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif !important;
        color: #222222;
    }
    
    /* Backgrounds */
    .stApp, .stApp > header {
        background-color: #F7F3F0 !important;
    }
    
    /* Headers */
    h1 {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        color: #222222 !important;
        border-bottom: 1px solid #D8D1D0 !important;
        padding-bottom: 10px !important;
        margin-bottom: 10px !important;
    }
    
    .section-title {
        font-size: 20px !important;
        font-weight: 700 !important;
        color: #222222 !important;
        margin-top: 0 !important;
        margin-bottom: 15px !important;
    }

    /* Cards */
    .kpi-card {
        background-color: #FFFFFF;
        border: 1px solid #D8D1D0;
        padding: 15px;
        margin-bottom: 15px;
    }
    .kpi-value {
        font-size: 2.5rem;
        color: #527EAD !important;
        margin: 0;
        line-height: 1.1;
        font-weight: 600;
    }
    .kpi-label {
        font-size: 0.85rem;
        color: #222222 !important;
        margin: 0;
        text-transform: uppercase;
        font-weight: 700;
    }
    
    /* Panels */
    .pink-panel {
        background-color: #F3E6E8;
        padding: 20px;
        border: 1px solid #D8D1D0;
        border-radius: 4px;
        margin-bottom: 20px;
    }
    
    /* Hide Streamlit Clutter */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# --- DATA LOADING ---
@st.cache_data
def load_data():
    df = pd.read_csv('drug_safety_signals.csv')
    return df

df = load_data()

# --- HEADER ---
st.title("DRUG SAFETY SIGNAL EXPLORER")
st.markdown("<p style='color: #444444; font-size: 1.1rem; margin-top: 0; margin-bottom: 25px;'>Explore disproportionate reporting patterns in openFDA adverse-event data</p>", unsafe_allow_html=True)

# --- CONTROLS ---
# Dropdown lists
all_drugs = ["All Drugs"] + sorted(df['drug'].unique().tolist())
all_reactions = ["All Reactions"] + sorted(df['reaction'].unique().tolist())

c1, c2, c3, c4 = st.columns(4)
with c1:
    drug_selection = st.selectbox("Drug", options=all_drugs, index=0)
with c2:
    reaction_selection = st.selectbox("Reaction", options=all_reactions, index=0)
with c3:
    min_reports = st.slider("Minimum Report Count", min_value=3, max_value=int(df['report_count'].max()), value=3)
with c4:
    min_ror = st.slider("Minimum ROR", min_value=1.0, max_value=float(df['ROR'].max()), value=1.0)

# --- FILTERING ---
filtered_df = df.copy()

if drug_selection != "All Drugs":
    filtered_df = filtered_df[filtered_df['drug'] == drug_selection]
    
if reaction_selection != "All Reactions":
    filtered_df = filtered_df[filtered_df['reaction'] == reaction_selection]

filtered_df = filtered_df[(filtered_df['report_count'] >= min_reports) & (filtered_df['ROR'] >= min_ror)]

# Calculate KPIs
total_reports_analyzed = 10000 # Hardcoded as per instructions
unique_drugs = filtered_df['drug'].nunique()
unique_reactions = filtered_df['reaction'].nunique()

# Potential Signals: ROR > 1 AND CI_lower >= 1 (to account for rounding to 1.0 in CSV export) AND report_count >= 3
potential_signals_count = len(filtered_df[(filtered_df['ROR'] > 1) & (filtered_df['CI_lower'] >= 1) & (filtered_df['report_count'] >= 3)])

# --- KPIs ---
st.write("") # small spacing
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.markdown(f"<div class='kpi-card'><p class='kpi-label'>REPORTS ANALYZED</p><p class='kpi-value'>{total_reports_analyzed:,}</p></div>", unsafe_allow_html=True)
with kpi2:
    st.markdown(f"<div class='kpi-card'><p class='kpi-label'>DRUGS IN SIGNAL DATA</p><p class='kpi-value'>{unique_drugs:,}</p></div>", unsafe_allow_html=True)
with kpi3:
    st.markdown(f"<div class='kpi-card'><p class='kpi-label'>REACTIONS IN SIGNAL DATA</p><p class='kpi-value'>{unique_reactions:,}</p></div>", unsafe_allow_html=True)
with kpi4:
    st.markdown(f"<div class='kpi-card'><p class='kpi-label'>POTENTIAL SIGNAL PAIRS</p><p class='kpi-value'>{potential_signals_count:,}</p></div>", unsafe_allow_html=True)

# --- CHARTS ROW 1 ---
st.write("") # small spacing
col1, col2 = st.columns(2)

chart_color = '#527EAD'
layout_updates = {
    'plot_bgcolor': 'rgba(0,0,0,0)',
    'paper_bgcolor': 'rgba(0,0,0,0)',
    'margin': dict(l=10, r=20, t=10, b=10),
    'font': dict(color='#222222', family='Inter, sans-serif', size=12)
}

with col1:
    st.markdown("<div class='pink-panel'>", unsafe_allow_html=True)
    st.markdown("<p class='section-title'>TOP DISPROPORTIONAL-REPORTING SIGNALS</p>", unsafe_allow_html=True)
    top_ror = filtered_df.nlargest(10, 'ROR').sort_values('ROR', ascending=True)
    if not top_ror.empty:
        # truncate for y-axis visually, keep full in hover
        top_ror['label'] = top_ror['drug_reaction'].apply(lambda x: x if len(x) <= 35 else x[:32] + '...')
        fig_ror = px.bar(top_ror, x='ROR', y='label', orientation='h', hover_data={'drug_reaction': True, 'label': False})
        fig_ror.update_traces(marker_color=chart_color, hovertemplate="<b>%{customdata[0]}</b><br>ROR: %{x:.2f}<extra></extra>")
        fig_ror.update_layout(**layout_updates)
        fig_ror.update_yaxes(title="")
        st.plotly_chart(fig_ror, use_container_width=True, config={'displayModeBar': False})
    else:
        st.info("No records match criteria.")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='pink-panel'>", unsafe_allow_html=True)
    st.markdown("<p class='section-title'>TOP REPORTED DRUG-REACTION PAIRS</p>", unsafe_allow_html=True)
    top_counts = filtered_df.nlargest(10, 'report_count').sort_values('report_count', ascending=True)
    if not top_counts.empty:
        top_counts['label'] = top_counts['drug_reaction'].apply(lambda x: x if len(x) <= 35 else x[:32] + '...')
        fig_counts = px.bar(top_counts, x='report_count', y='label', orientation='h', hover_data={'drug_reaction': True, 'label': False})
        fig_counts.update_traces(marker_color=chart_color, hovertemplate="<b>%{customdata[0]}</b><br>Count: %{x}<extra></extra>")
        fig_counts.update_layout(**layout_updates)
        fig_counts.update_yaxes(title="")
        fig_counts.update_xaxes(title="Report Count")
        st.plotly_chart(fig_counts, use_container_width=True, config={'displayModeBar': False})
    else:
        st.info("No records match criteria.")
    st.markdown("</div>", unsafe_allow_html=True)


# --- CHART ROW 2 (SCATTER) ---
st.markdown("<div class='pink-panel'>", unsafe_allow_html=True)
st.markdown("<p class='section-title'>REPORT COUNT VS ROR</p>", unsafe_allow_html=True)
if not filtered_df.empty:
    fig_scatter = px.scatter(
        filtered_df, 
        x='report_count', 
        y='ROR',
        hover_data=['drug', 'reaction', 'CI_lower', 'CI_upper'],
        log_y=True
    )
    fig_scatter.update_traces(marker=dict(color=chart_color, opacity=0.7, size=8, line=dict(width=1, color='#3F6289')),
                              hovertemplate="<b>%{customdata[0]}</b> + <b>%{customdata[1]}</b><br>Report Count: %{x}<br>ROR: %{y:.2f}<br>95% CI: [%{customdata[2]:.2f}, %{customdata[3]:.2f}]<extra></extra>")
    fig_scatter.update_layout(**layout_updates)
    fig_scatter.update_layout(margin=dict(l=10, r=20, t=10, b=40))
    fig_scatter.update_xaxes(title="Report Count", gridcolor='#D8D1D0')
    fig_scatter.update_yaxes(title="ROR (Log Scale)", gridcolor='#D8D1D0')
    st.plotly_chart(fig_scatter, use_container_width=True, config={'displayModeBar': False})
else:
    st.info("No records match criteria.")
st.markdown("</div>", unsafe_allow_html=True)

# --- ROW 3: TABLE & DETAIL ---
col_table, col_detail = st.columns([2, 1])

with col_table:
    st.markdown("<p class='section-title' style='margin-bottom: 5px !important;'>SIGNAL EXPLORER TABLE</p>", unsafe_allow_html=True)
    display_cols = ['drug', 'reaction', 'report_count', 'ROR', 'CI_lower', 'CI_upper']
    display_df = filtered_df[display_cols].copy()
    
    st.dataframe(
        display_df,
        column_config={
            "drug": "Drug",
            "reaction": "Reaction",
            "report_count": st.column_config.NumberColumn("Report Count", format="%d"),
            "ROR": st.column_config.NumberColumn("ROR", format="%.2f"),
            "CI_lower": st.column_config.NumberColumn("CI Lower", format="%.2f"),
            "CI_upper": st.column_config.NumberColumn("CI Upper", format="%.2f"),
        },
        hide_index=True,
        use_container_width=True,
        height=350
    )

with col_detail:
    st.markdown("<p class='section-title' style='margin-bottom: 5px !important;'>SIGNAL DETAIL</p>", unsafe_allow_html=True)
    if not display_df.empty:
        # Create a selectbox for picking the signal detail
        pair_options = ["Select a drug-reaction pair"] + filtered_df['drug_reaction'].tolist()
        selected_pair = st.selectbox("Select a pair to view details", options=pair_options, label_visibility="collapsed")
        
        if selected_pair != "Select a drug-reaction pair":
            selected_record = filtered_df[filtered_df['drug_reaction'] == selected_pair].iloc[0]
            
            st.markdown(f"""<div class='kpi-card'>
<h4 style='color: #3F6289; margin-top: 0; font-size: 1.1rem; border-bottom: none;'>{selected_record['drug']}</h4>
<p style='color: #222222; font-weight: 600; margin-bottom: 15px;'>{selected_record['reaction']}</p>
<p style='color: #444444; margin-bottom: 5px;'>Report Count: <span style='color: #222; font-weight: 600;'>{int(selected_record['report_count'])}</span></p>
<p style='color: #444444; margin-bottom: 5px;'>ROR: <span style='color: #222; font-weight: 600;'>{selected_record['ROR']:.2f}</span></p>
<p style='color: #444444; margin-bottom: 15px;'>95% CI: <span style='color: #222; font-weight: 600;'>[{selected_record['CI_lower']:.2f}, {selected_record['CI_upper']:.2f}]</span></p>
<hr style='border: 0; border-top: 1px solid #D8D1D0;'>
<p style='margin-bottom: 5px; font-weight: 700; color: #3F6289; font-size: 0.9rem;'>SIGNAL CRITERIA</p>
<ul style='margin-top: 0; padding-left: 20px; font-size: 0.9em; color: #222222;'>
<li>{'✓' if selected_record['ROR'] > 1 else '✗'} ROR > 1</li>
<li>{'✓' if selected_record['CI_lower'] >= 1 else '✗'} Lower 95% CI > 1</li>
<li>{'✓' if selected_record['report_count'] >= 3 else '✗'} ≥3 reports</li>
</ul>
</div>""", unsafe_allow_html=True)
        else:
            st.info("Please select a drug-reaction pair from the dropdown above to view signal details.")
    else:
        st.info("No selection available.")

# --- METHODOLOGY / FOOTER ---
st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
<div style='background-color: #F3E6E8; padding: 25px; border-top: 1px solid #D8D1D0; border-bottom: 1px solid #D8D1D0;'>
    <p style='margin: 0; color: #222222; font-size: 1rem;'><strong>Methodology:</strong> Potential signals are defined as ROR > 1, lower 95% CI > 1, and ≥3 reports. Results indicate disproportionate reporting within the analyzed sample and do not establish causality.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style='padding: 25px 0;'>
    <p class='section-title' style='color: #3F6289 !important;'>WHAT THIS DOES NOT PROVE</p>
    <p style='font-size: 0.95em; color: #444444; max-width: 900px; line-height: 1.5;'>
    This project identifies drug-reaction pairs with disproportionate reporting within the analyzed openFDA sample. A potential signal does not establish that a drug caused a reaction.<br><br>
    Adverse-event reports are voluntary and can be affected by reporting bias, drug popularity, media attention, and other factors. The results should therefore be treated as signals for further human review, not as evidence of causality or medical recommendations.
    </p>
</div>
""", unsafe_allow_html=True)
