import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from datetime import datetime, time,timedelta
import matplotlib.pyplot as plt

st.title("新竹客運：新竹-台中預計時間")

# 用google map 量
dis = {59:5.1,
61:11.7,
63:16,
67:23.7,
69:9.4,
73:6,
77:2.10,
79:5.7}
sections_need = [59, 61,63,67,69,73,77,79]

dfs ={}

for sec in sections_need:
    df = pd.read_csv(f"forecast/{sec}.csv")
    dfs[sec] = df
    if "timestamp" in dfs[sec].columns:
        dfs[sec]['timestamp'] = pd.to_datetime(dfs[sec]['timestamp'], errors='coerce')
        dfs[sec].set_index('timestamp', inplace=True)

# 1. 上傳多個 CSV
# uploaded_files = st.sidebar.file_uploader("請上傳 CSV 檔案", type="csv", accept_multiple_files=True)

date_col = "timestamp"

# USER_DATE = st.sidebar.date_input("選擇出發日期", value=df[date_col].min())

# 假設 df 是你的 DataFrame，且 df.index 是 DatetimeIndex
earliest_datetime = df.index.min()
earliest_date = earliest_datetime.date()  # 只取日期部分

USER_DATE = st.sidebar.date_input("選擇出發日期", value=earliest_date)

# USER_DATE = st.sidebar.date_input("選擇出發日期", value=df.index.min())
USER_TIME = st.sidebar.time_input("選擇出發時間", value=datetime.min.time())


if USER_TIME != datetime.min.time():
# if uploaded_files:

    # dfs = {f.name: pd.read_csv(f) for f in uploaded_files}
    # sections_need = ["59.csv", "61.csv","63.csv","67.csv","69.csv","73.csv","77.csv","79.csv"]

    # df = dfs["59.csv"]
    df = dfs[59]
    # st.dataframe(df.head())


    # st.write(f"{date_col}")
    # df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    # 4. 選擇完整的日期時間
    dt = datetime.combine(USER_DATE, USER_TIME)
    st.write("你選擇的完整日期時間：", dt)

    # 5. 比對並顯示符合條件的資料（範例：同一天）
    mask = df.index.date == dt.date()
    filtered = df[mask]
    st.write(f"篩選出符合 {dt.date()} 的資料：{len(filtered)} 筆。")
    # st.dataframe(filtered)
####### 計算時間 
    # 增加20 min的市區緩衝時間
    go2road = datetime.combine(USER_DATE, USER_TIME) + timedelta(minutes=20)

    # 國道上的時間計時
    road_min = 0

    # 收集國道上的時速
    road_speeds = []
    for sec in sections_need:
        df = dfs[sec].copy()

        # 初始remain
        remain_section = dis[sec]

        while remain_section >0:

            result = df.loc[go2road, "predicted_TravelSpeed"]

            # 速限設置
            if result > 120 :
                result = 120
            if result <0 :
                result = 0

            # 換成分速/km
            res_min = round(result/60,2)

            remain_section = remain_section - res_min
            road_min += 1
            road_speeds.append(result)
        
    arrive_time = go2road + timedelta(minutes=road_min) +timedelta(minutes=25) # 下高架後花費時間

    
    start_time = datetime.combine(USER_DATE, USER_TIME)
    waste_time = arrive_time - start_time
    st.write(f"預計抵達時間: {arrive_time}   總花費時間: {waste_time}")

    # 繪速度圖
    plt.figure(figsize=(10, 4))
    plt.plot(road_speeds, marker='o')
    plt.title('Travel Speed on Road Sections')
    plt.xlabel('Minute')
    plt.ylabel('Speed (km/h)')
    plt.grid(True)
    st.pyplot(plt)

else:
    st.write("請指定出發時間")

# 將你從 Google My Maps → 「嵌入到網站」取得的 iframe 程式碼，貼在這裡
iframe_code = '''
<iframe
  src="https://www.google.com/maps/d/u/0/embed?mid=1r432NZODghoi0PCof1oyCeCScQ490Pk&ehbc=2E312FF"
  width="700"
  height="480">
</iframe>
'''

# 使用 components.html 直接嵌入 iframe
components.html(iframe_code, height=480)
