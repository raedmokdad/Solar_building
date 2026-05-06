import streamlit as st
import requests
import pandas as pd
import os

# -------------------------
# SESSION STATE INIT
# -------------------------
if "password_correct" not in st.session_state:
    st.session_state.password_correct = False

if "login_attempted" not in st.session_state:
    st.session_state.login_attempted = False


# -------------------------
# LOGIN FUNCTION
# -------------------------
def check_password():

    def password_entered():
        st.session_state.login_attempted = True  # 🔥 user tried login

        if st.session_state["password"] == os.getenv("APP_PASSWORD"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    # already logged in → skip login UI
    if st.session_state.password_correct:
        return True

    # -------------------------
    # LOGIN UI
    # -------------------------
    st.markdown("## 🔐 Secure Access")

    st.text_input(
        "Password",
        type="password",
        on_change=password_entered,
        key="password",
    )

    # 🔥 show error ONLY after first attempt
    if st.session_state.login_attempted and not st.session_state.password_correct:
        st.error("❌ Incorrect password")

    return False


# -------------------------
# AUTH CHECK FIRST
# -------------------------
if not check_password():
    st.stop()


# -------------------------
# AFTER LOGIN → APP
# -------------------------
st.set_page_config(page_title="Solar Finder", layout="wide")

API_URL = "http://65.108.42.157:8000/buildings/filter"



st.title("☀️ Solar Building Finder")

with st.expander("ℹ️ Filter Explanation"):
    st.markdown("""
    ### 🔍 Filter Guide
    
    Use the filters in the sidebar to find the most suitable buildings for solar installation.
    
    #### ⚡ Power & Size
    - **kWp (kilowatt peak)**: Installed solar capacity of the building  
      → Higher = more solar panels / higher production  
    - **Building Area (m²)**: Roof size  
      → Larger roofs = more installation space  
    
    #### 🌞 Solar Performance
    - **Radiation (kWh/m²/year)**: Solar energy received  
      → Higher = better sunlight conditions  
    - **Annual Yield (kWh/year)**: Estimated yearly electricity production  
      → Based on installed capacity and efficiency  
    
    #### 📐 Roof Characteristics
    - **Tilt (°)**: Roof angle  
      → Optimal: 25°–40°  
      → Flat roofs (0°–10°) are also acceptable  
    - **Optimal Tilt (Auto Mode)**:  
      → If enabled, system automatically selects best tilt ranges  
      → If disabled, you can manually set min/max tilt  
    
    - **Orientation (South/West)**:  
      → South-facing roofs are best  
      → West is also acceptable  
    
    #### ⚡ Grid Connection
    - **Distance to Transformer (m)**:  
      → Shorter distance = easier and cheaper connection  
    - **Require Transformer**:  
      → Only include buildings with known grid access  
    
    #### 🏭 Land Use
    - **Land Use Type**:  
      → Commercial / Industrial buildings are prioritized  
      → Typically larger and more suitable for solar  
    
    #### 🎯 Tip
    Combine filters carefully:
    - Start broad → then narrow down
    - Too many strict filters = no results
    """)

# -------------------------
# SIDEBAR
# -------------------------
st.sidebar.header("Filters")

limit = st.sidebar.number_input(
    "Max Results",
    min_value=1,
    max_value=1000000,
    value=1000,
    step=100
)


city = st.sidebar.selectbox("City", ["dortmund", "bochum", "duesseldorf", "essen", "koeln"])

kwp_min = st.sidebar.number_input("Min kWp", value=50)
kwp_max = st.sidebar.number_input("Max kWp", value=1000)

# 🔥 Optimal tilt checkbox FIRST
optimal_tilt = st.sidebar.checkbox("Optimal Tilt (25–40° or flat)", True)

# 🔥 Tilt inputs (disabled when optimal_tilt = True)
tilt_min = st.sidebar.number_input(
    "Tilt Min (°)",
    value=0,
    disabled=optimal_tilt
)

tilt_max = st.sidebar.number_input(
    "Tilt Max (°)",
    value=50,
    disabled=optimal_tilt
)

# UX hint
if optimal_tilt:
    st.sidebar.info("Using optimal tilt automatically")

area_min = st.sidebar.number_input("Min Area", value=500)
area_max = st.sidebar.number_input("Max Area", value=5000)

distance_max = st.sidebar.number_input("Max Distance", value=500)

radiation_min = st.sidebar.number_input("Min Radiation", value=1000)
min_yield = st.sidebar.number_input("Min Yield", value=45000)

landuse = st.sidebar.multiselect(
    "Landuse",
    ["residential", "commercial", "industrial"],
    default=["commercial", "industrial"]
)

require_transformer = st.sidebar.checkbox("Require Transformer", True)
roof_orientation = st.sidebar.checkbox("South/West", True)

# -------------------------
# MAIN AREA
# -------------------------
st.info("👉 Select filters and click Search")

search = st.button("🔍 Search")

if search:

    # 🔥 IMPORTANT: avoid sending tilt when optimal_tilt is True
    payload = {
        "limit": limit,
        "city": city,
        "kwp_min": kwp_min,
        "kwp_max": kwp_max,
        "tilt_min": None if optimal_tilt else tilt_min,
        "tilt_max": None if optimal_tilt else tilt_max,
        "area_min": area_min,
        "area_max": area_max,
        "distance_max": distance_max,
        "radiation_min": radiation_min,
        "min_yield": min_yield,
        "landuse": landuse,
        "require_transformer": require_transformer,
        "roof_orientation": roof_orientation,
        "optimal_tilt": optimal_tilt
    }

    with st.spinner("Calling API..."):
        try:
            response = requests.post(API_URL, json=payload, timeout=120)

            if response.status_code != 200:
                st.error(f"API error: {response.text}")
            else:
                result = response.json()

                if not result.get("success", True):
                    st.error(result.get("error", "Unknown error"))
                elif result.get("count", 0) == 0:
                    st.warning("No results found")
                else:
                    df = pd.DataFrame(result["data"])

                    st.success(f"{result['count']} buildings found")

                    # Optional: limit columns display
                    st.dataframe(df)

        except requests.exceptions.Timeout:
            st.error("Request timed out. API is slow or unreachable.")

        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to API. Check server IP and port.")

        except Exception as e:
            st.error(f"Unexpected error: {e}")
