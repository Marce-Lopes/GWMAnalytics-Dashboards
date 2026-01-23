import clickhouse_connect
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta, date

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

@st.cache_data(ttl=450)
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
        query = "SELECT DISTINCT Vehicle FROM mart.ecommerce_pocket_report WHERE Vehicle NOT LIKE '%:%' ORDER BY Vehicle SETTINGS max_bytes_before_external_group_by = 3000000000"
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

@st.cache_data(ttl=450)
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
        SETTINGS max_bytes_before_external_group_by = 3000000000
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

@st.cache_data(ttl=450)
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
        query = "SELECT DISTINCT `Vehicle Family` FROM mart.ecommerce_pocket_report WHERE Vehicle = %(vehicle)s ORDER BY `Vehicle Family` SETTINGS max_bytes_before_external_group_by = 3000000000"
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

@st.cache_data(ttl=450)
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
        SETTINGS max_bytes_before_external_group_by = 3000000000
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
        SETTINGS max_bytes_before_external_group_by = 3000000000
        """
        
        # Query 3: 9K Last 24 Hours (Date >= today() - 1)
        query_24h = """
        SELECT `Vehicle Family`, sum(Orders) as total
        FROM mart.ecommerce_pocket_report
        WHERE Vehicle = %(vehicle)s
        AND Date >= today() - 1
        GROUP BY `Vehicle Family`
        SETTINGS max_bytes_before_external_group_by = 3000000000
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
        current_month_query = "SELECT formatDateTime(today(), '%b/%y') SETTINGS max_bytes_before_external_group_by = 3000000000"
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

@st.cache_data(ttl=450)
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
        current_month_query = "SELECT formatDateTime(today(), '%b/%y') SETTINGS max_bytes_before_external_group_by = 3000000000"
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
            SETTINGS max_bytes_before_external_group_by = 3000000000
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
            SETTINGS max_bytes_before_external_group_by = 3000000000
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

@st.cache_data(ttl=450)
def get_daily_data(vehicle_name, month_str, models):
    """
    Fetch total count (Paid + Unpaid + Last 24h) grouped by Date for each model.
    """
    client = get_db_client()
    daily_data = {model: {} for model in models}
    
    if not client:
        return daily_data

    try:
        current_month_query = "SELECT formatDateTime(today(), '%b/%y') SETTINGS max_bytes_before_external_group_by = 3000000000"
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
            SETTINGS max_bytes_before_external_group_by = 3000000000
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
            SETTINGS max_bytes_before_external_group_by = 3000000000
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

@st.cache_data(ttl=450)
def get_state_data(vehicle_name, month_str, models):
    """
    Fetch total count (Paid + Unpaid + Last 24h) grouped by Dealer State for each model.
    """
    client = get_db_client()
    state_data = {model: {} for model in models}
    
    if not client:
        return state_data

    try:
        current_month_query = "SELECT formatDateTime(today(), '%b/%y') SETTINGS max_bytes_before_external_group_by = 3000000000"
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
            SETTINGS max_bytes_before_external_group_by = 3000000000
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
            SETTINGS max_bytes_before_external_group_by = 3000000000
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

@st.cache_data(ttl=450)
def get_dealer_group_data(vehicle_name, month_str, models):
    """
    Fetch total count grouped by Dealer Group for each model.
    """
    client = get_db_client()
    dealer_data = {model: {} for model in models}
    
    if not client:
        return dealer_data

    try:
        current_month_query = "SELECT formatDateTime(today(), '%b/%y') SETTINGS max_bytes_before_external_group_by = 3000000000"
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
            SETTINGS max_bytes_before_external_group_by = 3000000000
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
            SETTINGS max_bytes_before_external_group_by = 3000000000
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

@st.cache_data(ttl=450)
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
            
        query += " GROUP BY day ORDER BY day ASC SETTINGS max_bytes_before_external_group_by = 3000000000"
        
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

