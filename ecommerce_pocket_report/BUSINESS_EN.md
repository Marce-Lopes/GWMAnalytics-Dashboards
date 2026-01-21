# GWM Pocket Report - Business Logic Documentation

## Overview
This dashboard provides a real-time snapshot of sales performance for GWM vehicles (H6, ORA, etc.). It is designed for mobile use ("Pocket Report") and tracks key performance indicators (KPIs) like paid orders, unpaid orders, and recent activity.

## Data Sources
- **Database**: ClickHouse (`mart.ecommerce_pocket_report`)
- **Update Frequency**: Real-time (Direct database query)

## Key Metrics Definitions

### 1. 9k Form With Payment (Paid)
- **Definition**: Confirmed orders where payment has been processed.
- **Filter**: `Status = 'Invoiced'`
- **Time Scope**:
    - **Current Month**: All invoiced orders up to yesterday (`Date < Today - 1`).
    - **Past Months**: All invoiced orders in that month.

### 2. 9k Form Without Payment (Unpaid)
- **Definition**: Orders that are open or not yet invoiced.
- **Filter**: `Status` is either `'Not Invoiced'` or `'Open'`.
- **Time Scope**:
    - **Current Month**: All open/not invoiced orders up to yesterday (`Date < Today - 1`).
    - **Past Months**: All open/not invoiced orders in that month.

### 3. Last 24 Hours (Recent Activity)
- **Definition**: All orders placed since yesterday. This captures the most recent market activity.
- **Filter**: `Date >= Today - 1`
- **Note**: This metric includes *all* statuses to show total recent inflow.
- **Display**: Shown separately in the summary and merged into charts for the current month.

### 4. Total
- **Definition**: The sum of Paid + Unpaid + Last 24h (for the current month view).

## Dimensions & Breakdown
The dashboard breaks down these metrics by:
- **Vehicle Family**: Specific models (e.g., H6 HEV2, H6 GT).
- **Exterior Color**: Distribution of sales by car color.
- **Daily Evolution**: Trend line of orders over the month.
- **Dealer State**: Geographic distribution of sales.
- **Dealer Group**: Performance by dealer network groups.

## Comparison Analysis
- Allows comparing daily trends between different vehicles or months.
- Supports filtering by "With Payment", "Without Payment", or "Total".
