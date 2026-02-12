import pandas as pd
import streamlit as st
import psycopg2 
import seaborn as sns
import json
import plotly.express as px
import matplotlib.pyplot as plt

db_config = psycopg2.connect(
    host="localhost",
    database="phonepe",
    user="postgres",
    password="root"
)

st.set_page_config(page_title="Phonepe", layout="wide")
st.sidebar.title("NAVIGATION")

if "page" not in st.session_state:
    st.session_state.page = "Home"

if st.sidebar.button("Home", use_container_width=True):
    st.session_state.page = "Home"

if st.sidebar.button("Insights", use_container_width=True):
    st.session_state.page = "Insights"

if st.session_state.page == "Home":

    
    col1a,col1b,col1c=st.columns(3)
    with col1a:
            selected_type=st.selectbox("Choose Type",("Transaction","User"),label_visibility="collapsed")
            if selected_type=="User":
                type="map_user"
            if selected_type=="Transaction":
                type="map_transaction"
    with col1b:
            selected_quarter=st.selectbox("Choose Quarter",("Q1","Q2","Q3","Q4"),label_visibility="collapsed")
            quat=selected_quarter.replace("Q","")
    with col1c:
            selected_year=st.selectbox("Choose Type",("2018","2019","2020","2021","2022","2023","2024"),label_visibility="collapsed")

    # ---------------- LOAD WORLD STATES GEOJSON ----------------
    col_map,col_data=st.columns([3,1.5])
    
    with col_map:
            with open("data/india_states.geojson", encoding="utf-8") as f:
                world_states = json.load(f)

            india_geo = {
                "type": "FeatureCollection",
                "features": [f for f in world_states["features"] if f["properties"]["admin"] == "India"]
            }

            query = f"SELECT state, SUM(transaction_amount) AS total_amount FROM aggregated_transaction where year = {selected_year} AND quarter = {quat} GROUP BY state;"
            df_map = pd.read_sql(query, db_config)
            df_map["state"] = df_map["state"].str.replace("-", " ").str.title().str.strip()

            # Fix Names for GeoJSON matching
            name_fixes = {"Andaman & Nicobar Islands": "Andaman and Nicobar", "Jammu & Kashmir": "Jammu and Kashmir"}
            df_map["state"] = df_map["state"].replace(name_fixes)

            fig = px.choropleth_mapbox(
                df_map, geojson=india_geo, locations="state", featureidkey="properties.name",
                color="total_amount", color_continuous_scale="Spectral", mapbox_style="open-street-map",
                zoom=4.2, center={"lat": 23, "lon": 82}, opacity=0.8, hover_name="state"
            )
            fig.update_layout(height=1100, margin={"r":0,"t":0,"l":0,"b":0})

            event = st.plotly_chart(fig, use_container_width=True, on_select="rerun")

            # HANDLE STATE SELECTION
            if event:
                if event["selection"]["points"]:
                    # A state was clicked: Drill down
                    st.session_state.selected_state = event["selection"]["points"][0]["hovertext"]
                    st.session_state.view = 'State'
                    
                else:
                    # Background was clicked (empty selection): Reset to India
                    st.session_state.view = 'India'
                    st.session_state.selected_state = None
                    
                
                

        # 3. RENDER THE DISTRICT VIEW
        
    with col_data:
    # 1. Determine if we are looking at a specific state or All India
        if type=="map_transaction":
            if st.session_state.view == 'State' and st.session_state.selected_state:
                state_query = st.session_state.selected_state.lower().replace(' ', '-')
                queryd = f""" SELECT year, quarter, SUM(amount) AS total_amount, SUM(count) AS total_count 
        FROM {type} 
        WHERE state = '{state_query}' 
        AND year = {selected_year} 
        AND quarter = {quat}
        GROUP BY year, quarter;"""
                title_suffix = f"in {st.session_state.selected_state}"
            else:
                queryd = f"""SELECT year, quarter, SUM(amount) AS total_amount, SUM(count) AS total_count FROM {type}
                WHERE   year = {selected_year} 
        AND quarter = {quat}
        GROUP BY year, quarter;"""
                title_suffix = "Across India"

            df_data = pd.read_sql(queryd, db_config)
            
            # Calculate values safely
            if not df_data.empty:
                total_val = df_data['total_amount'].iloc[0] or 0
                total_cnt = df_data['total_count'].iloc[0] or 1 # Prevent division by zero
                avg_val = total_val / total_cnt
            else:
                total_val=0
                total_cnt=1
                avg_val=0

            # 2. RENDER THE UI
            st.markdown("<h3 style='color:#32E0C4'>Transactions</h3>", unsafe_allow_html=True)
            st.markdown(f"<h5 style='color:#ffffff; margin-bottom:0px;'>All PhonePe transactions</h5>", unsafe_allow_html=True)
            st.markdown(
        f"""
        <h2 style='
            color: #32E0C4; 
            font-size: 30px; 
            padding: 0px; 
            margin: 0px; 
            line-height:1;
        '>
            ₹ {total_val:,.0f}
        </h2>
        """, 
        unsafe_allow_html=True
    )
            st.divider()
            
            

            left, right = st.columns(2)
            with left:
                st.markdown("<h5 style='color:#ffffff;padding: 5px;margin-bottom:10px;'>Total payment value</h5>", unsafe_allow_html=True)
                st.markdown(f"<h5 style='color:#32E0C4;padding: 0px; margin: 0px;'>₹{total_val/10000000 :,.0f} Cr</h5>", unsafe_allow_html=True)
                
            with right:
                st.markdown("<h5 style='color:#ffffff;padding: 5px ;margin-bottom:10px'>Avg. transaction value</h5>", unsafe_allow_html=True)
                st.markdown(f"<h5 style='color:#32E0C4;padding: 0px ;margin: 0px;'>₹{avg_val:,.2f}</h5>", unsafe_allow_html=True)
            st.divider()
            st.markdown("<h3 style='color:#ffffff'>Categories</h3>", unsafe_allow_html=True)
            leftc, rightc = st.columns(2)
            with leftc:
                st.markdown("<p style='color:#ffffff;padding: 2px;margin-bottom:0px;font-weight:600;font-size:20px'>Merchant payments</p>", unsafe_allow_html=True)
                st.markdown("<p style='color:#ffffff;padding: 2px ;margin-bottom:0px;font-weight:600;font-size:20px'>Peer-to-peer payments</p>", unsafe_allow_html=True)
                st.markdown("<p style='color:#ffffff;padding: 2px ;margin-bottom:0px;font-weight:600;font-size:20px'>Recharge & bill payments</p>", unsafe_allow_html=True)
                st.markdown("<p style='color:#ffffff;padding: 2px ;margin-bottom:0px;font-weight:600;font-size:20px'>Financial Services</p>", unsafe_allow_html=True)
                st.markdown("<p style='color:#ffffff;padding: 2px ;margin-bottom:0px;font-weight:600;font-size:20px'>Others</p>", unsafe_allow_html=True)
            with rightc:
                if st.session_state.view == 'State' and st.session_state.selected_state:
                    state_query = st.session_state.selected_state.lower().replace(' ', '-')
                    querytype = f""" SELECT year, quarter, SUM(transaction_amount) AS total_amount,transaction_type
            FROM aggregated_transaction 
            WHERE state = '{state_query}' 
            AND year = {selected_year} 
            AND quarter = {quat}
            GROUP BY year, quarter,transaction_type;"""
                    title_suffix = f"in {st.session_state.selected_state}"
                else:
                    querytype = f"""SELECT year, quarter, SUM(transaction_amount) AS total_amount,transaction_type FROM aggregated_transaction
                    WHERE   year = {selected_year} 
                    AND quarter = {quat}
                    GROUP BY year, quarter,transaction_type;"""
                    title_suffix = "Across India"
                df_type = pd.read_sql(querytype, db_config)
                
                type_data = dict(zip(df_type['transaction_type'], df_type['total_amount']))
                st.markdown(f"<h5 style='color:#32E0C4; padding: 0px; margin-top: 6px;'>₹ {type_data.get('Merchant payments', 0):,.0f}</h5>", unsafe_allow_html=True)
                st.markdown(f"<h5 style='color:#32E0C4; padding: 0px; margin-top: 12px;'>₹ {type_data.get('Peer-to-peer payments', 0):,.0f}</h5>", unsafe_allow_html=True)
                st.markdown(f"<h5 style='color:#32E0C4; padding: 0px; margin-top: 13px;'>₹ {type_data.get('Recharge & bill payments', 0):,.0f}</h5>", unsafe_allow_html=True)
                st.markdown(f"<h5 style='color:#32E0C4; padding: 0px; margin-top: 13px;'>₹ {type_data.get('Financial Services', 0):,.0f}</h5>", unsafe_allow_html=True)
                st.markdown(f"<h5 style='color:#32E0C4; padding: 0px; margin-top: 12px;'>₹ {type_data.get('Others', 0):,.0f}</h5>", unsafe_allow_html=True)
            st.divider()
            
            # --- START TOP 10 DISTRICTS ---
            if st.session_state.view == 'State' and st.session_state.selected_state: 
                state_query = st.session_state.selected_state.lower().replace(' ', '-')
                
                # Fetching the Top 10
                querylast = f"""SELECT district, SUM(amount) AS total_amount
                                FROM map_transaction 
                                WHERE state = '{state_query}' 
                                AND year = {selected_year} 
                                AND quarter = {quat}
                                GROUP BY district
                                ORDER BY total_amount DESC
                                LIMIT 10;"""
                
                df_last = pd.read_sql(querylast, db_config)
                

                if not df_last.empty:
                    st.markdown("<h3 style='color:#ffffff'>Top 10 Districts</h3>", unsafe_allow_html=True)
                    
                    # Create two columns for the list
                    ls, rs = st.columns([2, 1])
                    
                    with ls:
                        for i in range(len(df_last)):
                            re= df_last["district"].str.replace("district","")
                            d_name =re.iloc[i].title()
                            st.markdown(f"<p style='color:#ffffff; font-weight:600; font-size:20px; margin-bottom:0px;'>{i+1}. {d_name}</p>", unsafe_allow_html=True)
                    
                    with rs:
                        for i in range(len(df_last)):
                            d_amt = df_last["total_amount"].iloc[i]/10000000
                            st.markdown(f"<p style='color:#32E0C4; font-weight:600; font-size:20px; margin-bottom:0px;'>₹{d_amt:,.0f} cr</p>", unsafe_allow_html=True)
                else:
                    st.warning("No district data found for this selection.")
            
            else:
                st.markdown("""
    <style>
    /* Styling the container for all tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }

    /* Styling each individual tab (The "Pill") */
    .stTabs [data-baseweb="tab"] {
        height: 35px;
        white-space: pre-wrap;
        background-color: #2b1b3d; /* Dark purple background matching the theme */
        border-radius: 20px; /* Fully rounded corners for the pill look */
        color: #ffffff;
        padding-left: 20px;
        padding-right: 20px;
        margin-bottom:10px;
        border: 1px solid #4d3b5d;
    }

    /* Styling the active tab when selected */
    .stTabs [aria-selected="true"] {
        background-color:#7cfc00!important;
        color: #000000 !important;
        font-weight: bold;
    }
    
    /* Removing the default underline from Streamlit tabs */
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: transparent !important;
    }
    </style>
""", unsafe_allow_html=True)
                t1,t2=st.tabs(["States","Districts"])
                with t1:
                    if st.session_state.view == 'State' and st.session_state.selected_state: 
                        state_query = st.session_state.selected_state.lower().replace(' ', '-')
                        st.markdown("<h3 style='color:#ffffff'>Top 10 States</h3>", unsafe_allow_html=True)
                        querylast = f"""SELECT state,SUM(amount) AS total_amount
                                FROM map_transaction 
                                WHERE state = '{state_query}' 
                                AND year = {selected_year} 
                                AND quarter = {quat}
                                GROUP BY state
                                ORDER BY total_amount DESC
                                LIMIT 10;"""
                
                        df_last = pd.read_sql(querylast, db_config)

               
                    
                    # Create two columns for the list
                        ls, rs = st.columns([2, 1])
                    
                        with ls:
                            for i in range(len(df_last)):
                                d_name = df_last["state"].iloc[i].title()
                                st.markdown(f"<p style='color:#ffffff; font-weight:600; font-size:20px; margin-bottom:0px;'>{i+1}. {d_name}</p>", unsafe_allow_html=True)
                    
                        with rs:
                            for i in range(len(df_last)):
                                d_amt = df_last["total_amount"].iloc[i]/10000000
                                st.markdown(f"<p style='color:#32E0C4; font-weight:600; font-size:20px; margin-bottom:0px;'>₹{d_amt:,.0f} cr</p>", unsafe_allow_html=True)
                    else:
                        st.markdown("<h3 style='color:#ffffff'>Top 10 States</h3>", unsafe_allow_html=True)
                        querylast = f"""SELECT state,SUM(amount) AS total_amount
                                        FROM map_transaction 
                                        GROUP BY state
                                        ORDER BY total_amount DESC
                                        LIMIT 10;"""
                        
                        df_last = pd.read_sql(querylast, db_config)

                    
                            
                            # Create two columns for the list
                        ls, rs = st.columns([2, 1])
                            
                        with ls:
                                for i in range(len(df_last)):
                                    d_name = df_last["state"].iloc[i].title()
                                    st.markdown(f"<p style='color:#ffffff; font-weight:600; font-size:20px; margin-bottom:0px;'>{i+1}. {d_name}</p>", unsafe_allow_html=True)
                            
                        with rs:
                                for i in range(len(df_last)):
                                    d_amt = df_last["total_amount"].iloc[i]/10000000
                                    st.markdown(f"<p style='color:#32E0C4; font-weight:600; font-size:20px; margin-bottom:0px;'>₹{d_amt:,.0f} cr</p>", unsafe_allow_html=True)
                            
                
                with t2:
                    if st.session_state.view == 'State' and st.session_state.selected_state: 
                        st.markdown("<h3 style='color:#ffffff'>Top 10 States</h3>", unsafe_allow_html=True)
                        state_query = st.session_state.selected_state.lower().replace(' ', '-')
                        st.markdown("<h3 style='color:#ffffff'>Top 10 Districts</h3>", unsafe_allow_html=True)
                        querylast = f"""SELECT district,SUM(amount) AS total_amount
                                FROM map_transaction
                                WHERE state = '{state_query}' 
                                AND year = {selected_year} 
                                AND quarter = {quat} 
                                GROUP BY district
                                ORDER BY total_amount DESC
                                LIMIT 10;"""
                
                        df_last = pd.read_sql(querylast, db_config)

               
                    
                    # Create two columns for the list
                        ls, rs = st.columns([2, 1])
                    
                        with ls:
                            for i in range(len(df_last)):
                                re= df_last["district"].str.replace("district","")
                                d_name =re.iloc[i].title()
                                st.markdown(f"<p style='color:#ffffff; font-weight:600; font-size:20px; margin-bottom:0px;'>{i+1}. {d_name}</p>", unsafe_allow_html=True)
                    
                        with rs:
                            for i in range(len(df_last)):
                                d_amt = df_last["total_amount"].iloc[i]/10000000
                                st.markdown(f"<p style='color:#32E0C4; font-weight:600; font-size:20px; margin-bottom:0px;'>₹{d_amt:,.0f} cr</p>", unsafe_allow_html=True)
                    else:
                        st.markdown("<h3 style='color:#ffffff'>Top 10 Districts</h3>", unsafe_allow_html=True)
                        querylast = f"""SELECT district,SUM(amount) AS total_amount
                                FROM map_transaction
                                GROUP BY district
                                ORDER BY total_amount DESC
                                LIMIT 10;"""
                
                        df_last = pd.read_sql(querylast, db_config)

               
                    
                    # Create two columns for the list
                        ls, rs = st.columns([2, 1])
                    
                        with ls:
                            for i in range(len(df_last)):
                                re= df_last["district"].str.replace("district","")
                                d_name =re.iloc[i].title()
                                st.markdown(f"<p style='color:#ffffff; font-weight:600; font-size:20px; margin-bottom:0px;'>{i+1}. {d_name}</p>", unsafe_allow_html=True)
                    
                        with rs:
                            for i in range(len(df_last)):
                                d_amt = df_last["total_amount"].iloc[i]/10000000
                                st.markdown(f"<p style='color:#32E0C4; font-weight:600; font-size:20px; margin-bottom:0px;'>₹{d_amt:,.0f} cr</p>", unsafe_allow_html=True)
                    


                




        
        
        
        else:
            if st.session_state.view == 'State' and st.session_state.selected_state:
                state_query = st.session_state.selected_state.lower().replace(' ', '-')
                queryd = f""" SELECT year, quarter, SUM(registered_users) AS total_users,sum(app_opens) as apo
        FROM {type} 
        WHERE state = '{state_query}' 
        AND year = {selected_year} 
        AND quarter = {quat}
        GROUP BY year, quarter;"""
                title_suffix = f"in {st.session_state.selected_state}"
            else:
                queryd = f"""SELECT year, quarter, SUM(registered_users)AS total_users,sum(app_opens) as apo   FROM {type}
                WHERE   year = {selected_year} 
        AND quarter = {quat}
        GROUP BY year, quarter;"""
                title_suffix = "Across India"

            df_data1 = pd.read_sql(queryd, db_config)
            

            # 2. RENDER THE UI
            st.markdown("<h3 style='color:#32E0C4'>Users</h3>", unsafe_allow_html=True)
            st.markdown(f"<h5 style='color:#ffffff; margin-bottom:0px;'>Registered PhonePe Users</h5>", unsafe_allow_html=True)
            st.markdown(f"""<h2 style='color: #32E0C4; font-size: 40px; margin-bottom:20px; padding: 0px; margin: 0px; line-height:1;'>{df_data1['total_users'][0]:,.0f}</h2>""",unsafe_allow_html=True)
            st.markdown(f"<h5 style='color:#ffffff; margin-bottom:0px;'>PhonePe app opens</h5>", unsafe_allow_html=True)
            st.markdown(f"""<h2 style='color: #32E0C4; font-size: 40px; padding: 0px; margin: 0px; line-height:1;'>{df_data1['apo'][0]:,.0f}</h2>""",unsafe_allow_html=True)

            st.divider()
            if st.session_state.view == 'State' and st.session_state.selected_state: 
                state_query = st.session_state.selected_state.lower().replace(' ', '-')
                
                # Fetching the Top 10
                st.markdown("""
    <style>
    /* Styling the container for all tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }

    /* Styling each individual tab (The "Pill") */
    .stTabs [data-baseweb="tab"] {
        height: 35px;
        white-space: pre-wrap;
        background-color: #2b1b3d; /* Dark purple background matching the theme */
        border-radius: 20px; /* Fully rounded corners for the pill look */
        color: #ffffff;
        padding-left: 20px;
        padding-right: 20px;
        margin-bottom:10px;
        border: 1px solid #4d3b5d;
    }

    /* Styling the active tab when selected */
    .stTabs [aria-selected="true"] {
        background-color:#7cfc00!important;
        color: #000000 !important;
        font-weight: bold;
    }
    
    /* Removing the default underline from Streamlit tabs */
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: transparent !important;
    }
    </style>
""", unsafe_allow_html=True)
                t2,t3=st.tabs(["Districts","PIncode"])
                with t2:
                        st.markdown("<h3 style='color:#ffffff'>Top 10 Districts</h3>", unsafe_allow_html=True)
                        querylast = f"""SELECT district,SUM(registered_users) AS total_amount
                                FROM map_user
                                WHERE state='{state_query}'and
        year = {selected_year} 
        AND quarter = {quat}
                                GROUP BY district
                                ORDER BY total_amount DESC
                                LIMIT 10;"""
                
                        df_last = pd.read_sql(querylast, db_config)

               
                    
                    # Create two columns for the list
                        ls, rs = st.columns([2, 1])
                    
                        with ls:
                            for i in range(len(df_last)):
                                re= df_last["district"].str.replace("district","")
                                d_name =re.iloc[i].title()
                                st.markdown(f"<p style='color:#ffffff; font-weight:600; font-size:20px; margin-bottom:0px;'>{i+1}. {d_name}</p>", unsafe_allow_html=True)
                    
                        with rs:
                            for i in range(len(df_last)):
                                d_amt = df_last["total_amount"].iloc[i]/100000
                                st.markdown(f"<p style='color:#32E0C4; font-weight:600; font-size:20px; margin-bottom:0px;'>{d_amt:,.0f}L</p>", unsafe_allow_html=True)
                with t3:
                    st.markdown("<h3 style='color:#ffffff'>Top 10 Pincode</h3>", unsafe_allow_html=True)
                    querylast = f"""SELECT pincode,SUM(registered_users) AS total_amount
                                FROM top_user
                                WHERE state='{state_query}'and
        year = {selected_year} 
        AND quarter = {quat}
                                GROUP BY pincode
                                ORDER BY total_amount DESC
                                LIMIT 10;"""
                
                    df_last = pd.read_sql(querylast, db_config)

               
                    
                    # Create two columns for the list
                    ls, rs = st.columns([2, 1])
                    
                    with ls:
                        for i in range(len(df_last)):
                            d_name = df_last["pincode"].iloc[i].title()
                            st.markdown(f"<p style='color:#ffffff; font-weight:600; font-size:20px; margin-bottom:0px;'>{i+1}. {d_name}</p>", unsafe_allow_html=True)
                    
                    with rs:
                        for i in range(len(df_last)):
                            d_amt = df_last["total_amount"].iloc[i]/100000
                            st.markdown(f"<p style='color:#32E0C4; font-weight:600; font-size:20px; margin-bottom:0px;'>{d_amt:,.0f}L</p>", unsafe_allow_html=True)
            else:
                st.markdown("""
    <style>
    /* Styling the container for all tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }

    /* Styling each individual tab (The "Pill") */
    .stTabs [data-baseweb="tab"] {
        height: 35px;
        white-space: pre-wrap;
        background-color: #2b1b3d; /* Dark purple background matching the theme */
        border-radius: 20px; /* Fully rounded corners for the pill look */
        color: #ffffff;
        padding-left: 20px;
        padding-right: 20px;
        margin-bottom:10px;
        border: 1px solid #4d3b5d;
    }

    /* Styling the active tab when selected */
    .stTabs [aria-selected="true"] {
        background-color:#7cfc00!important;
        color: #000000 !important;
        font-weight: bold;
    }
    
    /* Removing the default underline from Streamlit tabs */
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: transparent !important;
    }
    </style>
""", unsafe_allow_html=True)
                t1,t2,t3=st.tabs(["States","Districts","PIncode"])
                with t1:
                        st.markdown("<h3 style='color:#ffffff'>Top 10 States</h3>", unsafe_allow_html=True)
                        querylast = f"""SELECT state,SUM(registered_users) AS total_amount
                                FROM map_user
                                WHERE
        year = {selected_year} 
        AND quarter = {quat}
                                GROUP BY state
                                ORDER BY total_amount DESC
                                LIMIT 10;"""
                
                        df_last = pd.read_sql(querylast, db_config)

                
                        
                        # Create two columns for the list
                        ls, rs = st.columns([2, 1])
                        
                        with ls:
                            for i in range(len(df_last)):
                                d_name = df_last["state"].iloc[i].title()
                                st.markdown(f"<p style='color:#ffffff; font-weight:600; font-size:20px; margin-bottom:0px;'>{i+1}. {d_name}</p>", unsafe_allow_html=True)
                        
                        with rs:
                            for i in range(len(df_last)):
                                d_amt = df_last["total_amount"].iloc[i]/100000
                                st.markdown(f"<p style='color:#32E0C4; font-weight:600; font-size:20px; margin-bottom:0px;'>{d_amt:,.0f}L</p>", unsafe_allow_html=True)
                   

                with t2:
                        st.markdown("<h3 style='color:#ffffff'>Top 10 Districts</h3>", unsafe_allow_html=True)
                        querylast = f"""SELECT district,SUM(registered_users) AS total_amount
                                FROM map_user
                                WHERE 
        year = {selected_year} 
        AND quarter = {quat}
                                GROUP BY district
                                ORDER BY total_amount DESC
                                LIMIT 10;"""
                
                        df_last = pd.read_sql(querylast, db_config)

               
                    
                    # Create two columns for the list
                        ls, rs = st.columns([2, 1])
                    
                        with ls:
                            for i in range(len(df_last)):
                                re= df_last["district"].str.replace("district","")
                                d_name =re.iloc[i].title()
                                st.markdown(f"<p style='color:#ffffff; font-weight:600; font-size:20px; margin-bottom:0px;'>{i+1}. {d_name}</p>", unsafe_allow_html=True)
                    
                        with rs:
                            for i in range(len(df_last)):
                                d_amt = df_last["total_amount"].iloc[i]/100000
                                st.markdown(f"<p style='color:#32E0C4; font-weight:600; font-size:20px; margin-bottom:0px;'>{d_amt:,.0f}L</p>", unsafe_allow_html=True)
                with t3:
                    st.markdown("<h3 style='color:#ffffff'>Top 10 Pincode</h3>", unsafe_allow_html=True)
                    querylast = f"""SELECT pincode,SUM(registered_users) AS total_amount
                                FROM top_user
                                WHERE
        year = {selected_year} 
        AND quarter = {quat}
                                GROUP BY pincode
                                ORDER BY total_amount DESC
                                LIMIT 10;"""
                
                    df_last = pd.read_sql(querylast, db_config)

               
                    
                    # Create two columns for the list
                    ls, rs = st.columns([2, 1])
                    
                    with ls:
                        for i in range(len(df_last)):
                            d_name = df_last["pincode"].iloc[i].title()
                            st.markdown(f"<p style='color:#ffffff; font-weight:600; font-size:20px; margin-bottom:0px;'>{i+1}. {d_name}</p>", unsafe_allow_html=True)
                    
                    with rs:
                        for i in range(len(df_last)):
                            d_amt = df_last["total_amount"].iloc[i]/100000
                            st.markdown(f"<p style='color:#32E0C4; font-weight:600; font-size:20px; margin-bottom:0px;'>{d_amt:,.0f}L</p>", unsafe_allow_html=True)

        
    

    


