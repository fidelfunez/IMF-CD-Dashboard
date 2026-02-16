"""
IMF & World Bank Economic Data Fetcher
Fetches economic indicators from IMF and World Bank APIs
and exports to PowerBI-ready CSV files.

Author: Fidel Fúnez C.
Date: 2026-01-27
"""

import requests
import pandas as pd
import json
import time
from typing import Dict, List, Optional
from datetime import datetime
import os

# ============================================================================
# CONFIGURATION
# ============================================================================

# IMF DataMapper API base URL (NO API KEY REQUIRED)
IMF_BASE_URL = "https://www.imf.org/external/datamapper/api/v1"

# World Bank API base URL (NO API KEY REQUIRED)
WB_BASE_URL = "https://api.worldbank.org/v2"

# Time period for data extraction
START_YEAR = 2018
END_YEAR = 2024

# 25 Countries with regions
COUNTRIES = {
    # Latin America
    "BRA": {"name": "Brazil", "region": "Latin America"},
    "MEX": {"name": "Mexico", "region": "Latin America"},
    "ARG": {"name": "Argentina", "region": "Latin America"},
    "COL": {"name": "Colombia", "region": "Latin America"},
    "CHL": {"name": "Chile", "region": "Latin America"},
    "PER": {"name": "Peru", "region": "Latin America"},
    
    # Africa
    "ZAF": {"name": "South Africa", "region": "Africa"},
    "NGA": {"name": "Nigeria", "region": "Africa"},
    "KEN": {"name": "Kenya", "region": "Africa"},
    "EGY": {"name": "Egypt", "region": "Africa"},
    "GHA": {"name": "Ghana", "region": "Africa"},
    "ETH": {"name": "Ethiopia", "region": "Africa"},
    
    # Asia
    "IND": {"name": "India", "region": "Asia"},
    "IDN": {"name": "Indonesia", "region": "Asia"},
    "PHL": {"name": "Philippines", "region": "Asia"},
    "VNM": {"name": "Vietnam", "region": "Asia"},
    "BGD": {"name": "Bangladesh", "region": "Asia"},
    "THA": {"name": "Thailand", "region": "Asia"},
    "MYS": {"name": "Malaysia", "region": "Asia"},
    
    # Europe
    "POL": {"name": "Poland", "region": "Europe"},
    "ROU": {"name": "Romania", "region": "Europe"},
    "TUR": {"name": "Turkey", "region": "Europe"},
    "UKR": {"name": "Ukraine", "region": "Europe"},
    
    # Middle East
    "JOR": {"name": "Jordan", "region": "Middle East"},
    "LBN": {"name": "Lebanon", "region": "Middle East"},
}

# IMF Indicator Codes (DataMapper API format)
IMF_INDICATORS = {
    "NGDP_RPCH": {
        "name": "GDP Growth Rate (Annual %)",
        "description": "Real GDP growth rate, annual percentage change"
    },
    "PCPIPCH": {
        "name": "Inflation Rate (CPI)",
        "description": "Consumer Price Index, annual percentage change"
    },
    "GGXWDG_NGDP": {
        "name": "Government Debt (% of GDP)",
        "description": "General government gross debt as percentage of GDP"
    },
    "GGXCNL_NGDP": {
        "name": "Fiscal Balance (% of GDP)",
        "description": "General government net lending/borrowing as percentage of GDP"
    },
    "GGR_NGDP": {
        "name": "Government Revenue (% of GDP)",
        "description": "General government revenue as percentage of GDP"
    },
    "GGX_NGDP": {
        "name": "Government Expenditure (% of GDP)",
        "description": "General government total expenditure as percentage of GDP"
    },
    "BCA_NGDPD": {
        "name": "Current Account Balance (% of GDP)",
        "description": "Current account balance as percentage of GDP"
    },
    "LUR": {
        "name": "Unemployment Rate",
        "description": "Unemployment rate, percent"
    }
}

