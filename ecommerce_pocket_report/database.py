import clickhouse_connect
import pandas as pd
import streamlit as st

# Database configuration

DB_HOST = '101.44.195.43'
DB_PORT = 8123
DB_USER = 'default'
DB_PASSWORD = 'Hw#2024.GWM'
DB_NAME = 'default' # Using default as initial connection, table is in 'mart' schema
@st.cache_resource
def get_db_client():
    """Get ClickHouse database client"""
    try:
        client = clickhouse_connect.get_client(
            host=DB_HOST,
            port=DB_PORT,
            username=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            connect_timeout=10
        )
        return client
    except Exception as e:
        st.error(f"Failed to connect to database: {e}")
        return None

@st.cache_data(ttl=900)
def get_vehicle_options():
    """Fetch unique vehicle options from the database"""
    client = get_db_client()
    if not client:
        # Fallback options if connection fails
        return [
            "H6 Pocket Report",
            "ORA Pocket Report",
            "H9 Pocket Report",
            "POER Pocket Report",
            "TANK Pocket Report"
        ]
    
    try:
        # Query to get unique vehicles
        # Filter out values that look like timestamps (containing ':')
        query = "SELECT DISTINCT Vehicle FROM mart.ecommerce_pocket_report WHERE Vehicle NOT LIKE '%:%' ORDER BY Vehicle"
        result = client.query(query)
        
        # Extract values from result
        vehicles = [row[0] for row in result.result_rows]
        
        # If no vehicles found, return fallback
        if not vehicles:
             return [
                "H6 Pocket Report",
                "ORA Pocket Report",
                "H9 Pocket Report",
                "POER Pocket Report",
                "TANK Pocket Report"
            ]
            
        # Format as "Vehicle Pocket Report" if needed, or just return vehicle names
        # The user requested: "Vehicles names (H6,ORA,H9,POER,TANK) should came from the 'Vehicle' Column"
        # And the previous options were "H6 Pocket Report".
        # I will append " Pocket Report" to maintain the existing UI style if the raw values are just names.
        
        formatted_options = [f"{v} Pocket Report" for v in vehicles]
        return formatted_options
        
    except Exception as e:
        st.error(f"Error fetching vehicle options: {e}")
        # Fallback
        return [
            "H6 Pocket Report",
            "ORA Pocket Report",
            "H9 Pocket Report",
            "POER Pocket Report",
            "TANK Pocket Report"
        ]

@st.cache_data(ttl=900)
def get_month_options():
    """Fetch unique month options from the database formatted as Mon/YY"""
    client = get_db_client()
    if not client:
        # Fallback options if connection fails
        return ["Jan/24", "Feb/24", "Mar/24", "Apr/24", "May/24", "Jun/24"]
    
    try:
        # Query to get unique months formatted as requested
        # We also select toStartOfMonth(Date) to order them correctly
        query = """
        SELECT DISTINCT 
            concat(formatDateTime(Date, '%b/%y')) as month_label,
            toStartOfMonth(Date) as sort_date
        FROM mart.ecommerce_pocket_report 
        ORDER BY sort_date DESC
        """
        result = client.query(query)
        
        # Extract just the formatted strings (first column)
        months = [row[0] for row in result.result_rows]
        
        # If no data, return fallback
        if not months:
             return ["Jan/24", "Feb/24", "Mar/24", "Apr/24", "May/24", "Jun/24"]
            
        return months
        
    except Exception as e:
        st.error(f"Error fetching month options: {e}")
        # Fallback
        return ["Jan/24", "Feb/24", "Mar/24", "Apr/24", "May/24", "Jun/24"]

@st.cache_data(ttl=900)
def get_vehicle_families(vehicle_name):
    """Fetch vehicle families for a specific vehicle"""
    client = get_db_client()
    if not client:
        # Fallback for H6 (default)
        if vehicle_name == 'H6':
             return ['H6 Hev2', 'H6 PHev19', 'H6 PHvev35', 'H6 GT']
        return []

    try:
        # Query to get vehicle families
        query = "SELECT DISTINCT `Vehicle Family` FROM mart.ecommerce_pocket_report WHERE Vehicle = %(vehicle)s ORDER BY `Vehicle Family`"
        result = client.query(query, parameters={'vehicle': vehicle_name})
        
        families = [row[0] for row in result.result_rows]
        
        if not families:
             if vehicle_name == 'H6':
                 return ['H6 Hev2', 'H6 PHev19', 'H6 PHvev35', 'H6 GT']
             return []
             
        return families
    except Exception as e:
        st.error(f"Error fetching vehicle families: {e}")
        if vehicle_name == 'H6':
             return ['H6 Hev2', 'H6 PHev19', 'H6 PHvev35', 'H6 GT']
        return []

