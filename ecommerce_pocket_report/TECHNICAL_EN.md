# GWM Pocket Report - Technical Documentation

## Introduction
This guide explains **how to run** the dashboard and **how it was built**. It is written for users with **zero** programming experience.

## Part 1: How it Works (The "Secret Sauce")
Before running it, here is how the magic happens:
1.  **The Engine (Python)**: The programming language that runs the logic.
2.  **The Interface (Streamlit)**: A library that turns Python code into a website. We didn't write HTML/CSS from scratch; Streamlit does the heavy lifting.
3.  **The Data (ClickHouse)**: The dashboard **does not** store data. It connects to a remote database (ClickHouse) to fetch live sales numbers.
4.  **The Visuals (Plotly)**: A tool used to draw the interactive charts and maps.

**The Flow:**
`Your Computer` -> `Requests Data` -> `Database (Remote)` -> `Returns Numbers` -> `Dashboard Draws Charts`

---

## Part 2: Installation Guide (Step-by-Step)

### Step 1: Install Python
1.  Go to [python.org](https://www.python.org/downloads/) and download the latest version.
2.  **CRITICAL**: When installing, check the box **"Add Python to PATH"** at the bottom of the installer window. If you miss this, the commands won't work!

### Step 2: Get the Code
1.  Download this project folder (e.g., "Download ZIP" and extract it).
2.  Open the folder. You should see files like `app.py` and `requirements.txt`.

### Step 3: Open the "Command Center"
We need to use a text interface to talk to the computer.
1.  **Windows**: Press `Start`, type `PowerShell`, and open it.
2.  **Mac**: Press `Cmd + Space`, type `Terminal`, and open it.
3.  Type `cd` (space) and drag the project folder into the terminal window. It will look like:
    ```bash
    cd C:\Users\YourName\Downloads\retencao
    ```
4.  Press **Enter**.

### Step 4: Install the "Tools" (Libraries)
We need to download the tools (Streamlit, Plotly, etc.) that the project uses.
Type this command and press **Enter**:
```bash
pip install -r requirements.txt
```
*You will see a lot of text scrolling. This is normal. Wait for it to stop.*

### Step 5: Run the Dashboard
Type this command and press **Enter**:
```bash
streamlit run app.py
```
A new tab will open in your internet browser with the dashboard!

---

## Part 3: Under the Hood (For Curious Minds)
If you want to understand the code structure:
-   **`app.py`**: The "Manager". It decides what to show on the screen (Charts, Tables, Filters).
-   **`database.py`**: The "Messenger". It contains the **SQL Queries** (instructions) sent to the database to get specific numbers (e.g., "Select all sales from yesterday").
-   **`styles.py`**: The "Stylist". It contains CSS code to make the dashboard look "Luxury" (fonts, colors, spacing).

## Troubleshooting
-   **"Failed to connect to database"**:
    -   Since the database is remote, you might need to be on the company **VPN** or office network.
    -   The dashboard cannot work offline.
-   **"Command not found"**:
    -   You likely forgot to check **"Add Python to PATH"** during installation. Reinstall Python and check that box.
