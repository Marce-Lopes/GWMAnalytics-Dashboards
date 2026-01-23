
import streamlit as st
import pandas as pd
from utils import format_number, get_base64_image
from charts import render_comparison_chart
from styles import get_login_styles

def create_html_table(headers, rows, max_height=None, show_header=True, highlight_indices=None):
    """
    Helper function to create a consistent HTML table with grid styling.
    headers: list of column names
    rows: list of lists/tuples containing cell values
    max_height: optional string (e.g., '300px') to enable vertical scrolling
    show_header: boolean, whether to display the table header
    highlight_indices: list of row indices (0-based) to highlight in yellow
    """
    scroll_style = f"max-height: {max_height}; overflow-y: auto;" if max_height else "overflow: hidden;"
    if highlight_indices is None:
        highlight_indices = []
    
    html = f"""
<div style="width: 100%; {scroll_style} border: 1px solid #E2E8F0; border-top: none; border-radius: 0 0 8px 8px; background: #FFFFFF;">
    <table style="width:100%; border-collapse: collapse; border-spacing: 0; font-family: 'Montserrat', sans-serif;">
"""
    if show_header:
        html += """      <thead style="position: sticky; top: 0; background-color: #000000; z-index: 1;">
        <tr>
"""
        for i, header in enumerate(headers):
            # Assume last column is numeric/right-aligned, others left-aligned
            align = "right" if i == len(headers) - 1 else "left"
            html += f'          <th style="text-align: {align}; color: #FFFFFF; background-color: #000000; padding: 8px; font-weight: bold; text-transform: uppercase; font-size: 0.8rem;">{header}</th>\n'
        
        html += """        </tr>
      </thead>
"""
    
    html += """      <tbody>
"""
    
    for idx, row in enumerate(rows):
        bg_color = "#FFD700" if idx in highlight_indices else "#FFFFFF" # Yellow for highlight, White for normal
        html += f'        <tr style="background-color: {bg_color} !important;">\n'
        for i, val in enumerate(row):
            align = "right" if i == len(row) - 1 else "left"
            # Remove border-bottom for the last row to create a seamless card look
            border_style = "border-bottom: 1px solid #F1F5F9;" if idx < len(rows) - 1 else ""
            html += f'          <td style="text-align: {align}; font-variant-numeric: tabular-nums; {border_style} padding: 8px; color: #000000; font-size: 13px;">{val}</td>\n'
        html += '        </tr>\n'
        
    html += """      </tbody>
    </table>
</div>
"""
    return html


def render_summary_html(model_name, summary_data):
    """Render summary table for a model using HTML to avoid scrollbars"""
    # Handle case sensitivity and missing keys
    if model_name in summary_data:
        data = summary_data[model_name]
    else:
        # Try to find a case-insensitive match
        match = next((k for k in summary_data.keys() if k.lower() == model_name.lower()), None)
        if match:
            data = summary_data[match]
        else:
            # Default data if model not found
            data = {
                'ok_form_without_payment': 0,
                'ok_form_with_payment': 0,
                '9k_last_24_hours': 0
            }
            
    values = [
        format_number(data.get('ok_form_without_payment', 0)),
        format_number(data.get('ok_form_with_payment', 0)),
        format_number(data.get('9k_last_24_hours', 0))
    ]
    
    metrics = [
        '9k form without payment',
        '9k form with payment',
        '9k last 24 hours'
    ]
    
    # Create rows for helper function
    rows = list(zip(metrics, values))
    # Highlight rows 1 and 2 (0-based) which correspond to '9k form with payment' and '9k last 24 hours'
    return create_html_table(['Metric', 'Value'], rows, show_header=False, highlight_indices=[1, 2])


def render_color_table(model_name, color_data):
    """Render by color table for a model"""
    # Handle case sensitivity and missing keys
    if model_name in color_data:
        data = color_data[model_name]
    else:
        # Try to find a case-insensitive match
        match = next((k for k in color_data.keys() if k.lower() == model_name.lower()), None)
        if match:
            data = color_data[match]
        else:
            # Default data
            data = {'No Data': 0}

    df = pd.DataFrame({
        'Color': list(data.keys()),
        'Total': list(data.values())
    })
    df = df.sort_values('Total', ascending=False)
    # Apply number formatting after sorting
    df['Total'] = df['Total'].apply(format_number)
    
    # Convert to HTML
    rows = []
    for _, row in df.iterrows():
        rows.append([row['Color'], row['Total']])
        
    return create_html_table(['Color', 'Total'], rows, show_header=False)