# World Bank Indicator Codes
WB_INDICATORS = {
    "SE.XPD.TOTL.GD.ZS": {
        "name": "Education Expenditure (% of GDP)",
        "description": "Government expenditure on education, total (% of GDP)"
    },
    "IS.RRS.TOTL.KM": {
        "name": "Railway Infrastructure",
        "description": "Railways, total (route-km)"
    },
    "SP.POP.TOTL": {
        "name": "Population",
        "description": "Population, total"
    },
    "NY.GNP.PCAP.CD": {
        "name": "GNI per Capita",
        "description": "GNI per capita, Atlas method (current US$)"
    },
    "IE.PPI.ENGY.CD": {
        "name": "Infrastructure Investment (Energy)",
        "description": "Investment in energy with private participation (current US$)"
    }
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def make_request(url: str, params: Optional[Dict] = None, max_retries: int = 3) -> Optional[Dict]:
    """
    Make HTTP request with error handling and retry logic.
    
    Args:
        url: API endpoint URL
        params: Query parameters
        max_retries: Maximum number of retry attempts
        
    Returns:
        JSON response as dictionary, or None if request fails
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f" Request failed (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                print(f" Failed to fetch data from {url}")
                return None
    return None


def get_imf_data(indicator_code: str, country_codes: List[str]) -> List[Dict]:
    """
    Fetch data from IMF DataMapper API for a specific indicator and countries.
    
    Args:
        indicator_code: IMF indicator code (e.g., 'NGDP_RPCH')
        country_codes: List of ISO 3-letter country codes
        
    Returns:
        List of dictionaries with country, year, and value data
    """
    data_points = []
    
    # Build URL with countries and time period
    countries_str = ",".join(country_codes)
    periods = ",".join([str(year) for year in range(START_YEAR, END_YEAR + 1)])
    url = f"{IMF_BASE_URL}/{indicator_code}/{countries_str}"
    params = {"periods": periods}
    
    print(f"  Fetching {IMF_INDICATORS[indicator_code]['name']}...")
    
    response = make_request(url, params)
    
    if not response:
        return data_points
    
    # Parse IMF DataMapper API response structure
    # Structure: response["values"][indicator_code][country_code][year] = value
    try:
        if "values" in response and indicator_code in response["values"]:
            indicator_data = response["values"][indicator_code]
            
            for country_code in country_codes:
                if country_code in indicator_data:
                    country_data = indicator_data[country_code]
                    
                    # Extract time series data (country_data is a dict of year: value)
                    for year_str, value in country_data.items():
                        try:
                            year = int(year_str)
                            if START_YEAR <= year <= END_YEAR and value is not None:
                                data_points.append({
                                    "Country_Code": country_code,
                                    "Country": COUNTRIES[country_code]["name"],
                                    "Region": COUNTRIES[country_code]["region"],
                                    "Year": year,
                                    "Indicator_Name": IMF_INDICATORS[indicator_code]["name"],
                                    "Indicator_Code": indicator_code,
                                    "Value": float(value) if value != "" else None,
                                    "Source": "IMF"
                                })
                        except (ValueError, TypeError):
                            continue
    except (KeyError, TypeError) as e:
        print(f"  Error parsing IMF response: {e}")
    
    return data_points


def get_world_bank_data(indicator_code: str, country_codes: List[str]) -> List[Dict]:
    """
    Fetch data from World Bank API for a specific indicator and countries.
    
    Args:
        indicator_code: World Bank indicator code
        country_codes: List of ISO 3-letter country codes
        
    Returns:
        List of dictionaries with country, year, and value data
    """
    data_points = []
    
    # World Bank API uses ISO 3-letter codes
    countries_str = ";".join(country_codes)
    
    url = f"{WB_BASE_URL}/country/{countries_str}/indicator/{indicator_code}"
    params = {
        "format": "json",
        "date": f"{START_YEAR}:{END_YEAR}",
        "per_page": 10000  # Large number to get all results
    }
    
    print(f"  Fetching {WB_INDICATORS[indicator_code]['name']}...")
    
    response = make_request(url, params)
    
    if not response or not isinstance(response, list) or len(response) < 2:
        return data_points
    
    # World Bank API returns [metadata, data] structure
    data = response[1] if len(response) > 1 else []
    
    for record in data:
        try:
            country_code = record.get("countryiso3code", "")
            if country_code in COUNTRIES:
                year = record.get("date", "")
                value = record.get("value")
                
                if year and value is not None:
                    try:
                        year_int = int(year)
                        if START_YEAR <= year_int <= END_YEAR:
                            data_points.append({
                                "Country_Code": country_code,
                                "Country": COUNTRIES[country_code]["name"],
                                "Region": COUNTRIES[country_code]["region"],
                                "Year": year_int,
                                "Indicator_Name": WB_INDICATORS[indicator_code]["name"],
                                "Indicator_Code": indicator_code,
                                "Value": float(value),
                                "Source": "World Bank"
                            })
                    except (ValueError, TypeError):
                        continue
        except (KeyError, TypeError):
            continue
    
    return data_points


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and standardize the dataframe.
    
    Args:
        df: Raw dataframe with economic data
        
    Returns:
        Cleaned dataframe
    """
    print(" Cleaning data...")
    
    # Remove rows with null values in critical columns
    df_clean = df.dropna(subset=["Country", "Year", "Indicator_Name"])
    
    # Ensure proper data types
    df_clean["Year"] = pd.to_numeric(df_clean["Year"], errors="coerce").astype("Int64")
    df_clean["Value"] = pd.to_numeric(df_clean["Value"], errors="coerce")
    
    # Sort by Country, Year, Indicator_Name for better readability
    df_clean = df_clean.sort_values(["Country", "Year", "Indicator_Name"])
    
    # Reset index
    df_clean = df_clean.reset_index(drop=True)
    
    return df_clean


def export_to_csv(df: pd.DataFrame, filename: str, output_dir: str = "data"):
    """
    Export dataframe to CSV file.
    
    Args:
        df: Dataframe to export
        filename: Output filename
        output_dir: Output directory
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    filepath = os.path.join(output_dir, filename)
    df.to_csv(filepath, index=False, encoding="utf-8")
    print(f"  Exported: {filepath} ({len(df)} rows)")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Main function to orchestrate data fetching and export.
    """
    print("=" * 70)
    print("IMF & World Bank Economic Data Fetcher")
    print("=" * 70)
    print(f"Countries: {len(COUNTRIES)}")
    print(f"Time Period: {START_YEAR}-{END_YEAR}")
    print(f"IMF Indicators: {len(IMF_INDICATORS)}")
    print(f"World Bank Indicators: {len(WB_INDICATORS)}")
    print("=" * 70)
    print()
    
    all_data = []
    country_codes = list(COUNTRIES.keys())
    
    # Fetch IMF data
    print("Fetching data from IMF API...")
    print("-" * 70)
    for indicator_code in IMF_INDICATORS.keys():
        imf_data = get_imf_data(indicator_code, country_codes)
        all_data.extend(imf_data)
        time.sleep(1)  # Rate limiting - be respectful to the API
    print()
    
    # Fetch World Bank data
    print("Fetching data from World Bank API...")
    print("-" * 70)
    for indicator_code in WB_INDICATORS.keys():
        wb_data = get_world_bank_data(indicator_code, country_codes)
        all_data.extend(wb_data)
        time.sleep(1)  # Rate limiting
    print()
    
    # Convert to DataFrame
    print("Processing data...")
    df = pd.DataFrame(all_data)
    
    if df.empty:
        print("❌ No data retrieved. Please check your API connections and country codes.")
        return
    
    print(f"  Total records retrieved: {len(df)}")
    
    # Clean data
    df_clean = clean_data(df)
    print(f"  Records after cleaning: {len(df_clean)}")
    print()
    
    # Export master CSV
    print("Exporting CSV files...")
    print("-" * 70)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Master CSV with all indicators
    master_filename = f"economic_data_master_{timestamp}.csv"
    export_to_csv(df_clean, master_filename)
    
    # Separate CSV files by source
    imf_df = df_clean[df_clean["Source"] == "IMF"]
    wb_df = df_clean[df_clean["Source"] == "World Bank"]
    
    if not imf_df.empty:
        export_to_csv(imf_df, f"imf_data_{timestamp}.csv")
    
    if not wb_df.empty:
        export_to_csv(wb_df, f"world_bank_data_{timestamp}.csv")
    
    # Summary statistics
    print()
    print("=" * 70)
    print("Summary Statistics")
    print("=" * 70)
    print(f"Total Countries: {df_clean['Country'].nunique()}")
    print(f"Total Indicators: {df_clean['Indicator_Name'].nunique()}")
    print(f"Year Range: {df_clean['Year'].min()} - {df_clean['Year'].max()}")
    print(f"Total Data Points: {len(df_clean)}")
    print(f"Missing Values: {df_clean['Value'].isna().sum()}")
    print()
    print("Data extraction complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