@st.cache_data(ttl=900)
def get_summary_data(vehicle_name, month_str, models):
    """
    Fetch summary KPI data for the given vehicle and month.
    Returns a dictionary keyed by model name (Vehicle Family).
    """
    client = get_db_client()
    # Initialize with zeros for all models to ensure structure
    summary_data = {
        model: {
            'ok_form_without_payment': 0,
            'ok_form_with_payment': 0,
            '9k_last_24_hours': 0
        } for model in models
    }
    
    if not client:
        return summary_data

    try:
        params = {'vehicle': vehicle_name, 'month': month_str}

        # Query 1: 9K Form With Payment (Status = 'Invoiced')
        # Using double % to escape percent sign in Python string for formatDateTime
        # And Date < today() - 1 (Yesterday)
        query_paid = """
        SELECT `Vehicle Family`, sum(Orders) as total
        FROM mart.ecommerce_pocket_report
        WHERE Vehicle = %(vehicle)s
        AND formatDateTime(Date, '%%b/%%y') = %(month)s
        AND Status = 'Invoiced'
        AND Date < today() - 1
        GROUP BY `Vehicle Family`
        """
        
        # Query 2: 9K Form Without Payment (Status IN ('Not Invoiced', 'Open'))
        # And Date < today() - 1 (Yesterday)
        query_unpaid = """
        SELECT `Vehicle Family`, sum(Orders) as total
        FROM mart.ecommerce_pocket_report
        WHERE Vehicle = %(vehicle)s
        AND formatDateTime(Date, '%%b/%%y') = %(month)s
        AND Status IN ('Not Invoiced', 'Open')
        AND Date < today() - 1
        GROUP BY `Vehicle Family`
        """
        
        # Query 3: 9K Last 24 Hours (Date >= today() - 1)
        query_24h = """
        SELECT `Vehicle Family`, sum(Orders) as total
        FROM mart.ecommerce_pocket_report
        WHERE Vehicle = %(vehicle)s
        AND Date >= today() - 1
        GROUP BY `Vehicle Family`
        """
        
        # Execute Query 1
        result_paid = client.query(query_paid, parameters=params)
        for row in result_paid.result_rows:
            family, count = row
            if family in summary_data:
                summary_data[family]['ok_form_with_payment'] = int(count) if count is not None else 0
                
        # Execute Query 2
        result_unpaid = client.query(query_unpaid, parameters=params)
        for row in result_unpaid.result_rows:
            family, count = row
            if family in summary_data:
                summary_data[family]['ok_form_without_payment'] = int(count) if count is not None else 0
                
        # Execute Query 3 - Only if selected month is current month
        # We query the DB for the current month formatted string to ensure consistency with the filter format
        current_month_query = "SELECT formatDateTime(today(), '%b/%y')"
        current_month_res = client.query(current_month_query)
        if current_month_res and current_month_res.result_rows:
            current_month_str = current_month_res.result_rows[0][0]
            
            if month_str == current_month_str:
                result_24h = client.query(query_24h, parameters={'vehicle': vehicle_name})
                for row in result_24h.result_rows:
                    family, count = row
                    if family in summary_data:
                        summary_data[family]['9k_last_24_hours'] = int(count) if count is not None else 0
                
        return summary_data
        
    except Exception as e:
        st.error(f"Error fetching summary data: {e}")
        return summary_data

@st.cache_data(ttl=900)
def get_color_data(vehicle_name, month_str, models):
    """
    Fetch total count (Paid + Unpaid + Last 24h) grouped by Exterior Color for each model.
    """
    client = get_db_client()
    # Initialize with empty dicts for all models
    color_data = {model: {} for model in models}
    
    if not client:
        return color_data

    try:
        # Check if current month to determine if we include Last 24h (which is date-based, not month-based)
        current_month_query = "SELECT formatDateTime(today(), '%b/%y')"
        current_month_res = client.query(current_month_query)
        is_current_month = False
        if current_month_res and current_month_res.result_rows:
            current_month_str = current_month_res.result_rows[0][0]
            if month_str == current_month_str:
                is_current_month = True

        if is_current_month:
            # Current Month Logic:
            # 1. Historical (Date < today - 1): Must match Month AND Status IN (Invoiced, Not Invoiced, Open)
            # 2. Recent (Date >= today - 1): All records (implicit Month match as it's recent)
            query = """
            SELECT `Vehicle Family`, `Exterior Color`, sum(Orders) as total
            FROM mart.ecommerce_pocket_report
            WHERE Vehicle = %(vehicle)s
            AND (
                (formatDateTime(Date, '%%b/%%y') = %(month)s AND Status IN ('Invoiced', 'Not Invoiced', 'Open') AND Date < today() - 1)
                OR
                (Date >= today() - 1)
            )
            GROUP BY `Vehicle Family`, `Exterior Color`
            ORDER BY total DESC
            """
        else:
            # Past Month Logic:
            # Only Historical data matching Month AND Status
            query = """
            SELECT `Vehicle Family`, `Exterior Color`, sum(Orders) as total
            FROM mart.ecommerce_pocket_report
            WHERE Vehicle = %(vehicle)s
            AND formatDateTime(Date, '%%b/%%y') = %(month)s
            AND Status IN ('Invoiced', 'Not Invoiced', 'Open')
            GROUP BY `Vehicle Family`, `Exterior Color`
            ORDER BY total DESC
            """
        
        result = client.query(query, parameters={'vehicle': vehicle_name, 'month': month_str})
        
        for row in result.result_rows:
            family, color, count = row
            if family in color_data:
                # If color is empty/None, use 'Unknown'
                color_key = color if color else 'Unknown'
                color_data[family][color_key] = int(count) if count is not None else 0
                
        return color_data
        
    except Exception as e:
        st.error(f"Error fetching color data: {e}")
        return color_data

