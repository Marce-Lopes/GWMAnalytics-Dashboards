
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from constants import BRAZIL_STATES
from database import get_comparison_daily_data
from utils import get_normalized_weekday

def render_daily_chart(model_name, daily_data):
    """Render daily line chart for a model using real data"""
    # Handle case sensitivity and missing keys
    if model_name in daily_data:
        data = daily_data[model_name]
    else:
        # Try to find a case-insensitive match
        match = next((k for k in daily_data.keys() if k.lower() == model_name.lower()), None)
        if match:
            data = daily_data[match]
        else:
            data = {}

    if not data:
        # Return empty chart or message if no data
        # create empty dataframe with columns
        df = pd.DataFrame({'date': [], 'value': []})
    else:
        # Convert dictionary to DataFrame
        # keys are date strings (YYYY-MM-DD), values are counts
        df = pd.DataFrame({
            'date': list(data.keys()),
            'value': list(data.values())
        })
        # Convert date to datetime for proper sorting and plotting
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')

    # Use Excel Grid Theme
    line_color = '#0000FF'  # Pure Blue
    marker_color = '#000000' # Black
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['value'],
        mode='lines+markers',
        name=model_name,
        line=dict(width=2, color=line_color, shape='spline'), # Smooth line
        marker=dict(size=4, color=marker_color, line=dict(width=1, color=line_color))
    ))
    
    fig.update_layout(
        title={'text': '', 'font': {'size': 1}}, # Explicitly empty title to avoid "undefined"
        xaxis_title=None,
        yaxis_title=None,
        height=200,
        margin=dict(l=0, r=0, t=10, b=25), # Zero side margins, minimal top/bottom
        font=dict(family='Montserrat', size=9, color='#000000'),
        plot_bgcolor='rgba(255,255,255,1)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        xaxis=dict(
            tickformat='%d-%m',
            tickangle=-45,
            tickfont=dict(size=8, color='#000000'),
            showgrid=False, # Remove gridlines
            gridcolor='#E0E0E0',
            showline=False,
            linecolor='#000000',
            automargin=True # Allow label space but keep it tight
        ),
        yaxis=dict(
            visible=True, 
            showticklabels=False, 
            showgrid=False, # Remove gridlines
            gridcolor='#E0E0E0',
            zeroline=True,
            zerolinecolor='#000000',
            tickfont=dict(size=8, color='#000000'),
            showline=False,
            linecolor='#000000',
            automargin=False # Don't reserve space for hidden labels
        ),
        hovermode='x unified', # Enhanced hover
        # Make chart responsive
        autosize=False
    )
    
    return fig