@st.cache_data(ttl=450)
def get_kpi_metrics(selected_vehicle, month_str):
    """
    Fetch KPI metrics: Total, vs Last Month, vs Last Year, Share
    """
    client = get_db_client()
    if not client:
        return {'total': 0, 'prev_total': 0, 'ly_total': 0, 'market_total': 0}

    try:
        # 1. Date Math
        current_date = datetime.strptime(month_str, "%b/%y")
        
        # Prev Month (First day of current - 1 day -> prev month end -> replace day 1)
        first_day = current_date.replace(day=1)
        prev_month_end = first_day - timedelta(days=1)
        prev_month_date = prev_month_end.replace(day=1)
        prev_month_str = prev_month_date.strftime("%b/%y")
        
        # Last Year
        try:
            last_year_date = current_date.replace(year=current_date.year - 1)
        except ValueError:
            last_year_date = current_date.replace(year=current_date.year - 1, day=28)
        last_year_str = last_year_date.strftime("%b/%y")
        
        # 2. Check if current month (for current date logic)
        current_month_query = "SELECT formatDateTime(today(), '%b/%y') SETTINGS max_bytes_before_external_group_by = 3000000000"
        res = client.query(current_month_query)
        is_current = False
        if res and res.result_rows and res.result_rows[0][0] == month_str:
            is_current = True
            
        # 3. Helper for conditions (Hardcoded format string to avoid issues)
        def get_condition_sql(m_key, is_curr, limit_day=False):
            base_cond = f"formatDateTime(Date, '%%b/%%y') = %({m_key})s"
            
            if is_curr:
                # Current month logic: Data < today - 1 OR recent data
                # AND Status filter is applied outside or appended
                return f"""(
                    ({base_cond} AND Date < today() - 1)
                    OR
                    (Date >= today() - 1)
                )"""
            elif limit_day:
                # Same-day comparison for past periods (e.g. Last Year, Prev Month)
                # Restrict to days <= today's day number
                return f"{base_cond} AND toDayOfMonth(Date) <= toDayOfMonth(today())"
            else:
                # Full month
                return base_cond

        # 4. Queries
        params = {
            'v': selected_vehicle,
            'm_curr': month_str,
            'm_prev': prev_month_str,
            'm_ly': last_year_str
        }
        
        # Conditions
        cond_curr = get_condition_sql('m_curr', is_current)
        # Apply limit_day to prev month if current is partial
        cond_prev = get_condition_sql('m_prev', False, limit_day=is_current) 
        cond_ly = get_condition_sql('m_ly', False, limit_day=is_current)
        
        # Base Status Filters
        status_total = "Status IN ('Invoiced', 'Not Invoiced', 'Open')"
        status_paid = "Status = 'Invoiced'"
        status_unpaid = "Status IN ('Not Invoiced', 'Open')"

        # Q1: Current Total
        q1 = f"SELECT sum(Orders) FROM mart.ecommerce_pocket_report WHERE Vehicle = %(v)s AND {cond_curr} AND {status_total} SETTINGS max_bytes_before_external_group_by = 3000000000"
        res1 = client.query(q1, params)
        total_curr = res1.result_rows[0][0] if res1.result_rows and res1.result_rows[0][0] else 0
        
        # Q2: Prev Month Total
        q2 = f"SELECT sum(Orders) FROM mart.ecommerce_pocket_report WHERE Vehicle = %(v)s AND {cond_prev} AND {status_total} SETTINGS max_bytes_before_external_group_by = 3000000000"
        res2 = client.query(q2, params)
        total_prev = res2.result_rows[0][0] if res2.result_rows and res2.result_rows[0][0] else 0
        
        # Q3: Last Year Total
        q3 = f"SELECT sum(Orders) FROM mart.ecommerce_pocket_report WHERE Vehicle = %(v)s AND {cond_ly} AND {status_total} SETTINGS max_bytes_before_external_group_by = 3000000000"
        res3 = client.query(q3, params)
        total_ly = res3.result_rows[0][0] if res3.result_rows and res3.result_rows[0][0] else 0
        
        # Q4: Market Total (All Vehicles)
        q4 = f"SELECT sum(Orders) FROM mart.ecommerce_pocket_report WHERE {cond_curr} AND {status_total} SETTINGS max_bytes_before_external_group_by = 3000000000"
        res4 = client.query(q4, params)
        market_total = res4.result_rows[0][0] if res4.result_rows and res4.result_rows[0][0] else 0
        
        # --- New KPIs: Paid & Unpaid ---
        
        # Q5: Paid Current
        q5 = f"SELECT sum(Orders) FROM mart.ecommerce_pocket_report WHERE Vehicle = %(v)s AND {cond_curr} AND {status_paid} SETTINGS max_bytes_before_external_group_by = 3000000000"
        res5 = client.query(q5, params)
        paid_curr = res5.result_rows[0][0] if res5.result_rows and res5.result_rows[0][0] else 0
        
        # Q6: Paid Prev
        q6 = f"SELECT sum(Orders) FROM mart.ecommerce_pocket_report WHERE Vehicle = %(v)s AND {cond_prev} AND {status_paid} SETTINGS max_bytes_before_external_group_by = 3000000000"
        res6 = client.query(q6, params)
        paid_prev = res6.result_rows[0][0] if res6.result_rows and res6.result_rows[0][0] else 0
        
        # Q7: Unpaid Current
        q7 = f"SELECT sum(Orders) FROM mart.ecommerce_pocket_report WHERE Vehicle = %(v)s AND {cond_curr} AND {status_unpaid} SETTINGS max_bytes_before_external_group_by = 3000000000"
        res7 = client.query(q7, params)
        unpaid_curr = res7.result_rows[0][0] if res7.result_rows and res7.result_rows[0][0] else 0
        
        # Q8: Unpaid Prev
        q8 = f"SELECT sum(Orders) FROM mart.ecommerce_pocket_report WHERE Vehicle = %(v)s AND {cond_prev} AND {status_unpaid} SETTINGS max_bytes_before_external_group_by = 3000000000"
        res8 = client.query(q8, params)
        unpaid_prev = res8.result_rows[0][0] if res8.result_rows and res8.result_rows[0][0] else 0

        # --- New KPI: Weekday Adjusted (Only if is_current) ---
        weekday_data = None
        if is_current:
            try:
                # Get max date (Today in DB context)
                q_max = "SELECT max(Date) FROM mart.ecommerce_pocket_report SETTINGS max_bytes_before_external_group_by = 3000000000"
                res_max = client.query(q_max)
                if res_max and res_max.result_rows:
                    db_today = res_max.result_rows[0][0] # date object
                    
                    # Today's Val
                    q_today = f"SELECT sum(Orders) FROM mart.ecommerce_pocket_report WHERE Vehicle = %(v)s AND toDate(Date) = %(d)s AND {status_total} SETTINGS max_bytes_before_external_group_by = 3000000000"
                    res_today = client.query(q_today, {'v': selected_vehicle, 'd': db_today})
                    today_val = res_today.result_rows[0][0] if res_today.result_rows and res_today.result_rows[0][0] else 0
                    
                    # Calculate Adjusted Date
                    # n-th weekday of month
                    day_num = db_today.day
                    n = (day_num - 1) // 7 + 1
                    w = db_today.weekday()
                    
                    # Find same n-th weekday in prev month
                    # prev_month_date is already a datetime object (1st of prev month)
                    
                    # Helper to find date
                    def get_nth_weekday_date(year, month, target_weekday, target_n):
                        c = 0
                        d = date(year, month, 1)
                        while d.month == month:
                            if d.weekday() == target_weekday:
                                c += 1
                                if c == target_n:
                                    return d
                            d += timedelta(days=1)
                        return None

                    adj_date = get_nth_weekday_date(prev_month_date.year, prev_month_date.month, w, n)
                    
                    if adj_date:
                        q_adj = f"SELECT sum(Orders) FROM mart.ecommerce_pocket_report WHERE Vehicle = %(v)s AND toDate(Date) = %(d)s AND {status_total} SETTINGS max_bytes_before_external_group_by = 3000000000"
                        res_adj = client.query(q_adj, {'v': selected_vehicle, 'd': adj_date})
                        adj_val = res_adj.result_rows[0][0] if res_adj.result_rows and res_adj.result_rows[0][0] else 0
                        
                        weekday_data = {
                            'today_val': float(today_val),
                            'today_date': db_today,
                            'adj_val': float(adj_val),
                            'adj_date': adj_date
                        }
            except Exception as e:
                print(f"Weekday KPI Error: {e}")
                pass
        
        return {
            'total': float(total_curr),
            'prev_total': float(total_prev),
            'ly_total': float(total_ly),
            'market_total': float(market_total),
            'paid_curr': float(paid_curr),
            'paid_prev': float(paid_prev),
            'unpaid_curr': float(unpaid_curr),
            'unpaid_prev': float(unpaid_prev),
            'weekday_data': weekday_data
        }
        
    except Exception as e:
        st.error(f"Error fetching KPI metrics: {e}")
        return {'total': 0, 'prev_total': 0, 'ly_total': 0, 'market_total': 0}

@st.cache_data(ttl=150)
def get_last_updated_date():
    """Fetch the maximum date available in the dataset"""
    client = get_db_client()
    if not client:
        return None
        
    try:
        query = "SELECT max(Date) FROM mart.ecommerce_pocket_report SETTINGS max_bytes_before_external_group_by = 3000000000"
        result = client.query(query)
        if result and result.result_rows:
            return result.result_rows[0][0]
        return None
    except Exception as e:
        # Don't show error to user for this auxiliary info, just log or return None
        return None
