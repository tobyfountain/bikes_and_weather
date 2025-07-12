import requests, streamlit as st

# ---------- configuration ----------
TFL_DOCKS = ["BikePoints_537", "BikePoints_206"]       # primary, fallback
LAT, LON   = 51.51793, -0.067937                      # fixed weather location
TFL_URL    = "https://api.tfl.gov.uk/BikePoint/{}"
WX_URL     = "https://api.open-meteo.com/v1/forecast"
# -----------------------------------

@st.cache_data(ttl=60)
def bike_status(dock_id: str):
    j = requests.get(TFL_URL.format(dock_id), timeout=5).json()
    name  = j["commonName"]
    props = {p["key"]: p["value"] for p in j["additionalProperties"]}
    pedal     = int(props.get("NbStandardBikes", 0))
    electric  = int(props.get("NbEBikes", 0))
    return name, pedal, electric

@st.cache_data(ttl=900)              # cache for 15 min
def weather_today(lat: float, lon: float):
    r = requests.get(
        WX_URL,
        params={
            "latitude": lat,
            "longitude": lon,
            "daily": (
                "precipitation_probability_max,"
                "temperature_2m_min,temperature_2m_max"
            ),
            "forecast_days": 1,
            "timezone": "Europe/London",
        },
        timeout=5,
    ).json()
    d = r["daily"]
    rain  = int(d["precipitation_probability_max"][0])        # %
    t_min = round(d["temperature_2m_min"][0])
    t_max = round(d["temperature_2m_max"][0])
    return rain, t_min, t_max

# ------------- UI -------------
st.title("Nearest bike and weather")

# bikes: use fallback dock if primary empty
name, pedal, electric = bike_status(TFL_DOCKS[0])
if pedal + electric == 0:
    name, pedal, electric = bike_status(TFL_DOCKS[1])

rain, t_min, t_max = weather_today(LAT, LON)

st.subheader(f"Dock: {name}")
st.write(f"{pedal} pedal, {electric} electric")

cols = st.columns(2)
cols[0].metric("Chance of rain", f"{rain}%")
cols[1].metric("Temp range", f"{t_min} – {t_max} °C")
