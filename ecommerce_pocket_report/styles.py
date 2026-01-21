
def get_main_styles():
    return """
    <style>
        /* Reduz o padding superior do container principal */
        .block-container {
            padding-top: 0.1rem;
            padding-bottom: 0rem;
            margin-top: 0.1rem;
        }
        header {
            visibility: hidden;
        }
        
        /* -------------------------------------------------------------------------- */
        /*                                LUXURY THEME                                */
        /* -------------------------------------------------------------------------- */
        
        /* Font Import */
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600&display=swap');
        
        /* General Settings */
        html, body, [class*="css"] {
            font-family: 'Montserrat', sans-serif;
            color: #0F172A; /* Deep Navy Text */
        }
        
        /* Background */
        .stApp {
            background-color: #F8FAFC; /* Very Light Grey-Blue */
        }
        
        /* -------------------------------------------------------------------------- */
        /*                                 COMPONENTS                                 */
        /* -------------------------------------------------------------------------- */
        
        /* Cards (Metrics, Tables) */
        .model-header, .stMarkdown div[data-testid="stMarkdownContainer"] table {
            background: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 12px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
            padding: 1rem !important;
        }

        .summary-card {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
        }

        /* Reset styles for tables inside summary-card to avoid double borders */
        .summary-card table {
            /* Re-apply border to table since we removed card border */
            border: 1px solid #E2E8F0 !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
            background: #FFFFFF !important;
            padding: 1rem !important;
            border-radius: 12px !important;
        }
        
        /* Model Header Specifics */
        .model-header {
            background: linear-gradient(135deg, #0B5ED7 0%, #1D4ED8 100%) !important;
            color: #FFFFFF !important;
            text-transform: uppercase;
            letter-spacing: 1px;
            border: none !important;
            font-size: 1rem !important;
            padding: 0.8rem !important;
        }

        /* Standard Chart Header */
        .chart-header {
            font-family: 'Montserrat', sans-serif !important;
            font-weight: bold !important;
            color: #0F172A !important;
            text-align: center !important;
            margin-bottom: 5px !important;
            margin-top: 5px !important;
        }
        
        /* Tables */
        .dataframe, table {
            width: 100% !important;
            border-collapse: separate !important; 
            border-spacing: 0 !important;
            border: none !important;
            font-family: 'Montserrat', sans-serif !important;
            font-size: 14px !important; /* Base size */
        }
        
        table th {
            background-color: transparent !important;
            color: #64748B !important; /* Slate 500 */
            font-weight: 600 !important;
            text-transform: uppercase !important;
            font-size: 0.85rem !important; /* Increased from 0.75rem */
            letter-spacing: 0.05em !important;
            border: none !important; /* Removed borders */
            padding: 4px !important;
        }
        
        table td {
            font-size: 0.95rem !important; /* Increased for readability */
            color: #334155 !important;
            padding: 4px !important;
            border-bottom: 1px solid #F1F5F9 !important;
        }

        /* Mobile Adjustments */
        @media only screen and (max-width: 600px) {
            html, body {
                font-size: 16px !important; /* Boost base font size on mobile */
            }
            .model-header {
                font-size: 1.1rem !important;
                padding: 1rem !important;
            }
            .chart-header {
                font-size: 1.1rem !important;
                margin-top: 1rem !important;
            }
            /* Make tables more spacious on touch */
            table td, table th {
                padding: 8px 4px !important;
            }
        }
        
        table tr:last-child td {
            border-bottom: none !important;
        }
        
        /* Remove alternating colors override (keep white) */
        table tbody tr:nth-child(even), table tbody tr:nth-child(odd) {
            background-color: transparent !important;
        }

        /* -------------------------------------------------------------------------- */
        /*                                   WIDGETS                                  */
        /* -------------------------------------------------------------------------- */
        
        /* Selectboxes */
        .stSelectbox div[data-baseweb="select"] > div {
            background-color: #FFFFFF !important;
            border-radius: 8px !important;
            border: 1px solid #CBD5E1 !important;
            color: #0F172A !important;
        }
        
        /* Buttons */
        .stButton button {
            background-color: #0F172A !important;
            color: #FFFFFF !important;
            border-radius: 8px !important;
            border: none !important;
            font-weight: 600 !important;
            transition: all 0.2s ease !important;
        }
        
        .stButton button:hover {
            background-color: #1E293B !important;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.2) !important;
            transform: translateY(-1px);
        }
        
        /* Radio Buttons (Pills) */
        div[role="radiogroup"] label {
            background-color: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 20px !important;
            padding: 0.5rem 1rem !important;
            transition: all 0.2s !important;
        }
        
        div[role="radiogroup"] label[data-checked="true"] {
            background-color: #0F172A !important;
            color: #FFFFFF !important;
            border-color: #0F172A !important;
        }

        /* -------------------------------------------------------------------------- */
        /*                                 LAYOUT                                     */
        /* -------------------------------------------------------------------------- */
        
        /* Headings */
        h1, h2, h3 {
            color: #0F172A !important;
            font-weight: 600 !important;
            letter-spacing: -0.5px !important;
        }
        
        h3 {
            font-size: 1.25rem !important;
            margin-bottom: 1.5rem !important;
        }
        
        /* Total Card Special Styling */
        .total-card {
            background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
            border: 1px solid #E2E8F0;
            border-left: 4px solid #09124F; /* New Dark Blue Accent */
            border-radius: 12px;
            padding: 0.75rem; /* Reduced padding */
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
            display: flex;
            flex-direction: column; /* Stack vertically */
            justify-content: center;
            align-items: center;
            margin: 0 0 0.5rem 0; /* Removed top margin */
            width: 100%; /* Full Width */
        }
        
        .total-label {
            font-size: 0.75rem; /* Reduced size */
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
            margin-top: 0.25rem;
        }
        
        .total-value {
            font-size: 1.5rem; /* Reduced size */
            color: #09124F; /* New Dark Blue */
            font-weight: 600; /* Bolder */
            font-family: 'Montserrat', sans-serif;
            line-height: 1.2;
        }
        
        /* Responsive Adjustments (Keeping existing logic but refining) */
        @media (max-width: 768px) {
            .block-container {
                padding: 1rem !important;
            }
            h3 {
                font-size: 1.1rem !important;
            }
        }
    </style>
    """

def get_login_styles():
    return """
        <style>
        .login-container {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 60vh;
        }
        .login-box {
            background-color: #FFFFFF;
            padding: 3rem 2rem;
            border-radius: 12px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
            max-width: 400px;
            width: 100%;
            border: 1px solid #E2E8F0;
        }
        .login-title {
            text-align: center;
            font-family: 'Montserrat', sans-serif;
            color: #0F172A;
            margin-bottom: 1.5rem;
        }
        .stTextInput input {
            background-color: #F8FAFC !important;
            border: 1px solid #E2E8F0 !important;
            color: #0F172A !important;
        }
        .stTextInput input:focus {
            border-color: #0F172A !important;
            box-shadow: none !important;
        }
        </style>
    """

def get_header_styles():
    return """
        <style>
        /* Center the middle column content */
        div[data-testid="column"]:nth-of-type(2) {
            text-align: center;
        }
        /* Right align the right column content */
        div[data-testid="column"]:nth-of-type(3) {
            text-align: right;
        }
        </style>
    """