elif st.session_state.page == "Insights":
    st.title("Insights Page")

    selected_option = st.selectbox(
        'Choose a case study:',
        (
            'Decoding Transaction Dynamics On Phonepe',
            'Insurance Penetration And Growth Potential Analysis',
            'Transaction Analysis For Market Expansion',
            'User Registration Analysis',
            'User Engagement And Growth Strategy'
        )
    )

    if selected_option == 'Decoding Transaction Dynamics On Phonepe':
        st.subheader("Yearly Transaction Trend")

        query = """
        SELECT year,
               SUM(transaction_count) AS total_trans_count,
               SUM(transaction_amount) AS total_trans_amount 
        FROM aggregated_transaction
        GROUP BY year
        ORDER BY year;
        """
        df_year = pd.read_sql(query, db_config)

        col1, col2 = st.columns(2)

        with col1:
            fig, ax = plt.subplots(figsize=(6,4))
            fig.patch.set_facecolor("#1e252c")
            ax.set_facecolor("#161c22")
            sns.lineplot(data=df_year, x="year", y="total_trans_count",
                         marker="o", color="#39FF14", linewidth=2.5, ax=ax)
            ax.set_title("Transaction Count Growth", color="#f3f4f6", fontsize=14, weight="bold")
            ax.tick_params(colors="white")
            ax.grid(color="#f3f4f6", linestyle="--", linewidth=0.5, alpha=0.4)
            st.pyplot(fig)

        with col2:
            fig, ax = plt.subplots(figsize=(6,4))
            fig.patch.set_facecolor("#1e252c")
            ax.set_facecolor("#161c22")
            sns.lineplot(data=df_year, x="year", y="total_trans_amount",
                         marker="o", color="#39FF14", linewidth=2.5, ax=ax)
            ax.set_title("Transaction Amount Growth", color="#f3f4f6", fontsize=14, weight="bold")
            ax.tick_params(colors="white")
            ax.grid(color="#f3f4f6", linestyle="--", linewidth=0.5, alpha=0.4)
            st.pyplot(fig)

        st.subheader("Top Transaction Type")

        query2 = """
        SELECT transaction_type,
               SUM(transaction_amount) AS total_trans_amount 
        FROM aggregated_transaction
        GROUP BY transaction_type
        ORDER BY total_trans_amount DESC;
        """
        df_state = pd.read_sql(query2, db_config)

        fig, ax3 = plt.subplots(figsize=(8,3))
        fig.patch.set_facecolor("#1e252c")
        ax3.set_facecolor("#161c22")
        sns.barplot(data=df_state, x="total_trans_amount",
                    y="transaction_type", color="#39FF14", ax=ax3)
        ax3.tick_params(colors="white")
        ax3.grid(color="#f3f4f6", linestyle="--", linewidth=0.5, alpha=0.3)
        st.pyplot(fig)

        st.subheader("Transaction Type Dynamics")

        tran_type = st.selectbox("Select Transaction Type", [
            "Peer-to-peer payments", "Merchant payments",
            "Recharge & bill payments", "Others", "Financial Services"
        ])

        query5 = """
        SELECT year, transaction_type,
               SUM(transaction_amount) AS total_transty_amount 
        FROM aggregated_transaction
        WHERE transaction_type = %s
        GROUP BY year, transaction_type
        ORDER BY year, total_transty_amount ASC;
        """
        df_type = pd.read_sql(query5, db_config, params=(tran_type,))

        fig, ax5 = plt.subplots(figsize=(8,3))
        fig.patch.set_facecolor("#1e252c")
        ax5.set_facecolor("#161c22")
        sns.barplot(data=df_type, x="year", y="total_transty_amount",
                    color="#39FF14", ax=ax5)
        ax5.set_xlabel("Year", color="white", weight="bold")
        ax5.set_ylabel("Transaction Amount", color="white", weight="bold")
        ax5.tick_params(colors="white")
        ax5.grid(color="#f3f4f6", linestyle="--", linewidth=0.5, alpha=0.3)
        st.pyplot(fig)

        st.subheader("Year and Quarter-wise Transactions")

        stateo = st.selectbox("Select State", [
            "andaman-&-nicobar-islands","andhra-pradesh","arunachal-pradesh","assam","bihar",
            "chandigarh","chhattisgarh","dadra-&-nagar-haveli-&-daman-&-diu","delhi","goa",
            "gujarat","haryana","himachal-pradesh","jammu-&-kashmir","jharkhand","karnataka",
            "kerala","ladakh","lakshadweep","madhya-pradesh","maharashtra","manipur",
            "meghalaya","mizoram","nagaland","odisha","puducherry","punjab","rajasthan",
            "sikkim","tamil-nadu","telangana","tripura","uttar-pradesh","uttarakhand","west-bengal"
        ])

        query3 = """
        SELECT year, quarter,
               SUM(transaction_amount)/10000000 AS total_trans_amount 
        FROM aggregated_transaction
        WHERE state = %s
        GROUP BY year, quarter
        ORDER BY year, quarter;
        """
        df_state = pd.read_sql(query3, db_config, params=(stateo,))

        fig, ax4 = plt.subplots(figsize=(15,4))
        fig.patch.set_facecolor("#1e252c")
        ax4.set_facecolor("#161c22")
        sns.barplot(data=df_state, x="year", y="total_trans_amount",
                    hue="quarter",
                    palette=["#39FF14", "#32E0C4", "#7CFC00", "#00FF7F"],
                    ax=ax4)
        ax4.set_title(f"Quarterly Transactions in {stateo.title()}",
                      color="#f3f4f6", fontsize=14, weight="bold")
        ax4.set_xlabel("Year", color="white", weight="bold")
        ax4.set_ylabel("Transaction Amount", color="white", weight="bold")
        ax4.tick_params(colors="white")
        ax4.grid(color="#f3f4f6", linestyle="--", linewidth=0.5, alpha=0.3)
        legend = ax4.legend(title="Quarter")
        plt.setp(legend.get_texts(), color='white')
        plt.setp(legend.get_title(), color='white')
        st.pyplot(fig)

        st.subheader("Region Wise Percentage")

        query6 = """
        SELECT r.region,
               SUM(ag.transaction_amount) AS total_sum
        FROM aggregated_transaction ag
        LEFT JOIN regions r ON ag.state = r.state
        GROUP BY r.region
        ORDER BY total_sum DESC;
        """
        df_region = pd.read_sql(query6, db_config)

        fig, ax6 = plt.subplots(figsize=(1.2,1.2))
        fig.patch.set_facecolor("#1e252c")
        ax6.set_facecolor("#161c22")

        wedges, texts, autotexts = ax6.pie(
            df_region["total_sum"],
            labels=df_region["region"],
            autopct='%1.1f%%',
            startangle=30,
            radius=1,
            colors=["#39FF14", "#00E5FF", "#FF6EC7", "#FFA500", "#9b59b6"],
            wedgeprops={'width':1},
            explode=[0,0,0,0,0,0.4],
            textprops={'color':"white",'fontsize':6}
        )

        for autotext in autotexts:
            autotext.set_color("black")
            autotext.set_fontweight("bold")
            autotext.set_fontsize(4)
        st.pyplot(fig)
        plt.clf()
    if selected_option == "Insurance Penetration And Growth Potential Analysis":
        st.subheader("Yearly Transaction Trend")
        col1,col2 =st.columns(2)
        with col1:
            queryin1="""select year,sum(transaction_count) as total_count from aggregated_insurance
                        group by year
                        order by year asc;
                     """
            df_in_c1=pd.read_sql(queryin1,db_config)
            fig,axc1=plt.subplots(figsize=(5.9,4))
            fig.patch.set_facecolor("#1e252c")
            axc1.set_facecolor("#161c22")
            sns.lineplot(data=df_in_c1,x="year",y="total_count",marker="o", color="#39FF14", linewidth=2.5, ax=axc1)
            axc1.set_xlabel("Years",color="white",weight="bold")
            axc1.set_ylabel("Insurance Count",color="white",weight="bold")
            axc1.tick_params(colors="white")
            axc1.set_title("Insurance Count Growth", color="#f3f4f6", fontsize=14, weight="bold")
            axc1.grid(color="#f3f4f6", linestyle="--", linewidth=0.5, alpha=0.3)
            axc1.set_xticks(df_in_c1["year"])
            #axc1.set_xticklabels(df_in_c1["year"].astype(int))
            st.pyplot(fig)

        with col2:
            queryin2="""select year,sum(transaction_amount) as total_amount from aggregated_insurance
                        group by year
                        order by year asc;
                     """
            df_in_c2=pd.read_sql(queryin2,db_config)
            fig,axc2=plt.subplots(figsize=(6,4))
            axc2.set_facecolor("#161c22")
            sns.lineplot(data=df_in_c2,x="year",y="total_amount",marker="o", color="#39FF14", linewidth=2.5, ax=axc2)
            fig.patch.set_facecolor("#1e252c")
            axc2.set_title("Insurance Transaction Amount Growth", color="#f3f4f6", fontsize=14, weight="bold")
            axc2.grid(color="#f3f4f6", linestyle="--", linewidth=0.5, alpha=0.3)
            axc2.set_xlabel("Years",color="white",weight="bold")
            axc2.tick_params(colors="white")
            axc2.set_ylabel("Transaction amount", color="#f3f4f6", fontsize=14, weight="bold")
            axc2.set_xticks(df_in_c2["year"])
            axc2.set_xticklabels(df_in_c2["year"])

            st.pyplot(fig)


        st.subheader("States By Insurance Adoption")
        cola,colb =st.columns(2)
        
        
        
        
        with cola:
            queryi1="""SELECT state,
       SUM(transaction_count) AS total_count
FROM aggregated_insurance
GROUP BY state
ORDER BY total_count DESC
LIMIT 10;"""
            df_in=pd.read_sql(queryi1,db_config)
            fig,axi1=plt.subplots(figsize=(7,4))
            fig.patch.set_facecolor("#1e252c")
            axi1.set_facecolor("#161c22")
            sns.barplot(data=df_in,x="total_count",y="state",color="#39FF14",ax=axi1)
            axi1.tick_params(colors="white")
            axi1.set_xlabel("Transaction Count",color="white",weight="bold")
            axi1.set_ylabel("States",color="white",weight="bold")
            axi1.grid(color="#f3f4f6", linestyle="--", linewidth=0.5, alpha=0.3)
            axi1.set_title("Top 10 States", color="#f3f4f6", fontsize=14, weight="bold")
        #axi1.set_xticks(df_in["state"])
            st.pyplot(fig)

        with colb:
            queryi1="""SELECT state,
       SUM(transaction_count) AS total_count
FROM aggregated_insurance
GROUP BY state
ORDER BY total_count ASC
LIMIT 10;"""
            df_in=pd.read_sql(queryi1,db_config)
            fig,axi1=plt.subplots(figsize=(5,4))
            fig.patch.set_facecolor("#1e252c")
            axi1.set_facecolor("#161c22")
            sns.barplot(data=df_in,x="total_count",y="state",color="#39FF14",ax=axi1)
            axi1.tick_params(colors="white")
            axi1.set_xlabel("Transaction Count",color="white",weight="bold")
            axi1.set_ylabel("States",color="white",weight="bold")
            axi1.grid(color="#f3f4f6", linestyle="--", linewidth=0.5, alpha=0.3)
            axi1.set_title("Bottom 10 States", color="#f3f4f6", fontsize=14, weight="bold")
            #axi1.set_xticks(df_in["state"])
            st.pyplot(fig)
        st.subheader("States Wise Insurance Growth Trend")
        queryi2="""SELECT year,state,
       SUM(transaction_count) AS total_count
FROM aggregated_insurance
WHERE state IN ('maharashtra','karnataka','tamil-nadu','uttar-pradesh','telangana')
GROUP BY year,state
ORDER BY year asc
;"""
        df_in=pd.read_sql(queryi2,db_config)
        fig,axi2=plt.subplots(figsize=(9,3.5))
        fig.patch.set_facecolor("#1e252c")
        axi2.set_facecolor("#161c22")
        sns.lineplot(data=df_in,x="year",y="total_count",hue="state",marker="o",ax=axi2)
        sns.move_legend(axi2, "upper left",borderpad=0.5,handlelength=1.0)
        axi2.tick_params(colors="white")
        axi2.set_xlabel("Years",color="white",weight="bold")
        axi2.set_ylabel("Transaction Count",color="white",weight="bold")
        axi2.grid(color="#f3f4f6", linestyle="--", linewidth=0.5, alpha=0.3)
        #axi2.set_title("Last 10 States", color="#f3f4f6", fontsize=14, weight="bold")
        axi2.set_xticklabels(df_in["year"])
        st.pyplot(fig)

        st.subheader("Insurance Penetration Of Total Transaction")
        queryi3="""SELECT at.year,
       SUM(ai.transaction_count) AS insurance_txn,
       SUM(at.transaction_count) AS total_txn
FROM aggregated_transaction at
JOIN aggregated_insurance ai
     ON at.year = ai.year
GROUP BY at.year
ORDER BY at.year;"""
        df_in=pd.read_sql(queryi3,db_config)
        fig,axi3=plt.subplots(figsize=(10,5))
        fig.patch.set_facecolor("#1e252c")
        axi3.set_facecolor("#161c22")
        df_in["penetration_pct"] = (df_in["insurance_txn"] / df_in["total_txn"]) * 100
        sns.barplot(data=df_in,x="year",y="penetration_pct",color="#39FF14",ax=axi3)
        axi3.tick_params(colors="white")
        axi3.set_xlabel("Years",color="white",weight="bold")
        axi3.set_ylabel("Percentage",color="white",weight="bold")
        axi3.grid(color="#f3f4f6", linestyle="--", linewidth=0.5, alpha=0.3)
        #axi2.set_title("Last 10 States", color="#f3f4f6", fontsize=14, weight="bold")
        #axi3.set_xticks(df_in["year"])
        for container in axi3.containers:
            axi3.bar_label(container, fmt='%1.3f%%', color="white")
        axi3.set_xticklabels(df_in["year"])

        st.pyplot(fig)

        st.subheader("Region Wise Insurance Share")
        queryi4="""SELECT r.region as region,
       SUM(ai.transaction_count) AS total_count
FROM aggregated_insurance ai
JOIN regions r ON ai.state = r.state
GROUP BY r.region
ORDER BY total_count DESC"""
        df_in=pd.read_sql(queryi4,db_config)
        fig,axi4=plt.subplots(figsize=(1.5,1.5))
        fig.patch.set_facecolor("#1e252c")
        axi4.set_facecolor("#161c22")
        #sns.barplot(data=df_in,x="region",y="total_count",color="#39FF14",ax=axi3)
        wedges, texts, autotexts = axi4.pie(
            df_in["total_count"],
            labels=df_in["region"],
            autopct='%1.1f%%',
            startangle=30,
            radius=1,
            colors=["#39FF14", "#00E5FF", "#FF6EC7", "#FFA500", "#9b59b6"],
            wedgeprops={'width':1},
            explode=[0,0,0,0,0,0.4],
            textprops={'color':"white",'fontsize':6}
        )
        for autotext in autotexts:
            autotext.set_color("black")
            autotext.set_fontweight("bold")
            autotext.set_fontsize(4)
        #axi4.pie(df_in["total_count"],labels=df_in["region"],autopct='%1.1f%%')
        #lengend=axi4.legend(["Northern","Southern","Central","Eastern","Western","North-Eastern"])
        #sns.move_legend(axi4,"upper left",title="Regions",)
        axi4.tick_params(colors="white")
        #axi3.set_xlabel("Years",color="white",weight="bold")
        #axi3.set_ylabel("Percentage",color="white",weight="bold")
        axi4.grid(color="#f3f4f6", linestyle="--", linewidth=0.5, alpha=0.3)
        #axi2.set_title("Last 10 States", color="#f3f4f6", fontsize=14, weight="bold")
        #axi3.set_xticks(df_in["year"])
        st.pyplot(fig)




    if selected_option == "Transaction Analysis For Market Expansion":
        st.subheader("Yearly Transaction Growth")
        
       
        queryin1="""SELECT year, SUM(transaction_count) AS total_count
FROM aggregated_transaction
GROUP BY year
ORDER BY year;
                     """
        df_in_c1=pd.read_sql(queryin1,db_config)
        fig,axc1=plt.subplots(figsize=(7,2))
        fig.patch.set_facecolor("#1e252c")
        axc1.set_facecolor("#161c22")
        sns.lineplot(data=df_in_c1,x="year",y="total_count",marker="o", color="#39FF14", linewidth=2.5, ax=axc1)
        axc1.set_xlabel("Years",color="white",weight="bold")
        axc1.set_ylabel("Transaction Count",color="white",weight="bold")
        axc1.tick_params(colors="white")
        axc1.set_title("Transaction Count Growth", color="#f3f4f6", fontsize=14, weight="bold")
        axc1.grid(color="#f3f4f6", linestyle="--", linewidth=0.5, alpha=0.3)
        axc1.set_xticks(df_in_c1["year"])
            #axc1.set_xticklabels(df_in_c1["year"].astype(int))
        st.pyplot(fig)

        


        st.subheader("States By Transaction Count")
        cola,colb =st.columns(2)
        
        
        
        
        with cola:
            queryi1="""SELECT state, SUM(transaction_count) AS total_count
FROM aggregated_transaction
GROUP BY state
ORDER BY total_count DESC
LIMIT 10;"""
            df_in=pd.read_sql(queryi1,db_config)
            fig,axi1=plt.subplots(figsize=(7,4))
            fig.patch.set_facecolor("#1e252c")
            axi1.set_facecolor("#161c22")
            sns.barplot(data=df_in,x="total_count",y="state",color="#39FF14",ax=axi1)
            axi1.tick_params(colors="white")
            axi1.set_xlabel("Transaction Count",color="white",weight="bold")
            axi1.set_ylabel("States",color="white",weight="bold")
            axi1.grid(color="#f3f4f6", linestyle="--", linewidth=0.5, alpha=0.3)
            axi1.set_title("Top 10 States", color="#f3f4f6", fontsize=14, weight="bold")
        #axi1.set_xticks(df_in["state"])
            st.pyplot(fig)

        with colb:
            queryi1="""SELECT state, SUM(transaction_count) AS total_count
FROM aggregated_transaction
GROUP BY state
ORDER BY total_count ASC
LIMIT 10;"""
            df_in=pd.read_sql(queryi1,db_config)
            fig,axi1=plt.subplots(figsize=(6,4))
            fig.patch.set_facecolor("#1e252c")
            axi1.set_facecolor("#161c22")
            sns.barplot(data=df_in,x="total_count",y="state",color="#39FF14",ax=axi1)
            axi1.tick_params(colors="white")
            axi1.set_xlabel("Transaction Count",color="white",weight="bold")
            axi1.set_ylabel("States",color="white",weight="bold")
            axi1.grid(color="#f3f4f6", linestyle="--", linewidth=0.5, alpha=0.3)
            axi1.set_title("Bottom 10 States", color="#f3f4f6", fontsize=14, weight="bold")
            #axi1.set_xticks(df_in["state"])
            st.pyplot(fig)

        st.subheader("Year and Quarter-wise Transactions")    
        queryi2="""SELECT year, quarter, SUM(transaction_count) AS total_count
FROM aggregated_transaction
GROUP BY year, quarter
ORDER BY year, quarter;"""
        df_in=pd.read_sql(queryi2,db_config)
        fig,axi2=plt.subplots(figsize=(15,4))
        fig.patch.set_facecolor("#1e252c")
        axi2.set_facecolor("#161c22")
        sns.barplot(data=df_in, x="year", y="total_count",
                    hue="quarter",
                    palette=["#39FF14", "#32E0C4", "#7CFC00", "#00FF7F"],
                    ax=axi2)
        axi2.set_title(f"Quarterly Transactions",
                      color="#f3f4f6", fontsize=14, weight="bold")
        axi2.tick_params(colors="white")
        axi2.set_xlabel("Years",color="white",weight="bold")
        axi2.set_ylabel("Transaction Count",color="white",weight="bold")
        axi2.grid(color="#f3f4f6", linestyle="--", linewidth=0.5, alpha=0.3)
        legend = axi2.legend(title="Quarter")
        plt.setp(legend.get_texts(), color='white')
        plt.setp(legend.get_title(), color='white')
        #axi2.set_title("Last 10 States", color="#f3f4f6", fontsize=14, weight="bold")
        
        st.pyplot(fig)

        st.subheader("Region Wise Transaction Share")
        queryi5="""SELECT r.region, SUM(ag.transaction_count) AS total_count
FROM aggregated_transaction ag
JOIN regions r ON ag.state = r.state
GROUP BY r.region
ORDER BY total_count DESC;"""
        df_in=pd.read_sql(queryi5,db_config)
        fig,axi5=plt.subplots(figsize=(1.5,1.5))
        fig.patch.set_facecolor("#1e252c")
        axi5.set_facecolor("#161c22")
        #sns.barplot(data=df_in,x="region",y="total_count",color="#39FF14",ax=axi3)
        wedges, texts, autotexts = axi5.pie(
            df_in["total_count"],
            labels=df_in["region"],
            autopct='%1.1f%%',
            startangle=30,
            radius=1,
            colors=["#39FF14", "#00E5FF", "#FF6EC7", "#FFA500", "#9b59b6"],
            wedgeprops={'width':1},
            explode=[0,0,0,0,0,0.4],
            textprops={'color':"white",'fontsize':6}
        )
        for autotext in autotexts:
            autotext.set_color("black")
            autotext.set_fontweight("bold")
            autotext.set_fontsize(4)
        #axi4.pie(df_in["total_count"],labels=df_in["region"],autopct='%1.1f%%')
        #lengend=axi4.legend(["Northern","Southern","Central","Eastern","Western","North-Eastern"])
        #sns.move_legend(axi4,"upper left",title="Regions",)
        axi5.tick_params(colors="white")
        #axi3.set_xlabel("Years",color="white",weight="bold")
        #axi3.set_ylabel("Percentage",color="white",weight="bold")
        axi5.grid(color="#f3f4f6", linestyle="--", linewidth=0.5, alpha=0.3)
        #axi2.set_title("Last 10 States", color="#f3f4f6", fontsize=14, weight="bold")
        #axi3.set_xticks(df_in["year"])
        


        st.pyplot(fig)




    if selected_option == "User Registration Analysis":
        st.subheader("Yearly User Growth")
        
       
        queryin1="""SELECT year, SUM(user_count) AS total_users
FROM aggregated_user
GROUP BY year
ORDER BY year;
                     """
        df_in_c1=pd.read_sql(queryin1,db_config)
        fig,axc1=plt.subplots(figsize=(7,2))
        fig.patch.set_facecolor("#1e252c")
        axc1.set_facecolor("#161c22")
        sns.lineplot(data=df_in_c1,x="year",y="total_users",marker="o", color="#39FF14", linewidth=2.5, ax=axc1)
        axc1.set_xlabel("Years",color="white",weight="bold")
        axc1.set_ylabel("User Count",color="white",weight="bold")
        axc1.tick_params(colors="white")
        axc1.set_title("user Growth", color="#f3f4f6", fontsize=14, weight="bold")
        axc1.grid(color="#f3f4f6", linestyle="--", linewidth=0.5, alpha=0.3)
        axc1.set_xticks(df_in_c1["year"])
            #axc1.set_xticklabels(df_in_c1["year"].astype(int))
        st.pyplot(fig)

        


        
        cola,colb =st.columns(2)
        
        
        
        
        with cola:
            st.subheader("Top States By User Count")
            queryi1="""SELECT state, SUM(user_count) AS total_users
FROM aggregated_user
GROUP BY state
ORDER BY total_users DESC
LIMIT 10;"""
            df_in=pd.read_sql(queryi1,db_config)
            fig,axi1=plt.subplots(figsize=(7,4))
            fig.patch.set_facecolor("#1e252c")
            axi1.set_facecolor("#161c22")
            sns.barplot(data=df_in,x="total_users",y="state",color="#39FF14",ax=axi1)
            axi1.tick_params(colors="white")
            axi1.set_xlabel("User Count",color="white",weight="bold")
            axi1.set_ylabel("States",color="white",weight="bold")
            axi1.grid(color="#f3f4f6", linestyle="--", linewidth=0.5, alpha=0.3)
            axi1.set_title("Top 10 States", color="#f3f4f6", fontsize=14, weight="bold")
        #axi1.set_xticks(df_in["state"])
            st.pyplot(fig)
        
        with colb:
            st.subheader("Top Districts By User Count")
            queryi1="""SELECT district, SUM(registered_users) AS total_users
FROM map_user
GROUP BY district
ORDER BY total_users DESC
LIMIT 10;"""
            df_in=pd.read_sql(queryi1,db_config)
            fig,axi1=plt.subplots(figsize=(5.3,4))
            fig.patch.set_facecolor("#1e252c")
            axi1.set_facecolor("#161c22")
            sns.barplot(data=df_in,x="total_users",y="district",color="#39FF14",ax=axi1)
            axi1.tick_params(colors="white")
            axi1.set_xlabel("Total Users",color="white",weight="bold")
            axi1.set_ylabel("District",color="white",weight="bold")
            axi1.grid(color="#f3f4f6", linestyle="--", linewidth=0.5, alpha=0.3)
            axi1.set_title("Bottom 10 States", color="#f3f4f6", fontsize=14, weight="bold")
            #axi1.set_xticks(df_in["state"])
            st.pyplot(fig)

        st.subheader("Quarterly Registration Trend")    
        queryi2="""SELECT year, quarter, SUM(user_count) AS total_users
FROM aggregated_user
GROUP BY year, quarter
ORDER BY year, quarter;"""
        df_in=pd.read_sql(queryi2,db_config)
        fig,axi2=plt.subplots(figsize=(15,4))
        fig.patch.set_facecolor("#1e252c")
        axi2.set_facecolor("#161c22")
        sns.barplot(data=df_in, x="year", y="total_users",
                    hue="quarter",
                    palette=["#39FF14", "#32E0C4", "#7CFC00", "#00FF7F"],
                    ax=axi2)
        axi2.set_title(f"Quarterly Registration",
                      color="#f3f4f6", fontsize=14, weight="bold")
        axi2.tick_params(colors="white")
        axi2.set_xlabel("Years",color="white",weight="bold")
        axi2.set_ylabel("Registration Count",color="white",weight="bold")
        axi2.grid(color="#f3f4f6", linestyle="--", linewidth=0.5, alpha=0.3)
        legend = axi2.legend(title="Quarter")
        plt.setp(legend.get_texts(), color='white')
        plt.setp(legend.get_title(), color='white')
        #axi2.set_title("Last 10 States", color="#f3f4f6", fontsize=14, weight="bold")
        
        st.pyplot(fig)

        st.subheader("User Percentage By Brands")
        queryi3="""WITH brands AS (
    SELECT brand, SUM(user_count) AS brand_total
    FROM aggregated_user
    GROUP BY brand
),
perc AS (
    SELECT SUM(user_count) AS grand_total
    FROM aggregated_user
)
SELECT 
    b.brand as bd,
    (b.brand_total * 100.0 / p.grand_total) AS user_percentage
FROM brands b
CROSS JOIN perc p
ORDER BY user_percentage asc;"""
        df_in=pd.read_sql(queryi3,db_config)
        fig,axi3=plt.subplots(figsize=(10,5))
        fig.patch.set_facecolor("#1e252c")
        axi3.set_facecolor("#161c22")
        #df_in["penetration_pct"] = (df_in["insurance_txn"] / df_in["total_txn"]) * 100
        sns.barplot(data=df_in,x="bd",y="user_percentage",color="#39FF14",ax=axi3)
        axi3.tick_params(colors="white")
        axi3.set_xlabel("Brands",color="white",weight="bold")
        axi3.set_ylabel("Percentage",color="white",weight="bold")
        axi3.grid(color="#f3f4f6", linestyle="--", linewidth=0.5, alpha=0.3)
        #axi2.set_title("Last 10 States", color="#f3f4f6", fontsize=14, weight="bold")
        #axi3.set_xticks(df_in["year"])
        plt.xticks(rotation=45)

        st.pyplot(fig)



        
    if selected_option == "User Engagement And Growth Strategy":
        st.subheader("App Opens Growth Over Time")
        
       
        queryin1="""SELECT year,
       SUM(app_opens) AS total_opens
FROM map_user
GROUP BY year
ORDER BY year;;
                     """
        df_in_c1=pd.read_sql(queryin1,db_config)
        fig,axc1=plt.subplots(figsize=(6,3))
        fig.patch.set_facecolor("#1e252c")
        axc1.set_facecolor("#161c22")
        sns.lineplot(data=df_in_c1,x="year",y="total_opens",marker="o", color="#39FF14", linewidth=2.5, ax=axc1)
        axc1.set_xlabel("Years",color="white",weight="bold")
        axc1.set_ylabel("Total App Opens",color="white",weight="bold")
        axc1.tick_params(colors="white")
        axc1.set_title("App Opens Trend", color="#f3f4f6", fontsize=14, weight="bold")
        axc1.grid(color="#f3f4f6", linestyle="--", linewidth=0.5, alpha=0.3)
        axc1.set_xticks(df_in_c1["year"])
            #axc1.set_xticklabels(df_in_c1["year"].astype(int))
        st.pyplot(fig)

        


        st.subheader("States By App Open")
        cole,colf=st.columns(2)
        
        
        
        with cole:
       
            queryi1="""SELECT state,
        SUM(app_opens) AS total_opens
    FROM map_user
    GROUP BY state
    ORDER BY total_opens DESC
    LIMIT 10;"""
            df_in=pd.read_sql(queryi1,db_config)
            fig,axi1=plt.subplots(figsize=(7,4))
            fig.patch.set_facecolor("#1e252c")
            axi1.set_facecolor("#161c22")
            sns.barplot(data=df_in,x="total_opens",y="state",color="#39FF14",ax=axi1)
            axi1.tick_params(colors="white")
            axi1.set_xlabel("Total Opens",color="white",weight="bold")
            axi1.set_ylabel("States",color="white",weight="bold")
            axi1.grid(color="#f3f4f6", linestyle="--", linewidth=0.5, alpha=0.3)
            axi1.set_title("Top 10 States", color="#f3f4f6", fontsize=14, weight="bold")
            #axi1.set_xticks(df_in["state"])
            st.pyplot(fig)
        with colf:
       
            queryi1="""SELECT state,
        SUM(app_opens) AS total_opens
    FROM map_user
    GROUP BY state
    ORDER BY total_opens asc
    LIMIT 10;"""
            df_in=pd.read_sql(queryi1,db_config)
            fig,axi1=plt.subplots(figsize=(5.2,4))
            fig.patch.set_facecolor("#1e252c")
            axi1.set_facecolor("#161c22")
            sns.barplot(data=df_in,x="total_opens",y="state",color="#39FF14",ax=axi1)
            axi1.tick_params(colors="white")
            axi1.set_xlabel("Total Opens",color="white",weight="bold")
            axi1.set_ylabel("States",color="white",weight="bold")
            axi1.grid(color="#f3f4f6", linestyle="--", linewidth=0.5, alpha=0.3)
            axi1.set_title("Bottom 10 States", color="#f3f4f6", fontsize=14, weight="bold")
            #axi1.set_xticks(df_in["state"])
            st.pyplot(fig)

       

        st.subheader("Engagement vs User Registrations")

        query = """
        SELECT mu.year,
            SUM(mu.app_opens) AS total_opens,
            SUM(au.user_count) AS total_users
        FROM map_user mu
        JOIN aggregated_user au
            ON mu.year = au.year
        GROUP BY mu.year
        ORDER BY mu.year;
        """

        df_eng = pd.read_sql(query, db_config)
        df_eng["year"] = df_eng["year"].astype(int)

        fig, ax1 = plt.subplots(figsize=(8,4))
        fig.patch.set_facecolor("#1e252c")
        ax1.set_facecolor("#161c22")

        # Left Axis → App Opens
        sns.lineplot(data=df_eng, x="year", y="total_opens",
                    marker="o", color="#39FF14", linewidth=2.5, ax=ax1)

        ax1.set_ylabel("App Opens", color="#39FF14", weight="bold")
        ax1.tick_params(axis='y', colors="#39FF14")

        # Right Axis → Registered Users
        ax2 = ax1.twinx()

        sns.lineplot(data=df_eng, x="year", y="total_users",
                    marker="o", color="#00E5FF", linewidth=2.5, ax=ax2)

        ax2.set_ylabel("Registered Users", color="#00E5FF", weight="bold")
        ax2.tick_params(axis='y', colors="#00E5FF")

        # Shared X styling
        ax1.set_xlabel("Year", color="white", weight="bold")
        ax1.tick_params(axis='x', colors="white")
        ax1.grid(color="#f3f4f6", linestyle="--", linewidth=0.5, alpha=0.3)

        years = df_eng["year"].tolist()
        ax1.set_xticks(years)
        ax1.set_xlim(min(years)-0.2, max(years)+0.2)

        plt.title("User Engagement vs Registrations",
                color="#f3f4f6", fontsize=14, weight="bold")

        st.pyplot(fig)

        st.subheader("Region Wise User Engagement")
        queryi5="""SELECT r.region as region,
       SUM(mu.app_opens) AS total_opens
FROM map_user mu
JOIN regions r
     ON mu.state = r.state
GROUP BY r.region
ORDER BY total_opens DESC;"""
        df_in=pd.read_sql(queryi5,db_config)
        fig,axi5=plt.subplots(figsize=(1.5,1.5))
        fig.patch.set_facecolor("#1e252c")
        axi5.set_facecolor("#161c22")
        #sns.barplot(data=df_in,x="region",y="total_count",color="#39FF14",ax=axi3)
        wedges, texts, autotexts = axi5.pie(
            df_in["total_opens"],
            labels=df_in["region"],
            autopct='%1.1f%%',
            startangle=30,
            radius=1,
            colors=["#39FF14", "#00E5FF", "#FF6EC7", "#FFA500", "#9b59b6"],
            wedgeprops={'width':1},
            textprops={'color':"white",'fontsize':6}
        )
        for autotext in autotexts:
            autotext.set_color("black")
            autotext.set_fontweight("bold")
            autotext.set_fontsize(4)
        #axi4.pie(df_in["total_count"],labels=df_in["region"],autopct='%1.1f%%')
        #lengend=axi4.legend(["Northern","Southern","Central","Eastern","Western","North-Eastern"])
        #sns.move_legend(axi4,"upper left",title="Regions",)
        axi5.tick_params(colors="white")
        #axi3.set_xlabel("Years",color="white",weight="bold")
        #axi3.set_ylabel("Percentage",color="white",weight="bold")
        axi5.grid(color="#f3f4f6", linestyle="--", linewidth=0.5, alpha=0.3)
        #axi2.set_title("Last 10 States", color="#f3f4f6", fontsize=14, weight="bold")
        #axi3.set_xticks(df_in["year"])
        


        st.pyplot(fig)
    
st.markdown("""
<style>
section[data-testid="stSidebar"] h1 {
    font-size: 26px !important;
    font-weight: 700 !important;
    justify-content:center;
    letter-spacing: 0.5px;
}
section[data-testid="stSidebar"]{
    background:#1e252c;
    color: white !important;
    font-size:20px;
}
section[data-testid="stSidebar"] button {
    background:#FAEBEB;
    color:black !important;
    border-radius: 8px;
}
section[data-testid="stSidebar"] button p{
    font-size:20px;
    font-weight: 700;
}
section[data-testid="stSidebar"] button:hover{
    background:linear-gradient(to right,#4ade80,#7cfc00);
    color:#1e252c;
    border-radius: 8px;
    margin-left:7px;
    transition: all 0.20s ease-in-out;
}
</style>
""", unsafe_allow_html=True)