def render_dealer_group_table(model_name, dealer_data):
    """Render dealer group table for a model using real data"""
    # Handle case sensitivity and missing keys
    if model_name in dealer_data:
        data = dealer_data[model_name]
    else:
        # Try to find a case-insensitive match
        match = next((k for k in dealer_data.keys() if k.lower() == model_name.lower()), None)
        if match:
            data = dealer_data[match]
        else:
            # Default data
            data = {'No Data': 0}

    df = pd.DataFrame({
        'Dealer Group': list(data.keys()),
        'Total': list(data.values())
    })
    df = df.sort_values('Total', ascending=False)
    # Filter out zeros for cleaner display
    df = df[df['Total'] > 0]
    # Apply number formatting after sorting and filtering
    df['Total'] = df['Total'].apply(format_number)
    
    # Convert to HTML
    rows = []
    for _, row in df.iterrows():
        rows.append([row['Dealer Group'], row['Total']])
        
    # Enable scrolling if many rows (e.g. > 15 items approx 400-500px)
    # Using 400px as a reasonable max height for top 15-ish
    return create_html_table(['Dealer Group', 'Total'], rows, max_height='400px', show_header=False)


def render_model_header_and_summary(model_name, summary_data):
    """Render header and summary table for one model"""
    # Summary Table HTML
    summary_html = render_summary_html(model_name, summary_data)
    
    # Combine into a single HTML block to avoid Streamlit container fragmentation
    # IMPORTANT: Keep HTML flush left to avoid Markdown code block interpretation
    full_html = f"""<div class="summary-card" style="display: flex; flex-direction: column;">
<div class="model-header">{model_name}</div>
{summary_html}
</div>"""
    st.markdown(full_html, unsafe_allow_html=True)