@st.cache_data(ttl=900)
def get_daily_data(vehicle_name, month_str, models):
    """
    Fetch total count (Paid + Unpaid + Last 24h) grouped by Date for each model.
    """
    client = get_db_client()
    daily_data = {model: {} for model in models}
    
    if not client:
        return daily_data

    try:
        current_month_query = "SELECT formatDateTime(today(), '%b/%y')"
        current_month_res = client.query(current_month_query)
        is_current_month = False
        if current_month_res and current_month_res.result_rows:
            current_month_str = current_month_res.result_rows[0][0]
            if month_str == current_month_str:
                is_current_month = True

        if is_current_month:
            query = """
            SELECT `Vehicle Family`, toDate(Date) as day, sum(Orders) as total
            FROM mart.ecommerce_pocket_report
            WHERE Vehicle = %(vehicle)s
            AND (
                (formatDateTime(Date, '%%b/%%y') = %(month)s AND Status IN ('Invoiced', 'Not Invoiced', 'Open') AND Date < today() - 1)
                OR
                (Date >= today() - 1)
            )
            GROUP BY `Vehicle Family`, day
            ORDER BY day ASC
            """
        else:
            query = """
            SELECT `Vehicle Family`, toDate(Date) as day, sum(Orders) as total
            FROM mart.ecommerce_pocket_report
            WHERE Vehicle = %(vehicle)s
            AND formatDateTime(Date, '%%b/%%y') = %(month)s
            AND Status IN ('Invoiced', 'Not Invoiced', 'Open')
            GROUP BY `Vehicle Family`, day
            ORDER BY day ASC
            """
        
        result = client.query(query, parameters={'vehicle': vehicle_name, 'month': month_str})
        
        for row in result.result_rows:
            family, day, count = row
            if family in daily_data:
                # Format date as YYYY-MM-DD string
                day_str = day.strftime('%Y-%m-%d')
                daily_data[family][day_str] = int(count) if count is not None else 0
                
        return daily_data
        
    except Exception as e:
        st.error(f"Error fetching daily data: {e}")
        return daily_data

@st.cache_data(ttl=900)
def get_state_data(vehicle_name, month_str, models):
    """
    Fetch total count (Paid + Unpaid + Last 24h) grouped by Dealer State for each model.
    """
    client = get_db_client()
    state_data = {model: {} for model in models}
    
    if not client:
        return state_data

    try:
        current_month_query = "SELECT formatDateTime(today(), '%b/%y')"
        current_month_res = client.query(current_month_query)
        is_current_month = False
        if current_month_res and current_month_res.result_rows:
            current_month_str = current_month_res.result_rows[0][0]
            if month_str == current_month_str:
                is_current_month = True

        if is_current_month:
            query = """
            SELECT `Vehicle Family`, `Dealer State`, sum(Orders) as total
            FROM mart.ecommerce_pocket_report
            WHERE Vehicle = %(vehicle)s
            AND (
                (formatDateTime(Date, '%%b/%%y') = %(month)s AND Status IN ('Invoiced', 'Not Invoiced', 'Open') AND Date < today() - 1)
                OR
                (Date >= today() - 1)
            )
            GROUP BY `Vehicle Family`, `Dealer State`
            ORDER BY total DESC
            """
        else:
            query = """
            SELECT `Vehicle Family`, `Dealer State`, sum(Orders) as total
            FROM mart.ecommerce_pocket_report
            WHERE Vehicle = %(vehicle)s
            AND formatDateTime(Date, '%%b/%%y') = %(month)s
            AND Status IN ('Invoiced', 'Not Invoiced', 'Open')
            GROUP BY `Vehicle Family`, `Dealer State`
            ORDER BY total DESC
            """
        
        result = client.query(query, parameters={'vehicle': vehicle_name, 'month': month_str})
        
        for row in result.result_rows:
            family, state, count = row
            if family in state_data:
                state_key = state if state else 'Unknown'
                state_data[family][state_key] = int(count) if count is not None else 0
                
        return state_data
        
    except Exception as e:
        st.error(f"Error fetching state data: {e}")
        return state_data

