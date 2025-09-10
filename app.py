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

# USER_DATE = st.date_input("選擇出發日期", value=earliest_date)

unique_dates = sorted(pd.Series(df.index.date).unique())
USER_DATE = st.selectbox("選擇出發日期", unique_dates)


# USER_DATE = st.sidebar.date_input("選擇出發日期", value=df.index.min())
# USER_TIME = st.time_input("選擇出發時間", value=datetime.min.time())

# 唯一時間選項（從你的資料中整理後）
time_options = [
    "00:00" ,"05:55", "06:25", "06:30", "06:35", "06:55", "07:15", "07:20", "07:25", "07:55",
    "08:10", "08:25", "08:50", "08:55", "09:00", "09:25", "09:40", "09:45", "09:50",
    "10:10", "10:20", "10:25", "10:30", "10:35", "10:50", "10:55", "11:00", "11:20",
    "11:25", "11:30", "11:35", "11:50", "11:55", "12:00", "12:25", "12:30", "12:55",
    "13:00", "13:25", "13:30", "13:35", "13:55", "14:00", "14:25", "14:30", "14:35",
    "14:55", "15:00", "15:15", "15:20", "15:25", "15:30", "15:35", "15:40", "15:55",
    "16:00", "16:20", "16:25", "16:30", "16:35", "16:50", "16:55", "17:00", "17:15",
    "17:20", "17:30", "17:40", "17:55", "18:00", "18:05", "18:25", "18:30", "18:45",
    "18:55", "19:00", "19:05", "19:15", "19:25", "19:30", "19:35", "19:50", "20:00",
    "20:05", "20:25", "20:30", "20:40", "21:00", "21:10", "21:20", "21:30", "22:00"
]

# 建立下拉選單
selected_time = st.selectbox("選擇出發時間", time_options)

USER_TIME = datetime.strptime(selected_time, "%H:%M").time()



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
    st.write("請指定出發時間(只能選假日喔！)")

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