def show_login_page():
    """Display login page"""
    st.markdown(get_login_styles(), unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Load and display image for login
        img_path = "analytics.png"
        img_base64 = get_base64_image(img_path)
        
        # Display Logo
        if img_base64:
            st.markdown(f"""
                <div style='text-align: center; margin-bottom: 2rem;'>
                    <img src='data:image/png;base64,{img_base64}' style='height: 80px; object-fit: contain;'>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("<h3 style='text-align: center; margin-bottom: 2rem;'>🚗 GWM Dashboard</h3>", unsafe_allow_html=True)
        
        # Inputs
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            login_button = st.button("Login", type="primary", use_container_width=True)
        
        if login_button:
            # Authorized users
            AUTHORIZED_USERS = {
                "andre.lembo@gwmmotors.com.br": "+c4ui&5vpHq1]0\\N1$18",
                "felipe.bellini@gwmmotors.com.br": "vJ15E6Lh/10ZkcXu8pnh",
                "admin@gwmmotors.com.br": "1Q5rwi{#tZLvfR8#Bf2u"
            }
            
            if username in AUTHORIZED_USERS and AUTHORIZED_USERS[username] == password:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid username or password")


def render_kpi_section(kpi_data):
        """Render the KPI section with Total, MoM, YoY, Share, Paid, Unpaid, Adjusted"""
        if not kpi_data:
            return

        total = kpi_data['total']
        prev_total = kpi_data['prev_total']
        ly_total = kpi_data['ly_total']
        market_total = kpi_data['market_total']
        
        # New Metrics
        paid_curr = kpi_data.get('paid_curr', 0)
        paid_prev = kpi_data.get('paid_prev', 0)
        unpaid_curr = kpi_data.get('unpaid_curr', 0)
        unpaid_prev = kpi_data.get('unpaid_prev', 0)
        weekday_data = kpi_data.get('weekday_data')

        # Calculations
        mom = ((total - prev_total) / prev_total * 100) if prev_total > 0 else 0
        yoy = ((total - ly_total) / ly_total * 100) if ly_total > 0 else 0
        share = (total / market_total * 100) if market_total > 0 else 0
        
        paid_mom = ((paid_curr - paid_prev) / paid_prev * 100) if paid_prev > 0 else 0
        unpaid_mom = ((unpaid_curr - unpaid_prev) / unpaid_prev * 100) if unpaid_prev > 0 else 0

        # Helper for arrow
        def get_arrow(val):
            if val > 0: return "↑", "#34D399" # Emerald-400 (Bright Green)
            if val < 0: return "↓", "#F87171" # Red-400 (Bright Red)
            return "-", "#94A3B8" # Slate-400 (Light Grey)

        # Helper for inverse arrow (Growth is Bad, Decline is Good)
        def get_inverse_arrow(val):
            if val > 0: return "↑", "#F87171" # Red (Bad)
            if val < 0: return "↓", "#34D399" # Green (Good)
            return "-", "#94A3B8" # Slate

        mom_arrow, mom_color = get_arrow(mom)
        yoy_arrow, yoy_color = get_arrow(yoy)
        paid_arrow, paid_color = get_arrow(paid_mom)
        unpaid_arrow, unpaid_color = get_inverse_arrow(unpaid_mom)
        
        # Weekday HTML
        weekday_html = ""
        if weekday_data:
            t_val = int(weekday_data['today_val'])
            a_val = int(weekday_data['adj_val'])
            
            # Simple diff indicator
            diff = t_val - a_val
            diff_color = "#10B981" if diff > 0 else "#EF4444" if diff < 0 else "#94A3B8"
            
            # Using single line to avoid code block rendering
            weekday_html = f"""<div style="text-align: center;"><div style="font-size: 0.85rem; color: #94A3B8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">Today vs Adjusted</div><div style="font-size: 1.5rem; font-weight: 600; color: #FFFFFF; font-family: 'Montserrat', sans-serif;">{t_val} <span style="font-size: 0.9rem; color: {diff_color}; font-weight: 500;">(vs {a_val})</span></div></div>"""

        st.markdown(f"""
<div style="background-color: #1E293B; border-radius: 8px; padding: 1rem 2rem; margin: 2rem 0; border: 1px solid #334155; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2); overflow-x: auto;">
    <div style="display: flex; justify-content: space-between; align-items: center; width: 100%; min-width: max-content;">
        <div style="text-align: center;">
            <div style="font-size: 0.85rem; color: #94A3B8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">Total</div>
            <div style="font-size: 2rem; font-weight: 700; color: #FFFFFF; font-family: 'Montserrat', sans-serif;">{int(total):,}</div>
        </div>
        <div style="text-align: center;">
            <div style="font-size: 0.85rem; color: #94A3B8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">% Vs Last Month</div>
            <div style="font-size: 1.5rem; font-weight: 600; color: {mom_color}; font-family: 'Montserrat', sans-serif;">{mom_arrow} {abs(mom):.1f}%</div>
        </div>
        <div style="text-align: center;">
            <div style="font-size: 0.85rem; color: #94A3B8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">% Vs Last Year</div>
            <div style="font-size: 1.5rem; font-weight: 600; color: {yoy_color}; font-family: 'Montserrat', sans-serif;">{yoy_arrow} {abs(yoy):.1f}%</div>
        </div>
        <div style="text-align: center;">
            <div style="font-size: 0.85rem; color: #94A3B8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">% Share</div>
            <div style="font-size: 1.5rem; font-weight: 600; color: #3B82F6; font-family: 'Montserrat', sans-serif;">{share:.1f}%</div>
        </div>
        <div style="width: 1px; height: 40px; background-color: #334155;"></div>
        <div style="text-align: center;">
            <div style="font-size: 0.85rem; color: #94A3B8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">9K Paid</div>
            <div style="font-size: 1.5rem; font-weight: 600; color: {paid_color}; font-family: 'Montserrat', sans-serif;">{paid_arrow} {abs(paid_mom):.1f}%</div>
        </div>
        <div style="text-align: center;">
            <div style="font-size: 0.85rem; color: #94A3B8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">9K Unpaid</div>
            <div style="font-size: 1.5rem; font-weight: 600; color: {unpaid_color}; font-family: 'Montserrat', sans-serif;">{unpaid_arrow} {abs(unpaid_mom):.1f}%</div>
        </div>
        {weekday_html}
    </div>
</div>
""", unsafe_allow_html=True)


def render_comparison_section(raw_vehicle, month_options, models):
    """Render the Comparison Chart section"""
    st.markdown("""
        <div style="
            padding: 0.5rem 1rem; 
            margin-bottom: 1rem; 
        ">
            <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 0.5rem;">
                <h3 style="
                    color: #09124F !important; 
                    margin: 0 !important; 
                    font-family: 'Montserrat', sans-serif;
                    font-weight: 600;
                    font-size: 1.4rem;
                    line-height: 1.2 !important;
                    letter-spacing: 1px;
                    padding: 0 !important;
                ">Comparison Analysis</h3>
            </div>
            <div style="
                width: 100%;
                height: 4px;
                background-color: #000000;
                border-radius: 2px;
            "></div>
        </div>
    """, unsafe_allow_html=True)
    
    # --- Filters Row 1 ---
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Month A - Default to current month (or first in list)
        month_a = st.selectbox("Month A", month_options, index=0, key="comp_month_a")
        
    with col2:
        # Month B - Default to previous month (or second in list)
        default_idx_b = 1 if len(month_options) > 1 else 0
        month_b = st.selectbox("Month B", month_options, index=default_idx_b, key="comp_month_b")
        
    with col3:
        # Vehicle Family
        # If 'models' is passed, use it. Add 'All' option.
        family_options = ['All'] + models
        family_name = st.selectbox("Vehicle Family", family_options, index=0, key="comp_family")
        
    with col4:
        # 9k Status
        status_options = ['9k form without payment', '9k form with payment', 'Total']
        status_filter = st.selectbox("9k Status", status_options, index=2, key="comp_status") # Default Total
        
    # --- Mode Selection Row 2 ---
    # Centered buttons using columns
    c1, c2, c3 = st.columns([2, 1, 2])
    with c2:
        # Using a radio button designed as pills/buttons if possible, or just radio
        # Streamlit's radio is horizontal
        mode = st.radio("Comparison Mode", ['Normalized', 'MoM'], horizontal=True, label_visibility="collapsed", key="comp_mode")
        
    # --- Chart Row 3 ---
    render_comparison_chart(raw_vehicle, month_a, month_b, family_name, status_filter, mode)