@st.cache_data(ttl=900)
def get_dealer_group_data(vehicle_name, month_str, models):
    """
    Fetch total count grouped by Dealer Group for each model.
    """
    client = get_db_client()
    dealer_data = {model: {} for model in models}
    
    if not client:
        return dealer_data

    try:
        current_month_query = "SELECT formatDateTime(today(), '%b/%y')"
        current_month_res = client.query(current_month_query)
        is_current_month = False
        if current_month_res and current_month_res.result_rows:
            current_month_str = current_month_res.result_rows[0][0]
            if month_str == current_month_str:
                is_current_month = True

        if is_current_month:
            query = """
            SELECT `Vehicle Family`, `Dealer Group Name`, sum(Orders) as total
            FROM mart.ecommerce_pocket_report
            WHERE Vehicle = %(vehicle)s
            AND (
                (formatDateTime(Date, '%%b/%%y') = %(month)s AND Status IN ('Invoiced', 'Not Invoiced', 'Open') AND Date < today() - 1)
                OR
                (Date >= today() - 1)
            )
            GROUP BY `Vehicle Family`, `Dealer Group Name`
            ORDER BY total DESC
            """
        else:
            query = """
            SELECT `Vehicle Family`, `Dealer Group Name`, sum(Orders) as total
            FROM mart.ecommerce_pocket_report
            WHERE Vehicle = %(vehicle)s
            AND formatDateTime(Date, '%%b/%%y') = %(month)s
            AND Status IN ('Invoiced', 'Not Invoiced', 'Open')
            GROUP BY `Vehicle Family`, `Dealer Group Name`
            ORDER BY total DESC
            """
        
        result = client.query(query, parameters={'vehicle': vehicle_name, 'month': month_str})
        
        for row in result.result_rows:
            family, group, count = row
            if family in dealer_data:
                group_key = group if group else 'Unknown'
                dealer_data[family][group_key] = int(count) if count is not None else 0
                
        return dealer_data
        
    except Exception as e:
        st.error(f"Error fetching dealer group data: {e}")
        return dealer_data

@st.cache_data(ttl=900)
def get_comparison_daily_data(vehicle_name, month_str, family_name, status_filter):
    """
    Fetch daily data for comparison chart.
    vehicle_name: Selected vehicle (e.g. 'H6')
    month_str: Month to fetch (e.g. 'Jan/26')
    family_name: Specific family or 'All'
    status_filter: '9k form without payment', '9k form with payment', 'Total'
    """
    client = get_db_client()
    data = {}
    
    if not client:
        return data

    try:
        # Base query
        query = """
        SELECT toDate(Date) as day, sum(Orders) as total
        FROM mart.ecommerce_pocket_report
        WHERE Vehicle = %(vehicle)s
        AND formatDateTime(Date, '%%b/%%y') = %(month)s
        """
        
        params = {'vehicle': vehicle_name, 'month': month_str}
        
        # Add family filter
        if family_name and family_name != 'All':
            query += " AND `Vehicle Family` = %(family)s"
            params['family'] = family_name
            
        # Add status filter
        if status_filter == '9k form without payment':
            query += " AND Status IN ('Not Invoiced', 'Open')"
        elif status_filter == '9k form with payment':
            query += " AND Status = 'Invoiced'"
        else: # Total
            query += " AND Status IN ('Invoiced', 'Not Invoiced', 'Open')"
            
        query += " GROUP BY day ORDER BY day ASC"
        
        result = client.query(query, parameters=params)
        
        for row in result.result_rows:
            day, count = row
            # Format date as YYYY-MM-DD string
            day_str = day.strftime('%Y-%m-%d')
            data[day_str] = int(count) if count is not None else 0
                
        return data
        
    except Exception as e:
        st.error(f"Error fetching comparison data: {e}")
        return data

@st.cache_data(ttl=300)
def get_last_updated_date():
    """Fetch the maximum date available in the dataset"""
    client = get_db_client()
    if not client:
        return None
        
    try:
        query = "SELECT max(Date) FROM mart.ecommerce_pocket_report"
        result = client.query(query)
        if result and result.result_rows:
            return result.result_rows[0][0]
        return None
    except Exception as e:
        # Don't show error to user for this auxiliary info, just log or return None
        return None
