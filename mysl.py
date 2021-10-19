import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import pydeck as pdk

# SETTING PAGE CONFIG TO WIDE MODE
st.set_page_config(layout="wide")

#Title
st.title('Origin-Destination extracted from iTIC data')
st.header('Pun Jandaeng')

# LAYING OUT THE TOP SECTION OF THE APP
row1_1, row1_2 = st.columns((2,3))
with row1_1:
    st.write('Select a date in January 2019')
    selected_date = st.slider('Date', 0, 4, 0, 1)

with row1_2:
    hour_selected = st.slider("Select Time (hour)", 0, 23, 0, 1)


@st.cache(allow_output_mutation=True)
def load_data(date):
###  https://github.com/Maplub/odsample/blob/master/20190102.csv?raw=true
    url = "https://github.com/Maplub/odsample/blob/master/2019010" + str(date) + ".csv?raw=true"
    df = pd.read_csv(url, header = 0)
    lowercase = lambda x: str(x).lower()
    df.rename(lowercase, axis="columns", inplace=True)
    df.drop(['unnamed: 0'], axis=1)
    #df[DATE_TIME] = pd.to_datetime(df[DATE_TIME])
    return df
df = load_data(selected_date)
data = df


###################
# CREATING FUNCTION FOR MAPS
def mapl(data, lat, lon, zoom):
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

def mapr(data, lat, lon, zoom):
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
###########3#######
# FILTERING DATA BY HOUR SELECTED
#DATE_TIME = "date/time"
#t_start = "timestart"
#t_stop = "timestop"
#data = df[df[DATE_TIME].dt.hour == hour_selected]
data['timestart'] = pd.to_datetime(data['timestart'])
data['timestop'] = pd.to_datetime(data['timestop'])

# LAYING OUT THE TOP SECTION OF THE APP
t_start = "timestart"
t_stop = "timestop"
data1 = data[data[t_start].dt.hour <= hour_selected+1]
data2 = data[data[t_stop].dt.hour <= hour_selected+1]
midpoint1 = (np.average(data1["latstartl"]), np.average(data1["lonstartl"]))
midpoint2 = (np.average(data2["latstop"]), np.average(data2["lonstop"]))


row2_1, row2_2= st.columns((1,1))
with row2_1:
    st.write('**Origin Dataframe** of Selected Date (',str(selected_date),'/1/2019) : **Start**')#str(selected_date)
    dd1 = data1[['latstartl', 'lonstartl','timestart']]
    st.dataframe(dd1)

with row2_2:
    st.write('**Destination Dataframe** of Selected Date (',str(selected_date),'/1/2019) : **Stop**')#str(selected_date)
    dd2 = data2[['latstop','lonstop','timestop']]
    st.dataframe(dd2)

row3_1, row3_2= st.columns((1,1))
with row3_1:
    st.write("**Origin location from %i:00 to %i:00**" % (hour_selected, (hour_selected+3) % 24))
    mapl(dd1, midpoint1[0], midpoint1[1], 11)

with row3_2:
    st.write("**Destination location from %i:00 to %i:00**" % (hour_selected, (hour_selected+3) % 24))
    mapr(dd2, midpoint2[0], midpoint2[1], 11)


# FILTERING DATA FOR THE HISTOGRAM #START
filtered = data[
    (data[t_start].dt.hour >= hour_selected) & (data[t_start].dt.hour < (hour_selected + 3))
    ]

hist = np.histogram(filtered[t_start].dt.minute, bins=60, range=(0, 60))[0]

chart_data = pd.DataFrame({"minute": range(60), "volume": hist})

# FILTERING DATA FOR THE HISTOGRAM #STOP
filtered = data[
    (data[t_stop].dt.hour >= hour_selected) & (data[t_stop].dt.hour < (hour_selected + 1))
    ]

hist = np.histogram(filtered[t_stop].dt.minute, bins=60, range=(0, 60))[0]

chart_data = pd.DataFrame({"minute": range(60), "volume": hist})

# LAYING OUT THE HISTOGRAM SECTION

st.write("")

st.write("**Breakdown of coordinate per minute between %i:00 to %i:00**" % (hour_selected, (hour_selected + 1) % 24))

st.altair_chart(alt.Chart(chart_data)
    .mark_area(
        interpolate='step-after',
    ).encode(
        x=alt.X("minute:Q", scale=alt.Scale(nice=False)),
        y=alt.Y("volume:Q"),
        tooltip=['minute', 'volume']
    ).configure_mark(
        opacity=0.5,
        color='red'
    ), use_container_width=True)