def render_comparison_chart(vehicle_name, month_a, month_b, family_name, status_filter, mode):
    """
    Render comparison chart between Month A and Month B.
    mode: 'MoM' (Day vs Day) or 'Normalized' (Weekday vs Weekday)
    """
    # Fetch data
    data_a = get_comparison_daily_data(vehicle_name, month_a, family_name, status_filter)
    data_b = get_comparison_daily_data(vehicle_name, month_b, family_name, status_filter)
    
    df_a = pd.DataFrame({'date': list(data_a.keys()), 'value': list(data_a.values())})
    df_b = pd.DataFrame({'date': list(data_b.keys()), 'value': list(data_b.values())})
    
    if df_a.empty and df_b.empty:
        st.info("No data available for the selected comparison.")
        return
        
    # Process Data based on Mode
    if mode == 'MoM':
        # Align by Day of Month (1, 2, 3...)
        if not df_a.empty:
            df_a['date'] = pd.to_datetime(df_a['date'])
            df_a['key'] = df_a['date'].dt.day
        else:
             df_a = pd.DataFrame({'key': [], 'value': []})
             
        if not df_b.empty:
            df_b['date'] = pd.to_datetime(df_b['date'])
            df_b['key'] = df_b['date'].dt.day
        else:
             df_b = pd.DataFrame({'key': [], 'value': []})
            
        x_label = "Day of Month"
        
    else: # Normalized
        # Align by Nth Weekday
        if not df_a.empty:
            df_a['date'] = pd.to_datetime(df_a['date'])
            df_a['key'] = df_a['date'].apply(get_normalized_weekday)
            # Add sort key (day of month) to ensure correct order
            df_a['sort_key'] = df_a['date'].dt.day 
        else:
             df_a = pd.DataFrame({'key': [], 'value': [], 'sort_key': []})

        if not df_b.empty:
            df_b['date'] = pd.to_datetime(df_b['date'])
            df_b['key'] = df_b['date'].apply(get_normalized_weekday)
            df_b['sort_key'] = df_b['date'].dt.day
        else:
             df_b = pd.DataFrame({'key': [], 'value': [], 'sort_key': []})
             
        x_label = "Normalized Weekday"

    # Merge DataFrames on Key
    # We need a master list of keys to ensure we show all points
    if mode == 'MoM':
        all_keys = sorted(list(set(df_a['key'].tolist() + df_b['key'].tolist())))
    else:
        # For sorting normalized keys, we can cheat: 
        # "1st Monday" -> 10, "1st Tuesday" -> 11... "2nd Monday" -> 20.
        # Map Weekday to 0-6. N * 10 + Weekday.
        
        weekday_map = {'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6}
        
        def get_sort_val(key):
            try:
                # key format: "1st Monday"
                parts = key.split(' ')
                nth = int(parts[0][:-2]) # 1, 2, 3
                day = parts[1]
                return nth * 10 + weekday_map.get(day, 0)
            except:
                return 999

        all_keys = list(set(df_a['key'].tolist() + df_b['key'].tolist()))
        all_keys.sort(key=get_sort_val)

    # Create master dataframe for plotting
    plot_data = []
    for k in all_keys:
        val_a = df_a[df_a['key'] == k]['value'].sum() if not df_a.empty and k in df_a['key'].values else None
        val_b = df_b[df_b['key'] == k]['value'].sum() if not df_b.empty and k in df_b['key'].values else None
        plot_data.append({'key': k, f'Month A ({month_a})': val_a, f'Month B ({month_b})': val_b})
        
    df_plot = pd.DataFrame(plot_data)
    
    # Plotly Chart
    fig = go.Figure()
    
    # Month A (Solid Line)
    fig.add_trace(go.Scatter(
        x=df_plot['key'],
        y=df_plot[f'Month A ({month_a})'],
        mode='lines+markers',
        name=f'Month A: {month_a}',
        line=dict(width=3, color='#0000FF'), # Pure Blue
        marker=dict(size=6, color='#0000FF', line=dict(width=1, color='white')),
        connectgaps=True 
    ))
    
    # Month B (Dotted Line)
    fig.add_trace(go.Scatter(
        x=df_plot['key'],
        y=df_plot[f'Month B ({month_b})'],
        mode='lines+markers',
        name=f'Month B: {month_b}',
        line=dict(width=3, color='#000000', dash='dot'), # Black Dotted for contrast
        marker=dict(size=6, color='#000000', line=dict(width=1, color='white')),
        connectgaps=True
    ))
    
    fig.update_layout(
        title={
            'text': f"Comparison: {month_a} vs {month_b} ({mode})",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(family='Montserrat', size=14, color='#000000')
        },
        xaxis_title=x_label,
        yaxis_title="Orders",
        height=400,
        margin=dict(l=40, r=20, t=60, b=60),
        font=dict(family='Montserrat', size=10, color='#000000'),
        plot_bgcolor='rgba(255,255,255,1)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(family='Montserrat', size=10, color='#000000')
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='#E0E0E0',
            showline=True,
            linecolor='#000000',
            tickfont=dict(color='#000000')
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#E0E0E0',
            zeroline=True,
            zerolinecolor='#000000',
            tickfont=dict(color='#000000'),
            linecolor='#000000'
        ),
        autosize=True
    )
    
    if mode == 'Normalized':
         fig.update_xaxes(tickangle=-45)
         
    st.plotly_chart(fig, use_container_width=True)


def render_state_map(model_name, state_data):
    """Render Brazil state map visualization for a model using real data"""
    # Handle case sensitivity and missing keys
    if model_name in state_data:
        data = state_data[model_name]
    else:
        # Try to find a case-insensitive match
        match = next((k for k in state_data.keys() if k.lower() == model_name.lower()), None)
        if match:
            data = state_data[match]
        else:
            # Default data
            data = {}
            
    if not data:
         # Return empty chart logic or small placeholder
         data = {'No Data': 0}
         df_sorted = pd.DataFrame({'state_name': ['No Data'], 'value': [0]})
    else:
        # Create DataFrame with state codes and values
        # Map state codes to names using BRAZIL_STATES, fallback to code if not found
        state_names = [BRAZIL_STATES.get(code, code) for code in data.keys()]
        
        df = pd.DataFrame({
            'state_code': list(data.keys()),
            'state_name': state_names,
            'value': list(data.values())
        })
        
        # Sort by value for better visualization
        df_sorted = df.sort_values('value', ascending=True).tail(15)  # Top 15 states
    
    # Create horizontal bar chart (more map-like visualization)
    # Note: For a full choropleth map, GeoJSON data for Brazil states would be needed
    fig = go.Figure()
    
    # Custom Gradient Scale from Blue to Dark Blue
    custom_colorscale = [
        [0.0, '#6699FF'],
        [1.0, '#0000FF']
    ]
    
    fig.add_trace(go.Bar(
        x=df_sorted['value'],
        y=df_sorted['state_name'],
        orientation='h',
        marker=dict(
            color=df_sorted['value'],
            colorscale=custom_colorscale, # Custom Gradient
            showscale=False, # Hide scale for cleaner look
            line=dict(color='#000000', width=1) # Black border
        ),
        text=df_sorted['value'],
        textposition='outside',
        textfont=dict(family='Montserrat', color='#000000', size=14) # Increased size
    ))
    
    fig.update_layout(
        height=350, # Increased height
        margin=dict(l=100, r=20, t=10, b=40), # Reduced top margin as title is external
        font=dict(family='Montserrat', size=9, color='#000000'),
        xaxis_title="",
        yaxis_title="",
        yaxis=dict(
            autorange="reversed", 
            tickfont=dict(color='#000000')
        ),  # Reverse to show highest on top
        xaxis=dict(
            visible=False
        ), # Hide X Axis
        plot_bgcolor='rgba(255,255,255,1)',
        paper_bgcolor='rgba(0,0,0,0)',
        # Make chart responsive
        autosize=True
    )
    
    return fig