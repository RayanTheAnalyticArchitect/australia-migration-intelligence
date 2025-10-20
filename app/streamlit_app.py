import os
import streamlit as st
import pandas as pd
import snowflake.connector

st.set_page_config(page_title="AU Migration Intelligence", layout="wide")

@st.cache_resource
def get_cnx():
    return snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
        database="RIPPAA_MIGRATION",
        schema="GOLD",
        role=os.getenv("SNOWFLAKE_ROLE", "SYSADMIN"),
    )

def run_df(sql):
    cnx = get_cnx()
    cur = cnx.cursor()
    cur.execute(sql)
    cols = [c[0] for c in cur.description]
    rows = cur.fetchall()
    return pd.DataFrame(rows, columns=cols)

st.title("Australia Migration Intelligence")

year = st.selectbox("Year", ["2019","2020","2021","2022","2023"])

st.subheader("Top inbound states")
df_in = run_df(f"""
    SELECT TO_STATE, SUM(MOVES) AS TOTAL_MOVES
    FROM RIPPAA_MIGRATION.GOLD.STATE_MONTHLY_FLOWS
    WHERE STAT_MONTH LIKE '{year}-%'
    GROUP BY TO_STATE
    ORDER BY TOTAL_MOVES DESC
    LIMIT 10
""")
st.bar_chart(df_in.set_index("TO_STATE"))

st.subheader("Top state OD pairs")
df_od = run_df(f"""
    SELECT FROM_STATE || ' → ' || TO_STATE AS PAIR, SUM(MOVES) AS MOVES
    FROM RIPPAA_MIGRATION.GOLD.STATE_OD_MATRIX
    WHERE STAT_MONTH LIKE '{year}-%'
    GROUP BY FROM_STATE, TO_STATE
    ORDER BY MOVES DESC
    LIMIT 10
""")
st.dataframe(df_od)
