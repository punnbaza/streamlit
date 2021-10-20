import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import pydeck as pdk
#layout
st.set_page_config(layout="wide")
st.title('Origin-Destination extracted from iTIC data')
st.header('Pun Jandaeng')
st.write('source data :',"https://github.com/Maplub/odsample")

row1_1, row1_2 = st.columns((2,3))
with row1_1:
  day=st.slider('Select date in January',1,5)
with row1_2:
  hour=st.slider('Select hour in date ',0,23)  

##load data
@st.cache(allow_output_mutation=True)
def load_data(day):
  url="https://github.com/Maplub/odsample/blob/master/2019010" + str(day) + ".csv?raw=true"
  df = pd.read_csv(url, header = 0)
  lowercase = lambda x: str(x).lower()
  df.rename(lowercase, axis="columns", inplace=True)
  df.drop(['unnamed: 0'], axis=1)
  return df
df=load_data(day)
data=df
##map 
def map_str(data, lat, lon, zoom):
    st.write(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state={
            "latitude": lat,
            "longitude": lon,
            "zoom": zoom,
            "pitch": 50,
        },
        layers=[
            pdk.Layer(
                "HexagonLayer",
                data=data,
                get_position=["lonstartl", "latstartl"],
                radius=100,
                elevation_scale=4,
                elevation_range=[0, 1000],
                pickable=True,
                extruded=True,
            ),
        ]
    ))
def map_stp(data, lat, lon, zoom):
    st.write(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state={
            "latitude": lat,
            "longitude": lon,
            "zoom": zoom,
            "pitch": 50,
        },
        layers=[
            pdk.Layer(
                "HexagonLayer",
                data=data,
                get_position=["lonstop", "latstop"],
                radius=100,
                elevation_scale=4,
                elevation_range=[0, 1000],
                pickable=True,
                extruded=True,
            ),
        ]
    ))
data['timestart'] = pd.to_datetime(data['timestart'])
data['timestop'] = pd.to_datetime(data['timestop'])

data_str = data[data["timestart"].dt.hour <= hour+1]
data_stp = data[data["timestop"].dt.hour <= hour+1]

org_str = (np.average(data_str["latstartl"]), np.average(data_str["lonstartl"]))
org_stp = (np.average(data_stp["latstop"]), np.average(data_stp["lonstop"]))


row2_1, row2_2= st.columns((1,2))
with row2_1:
  st.header('Origin')
  st.write('data frame at'+str(day)+' January 2019')
  d1=data_str[['latstartl', 'lonstartl','timestart']]
  st.dataframe(d1)
with row2_2:
  st.header("     ")
  st.header("     ")
  st.write(' At',str(hour)+":00 to" ,str((hour+1) % 24)+":00")
  map_str(d1, org_str[0], org_str[1], 10)

row3_1, row3_2= st.columns((1,2))
with row3_1:
  st.header('Destination')
  st.write('data frame at'+str(day)+' January 2019')
  d2=data_str[['latstop','lonstop','timestop']]
  st.dataframe(d2)
with row3_2:
  st.header("     ")
  st.header("     ")
  st.write(' At',str(hour)+":00 to" ,str((hour+1) %24)+":00")
  map_stp(d2, org_stp[0], org_stp[1], 12)
  

#filter data
filtered = data[
    (data["timestop"].dt.hour >= hour) & (data["timestop"].dt.hour < (hour + 3))
    ]
#histogram

hist = np.histogram(filtered["timestop"].dt.minute, bins=60, range=(0, 60))[0]

chart_data = pd.DataFrame({"minute": range(60), "pickups": hist})

# LAYING OUT THE HISTOGRAM SECTION

st.write("")

st.write("**Breakdown of rides per minute between %i:00 to %i:00**" % (hour, (hour + 1) % 24))

st.altair_chart(alt.Chart(chart_data)
    .mark_area(
        interpolate='step-after',
    ).encode(
        x=alt.X("minute:Q", scale=alt.Scale(nice=False)),
        y=alt.Y("pickups:Q"),
        tooltip=['minute', 'pickups']
    ).configure_mark(
        opacity=0.5,
        color='red'
    ), use_container_width=True)
