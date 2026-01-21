
"""
GWM Pocket Report Dashboard
Mobile-optimized Streamlit dashboard
"""
import streamlit as st
from PIL import Image
from datetime import datetime
from database import (
    get_vehicle_options, 
    get_month_options, 
    get_vehicle_families, 
    get_summary_data, 
    get_color_data,
    get_daily_data,
    get_state_data,
    get_dealer_group_data,
    get_last_updated_date
)
from utils import get_base64_image, format_number
from styles import get_main_styles, get_header_styles
from components import (
    show_login_page, 
    render_model_header_and_summary, 
    render_color_table, 
    render_dealer_group_table,
    render_comparison_section
)
from charts import (
    render_daily_chart,
    render_state_map
)

# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None

# Load page icon
try:
    # Try local absolute path first (dev mode)
    import os
    if os.path.exists("analytics.png"):
        icon_path = "analytics.png"
    else:
        # Fallback for dev environment with specific path
        icon_path = r"C:\Users\61000453\Documents\rio_pmo_project\retencao\analytics.png"
    
    page_icon = Image.open(icon_path)
except Exception:
    page_icon = "🚗"

# Page configuration for mobile optimization
st.set_page_config(
    page_title="GWM Pocket Report",
    page_icon=page_icon,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply Main Styles
st.markdown(get_main_styles(), unsafe_allow_html=True)

# Add viewport meta tag for better mobile rendering
st.markdown("""
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
""", unsafe_allow_html=True)


def main():
    """Main dashboard function"""
    # Check authentication
    if not st.session_state.authenticated:
        show_login_page()
        return
    
    # Combined Header with Logout - REDUCED SPACING
    st.markdown(get_header_styles(), unsafe_allow_html=True)

    # Use columns: [Spacer, Title, Logout]
    # Ratios ensure Title is centered and Logout is on the right
    col_left, col_center, col_right = st.columns([1, 6, 1])
    
    with col_center:
        # Load and display image
        import os
        if os.path.exists("analytics.png"):
            img_path = "analytics.png"
        else:
            img_path = r"C:\Users\61000453\Documents\rio_pmo_project\retencao\analytics.png"
            
        img_base64 = get_base64_image(img_path)
        
        if img_base64:
            st.markdown(f"""
                <div style='text-align: center; margin-top: -10px; margin-bottom: 0px;'>
                    <img src='data:image/png;base64,{img_base64}' style='height: 85px; object-fit: contain;'>
                </div>
            """, unsafe_allow_html=True)
        else:
            # Fallback if image not found
            st.markdown("""
                <h3 style='text-align: center; margin-bottom: 0px; padding-bottom: 0px; margin-top: -5px;'>GWM</h3>
            """, unsafe_allow_html=True)
            
        # Display Last Updated Date
        last_updated = get_last_updated_date()
        if last_updated:
            # Format if it's a datetime object, but it likely comes as Timestamp or similar from ClickHouse
            # Usually str(last_updated) works, or .strftime if it's a datetime
            # ClickHouse connect returns datetime objects usually
            try:
                date_str = last_updated.strftime('%d/%m/%Y')
            except:
                date_str = str(last_updated).split(' ')[0] # Fallback
                
            st.markdown(f"""
                <div style='text-align: center; font-size: 10px; color: #64748B; margin-top: 2px; margin-bottom: 5px;'>
                    Data updated until: {date_str}
                </div>
            """, unsafe_allow_html=True)
        
    with col_right:
        if st.button("Logout", key="logout_btn"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.rerun()
    
    # Combined Filter Section - Single Row
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    
    # Fetch report options from database
    report_options = get_vehicle_options()
    
    # Use a single row with columns to place filters side by side
    # Layout: Spacer | Report Selector | Spacer | Month Selector | Spacer
    col_spacer_l, col_report, col_spacer_m, col_month, col_spacer_r = st.columns([1, 4, 0.5, 2, 1])
    
    with col_report:
        selected_report = st.selectbox(
            "",
            options=report_options,
            index=0,
            label_visibility="collapsed",
            key="report_selector"
        )
        
    # Fetch month options
    month_options = get_month_options()

    with col_month:
        selected_month_str = st.selectbox(
            "",
            options=month_options,
            index=0,
            label_visibility="collapsed",
            key="month_selector"
        )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Parse selected month string to get month and year
    try:
        # Format is Mon/YY (e.g. Jan/24)
        parsed_date = datetime.strptime(selected_month_str, '%b/%y')
        month = parsed_date.month
        year = parsed_date.year
    except Exception:
        # Fallback if parsing fails
        month = 1
        year = 2024
    
    # Mobile-responsive layout
    # On mobile: stack vertically, on desktop: show in columns
    
    # Get raw vehicle name from selection (remove " Pocket Report")
    raw_vehicle = selected_report.replace(" Pocket Report", "")
    
    # Fetch models/families dynamically based on selection
    models = get_vehicle_families(raw_vehicle)
    
    # If no models found (or empty list), fallback to default H6 models if H6 is selected,
    # otherwise show a warning or handle gracefully.
    if not models and raw_vehicle == 'H6':
        models = ['H6 Hev2', 'H6 PHev19', 'H6 PHvev35', 'H6 GT']
    elif not models:
        # If models list is empty, we might want to show a message or use what we found
        # For now, let's just proceed. The loops below will just not run if models is empty.
        pass

    # Generate data
    summary_data = get_summary_data(raw_vehicle, selected_month_str, models)
    
    # Fetch real color data from database
    color_data = get_color_data(raw_vehicle, selected_month_str, models)
    
    # Fetch real daily and state data
    daily_data = get_daily_data(raw_vehicle, selected_month_str, models)
    state_data = get_state_data(raw_vehicle, selected_month_str, models)
    dealer_data = get_dealer_group_data(raw_vehicle, selected_month_str, models)
    
    # Detect screen size and adjust layout
    # Streamlit columns automatically stack on mobile, but we'll ensure it works well
    # For mobile: single column, for tablet: 2 columns, for desktop: 4 columns
    # Streamlit handles this automatically, but we ensure proper stacking
    
    # Define grid size - max 3 columns per row for better visibility on all screens
    # On mobile, these will naturally stack 1 per row.
    MAX_COLS = 3

    # Use columns - they will automatically stack on mobile devices
    if models:
        # Helper to chunk list
        def chunked(iterable, n):
            return [iterable[i:i + n] for i in range(0, len(iterable), n)]

        model_chunks = chunked(models, MAX_COLS)
        
        # 0. Summary Section
        for chunk in model_chunks:
            cols = st.columns(len(chunk))
            for idx, model_name in enumerate(chunk):
                with cols[idx]:
                    render_model_header_and_summary(model_name, summary_data)
        
        # Spacer removed
    else:
        st.info("No models found for this selection.")

    # Calculate Total He dynamically from the fetched summary data
    # Sum of all metrics for all models displayed
    total_he = 0
    if summary_data:
        for model_metrics in summary_data.values():
            total_he += model_metrics.get('ok_form_without_payment', 0)
            total_he += model_metrics.get('ok_form_with_payment', 0)
            total_he += model_metrics.get('9k_last_24_hours', 0)

    # Total He Section - Full Width
    # total_he is now calculated dynamically above
    st.markdown(f"""
        <div class="total-card">
            <span class="total-value">{format_number(total_he)}</span>
            <span class="total-label">Total {raw_vehicle}</span>
        </div>
        <div style="margin-bottom: 1.5rem;"></div>
    """, unsafe_allow_html=True)
    
    # Detailed sections below - Row by Row alignment
    if models:
        # Helper function for grid rendering
        def render_section_grid(models, section_type):
            chunks = chunked(models, MAX_COLS)
            for chunk in chunks:
                cols = st.columns(len(chunk))
                for idx, model_name in enumerate(chunk):
                    with cols[idx]:
                        if section_type == "color":
                            st.markdown(f"<div class='chart-header'>{model_name} by color</div>", unsafe_allow_html=True)
                            color_html = render_color_table(model_name, color_data)
                            st.markdown(color_html, unsafe_allow_html=True)
                        elif section_type == "day":
                            st.markdown(f"<div class='chart-header'>{model_name} by day</div>", unsafe_allow_html=True)
                            daily_chart = render_daily_chart(model_name, daily_data)
                            st.plotly_chart(daily_chart, use_container_width=True, config={'displayModeBar': False})
                        elif section_type == "state":
                            st.markdown(f"<div class='chart-header'>{model_name} by state</div>", unsafe_allow_html=True)
                            state_map = render_state_map(model_name, state_data)
                            st.plotly_chart(state_map, use_container_width=True, config={'displayModeBar': False})
                        elif section_type == "dealer":
                            st.markdown(f"<div class='chart-header'>{model_name} by Dealer Group</div>", unsafe_allow_html=True)
                            dealer_html = render_dealer_group_table(model_name, dealer_data)
                            st.markdown(dealer_html, unsafe_allow_html=True)

        # 1. By Color Row
        render_section_grid(models, "color")
        st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

        # 2. By Day Row
        render_section_grid(models, "day")
        st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

        # 3. By State Row
        render_section_grid(models, "state")
        st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

        # 4. By Dealer Group Row
        render_section_grid(models, "dealer")
                
        st.markdown("---")

    # Comparison Section
    render_comparison_section(raw_vehicle, month_options, models)


if __name__ == "__main__":
    main()
