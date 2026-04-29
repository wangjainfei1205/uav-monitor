import streamlit as st
import folium
from streamlit_folium import st_folium
import math
import random
import json
import os
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="无人机智能化应用系统",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="expanded"
)

NANJING_LAT = 32.234104
NANJING_LNG = 118.749421

def create_satellite_map(center_lat, center_lng, zoom=15):
    m = folium.Map(location=[center_lat, center_lng], zoom_start=zoom, tiles=None)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='© Esri',
        name='卫星地图'
    ).add_to(m)
    return m

def save_data(data, filename='route.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_data(filename='route.json'):
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {'waypoints': [], 'obstacles': []}

def init_session_state():
    if 'data' not in st.session_state:
        st.session_state.data = load_data()
    if 'heartbeat_data' not in st.session_state:
        st.session_state.heartbeat_data = []
    if 'is_simulating' not in st.session_state:
        st.session_state.is_simulating = False
    if 'battery_level' not in st.session_state:
        st.session_state.battery_level = 100.0
    if 'current_position' not in st.session_state:
        st.session_state.current_position = [NANJING_LAT, NANJING_LNG]
    if 'flight_path' not in st.session_state:
        st.session_state.flight_path = []
    if 'temp_obstacle' not in st.session_state:
        st.session_state.temp_obstacle = []
    if 'map_click_mode' not in st.session_state:
        st.session_state.map_click_mode = 'waypoint'

def render_home_page():
    st.markdown('<h1 style="text-align: center; color: #00D4AA; font-size: 2.5rem; font-weight: bold;">🚁 无人机智能化应用系统</h1>', unsafe_allow_html=True)
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### 🗺️ 航线规划
        - 卫星地图展示
        - 添加航点和障碍物（支持地图点击）
        """)
    with col2:
        st.markdown("""
        ### 🚁 飞行监控
        - 心跳包实时监控
        - 飞行轨迹实时显示
        """)

def render_route_planning_page():
    st.header("🗺️ 航线规划")
    data = st.session_state.data

    col1, col2 = st.columns([1, 2])

    with col1:
        st.info(f"🎯 当前模式：{'📍 航点模式（点击地图加航点）' if st.session_state.map_click_mode == 'waypoint' else '🚧 障碍物模式（点击地图加顶点）'}")
        
        mode1, mode2 = st.columns(2)
        with mode1:
            if st.button("📍 航点模式", type="primary" if st.session_state.map_click_mode == "waypoint" else "secondary"):
                st.session_state.map_click_mode = "waypoint"
                st.rerun()
        with mode2:
            if st.button("🚧 障碍物模式", type="primary" if st.session_state.map_click_mode == "obstacle" else "secondary"):
                st.session_state.map_click_mode = "obstacle"
                st.rerun()

        st.markdown("---")

        tab1, tab2 = st.tabs(["📍 航点管理", "🚧 障碍物管理"])

        with tab1:
            st.subheader("添加航点")

            wp_lat = st.number_input("纬度", value=NANJING_LAT, step=0.0001, format="%.6f", key="wp_lat")
            wp_lng = st.number_input("经度", value=NANJING_LNG, step=0.0001, format="%.6f", key="wp_lng")
            wp_name = st.text_input("名称", placeholder=f"航点{len(data['waypoints'])+1}", key="wp_name")

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("➕ 添加航点", use_container_width=True):
                    name = wp_name if wp_name else f"航点{len(data['waypoints'])+1}"
                    data['waypoints'].append({'lat': wp_lat, 'lng': wp_lng, 'name': name})
                    save_data(data)
                    st.success(f"✅ {name} 添加成功！")

            with col_btn2:
                if st.button("🗑️ 清空航点", use_container_width=True):
                    data['waypoints'] = []
                    save_data(data)
                    st.success("✅ 已清空")

            st.markdown("---")

            if data['waypoints']:
                st.subheader("航点列表")
                for i, wp in enumerate(data['waypoints']):
                    col_wp1, col_wp2 = st.columns([4, 1])
                    with col_wp1:
                        st.write(f"{i+1}. **{wp['name']}**: ({wp['lat']:.6f}, {wp['lng']:.6f})")
                    with col_wp2:
                        if st.button("🗑️", key=f"del_wp_{i}"):
                            del data['waypoints'][i]
                            save_data(data)
                            st.rerun()

        with tab2:
            st.subheader("添加障碍物")

            obs_name = st.text_input("障碍物名称", placeholder="障碍物1", key="obs_name")

            st.markdown(f"**已添加 {len(st.session_state.temp_obstacle)} 个顶点** (需要至少3个)")

            col_obs1, col_obs2 = st.columns(2)
            with col_obs1:
                if st.button("➕ 添加障碍物", use_container_width=True):
                    if len(st.session_state.temp_obstacle) >= 3:
                        name = obs_name if obs_name else f"障碍物{len(data['obstacles'])+1}"
                        data['obstacles'].append({'name': name, 'coords': st.session_state.temp_obstacle.copy()})
                        save_data(data)
                        st.success(f"✅ {name} 添加成功！")
                        st.session_state.temp_obstacle = []
                    else:
                        st.warning("⚠️ 需要至少3个顶点")

            with col_obs2:
                if st.button("🔄 重置顶点", use_container_width=True):
                    st.session_state.temp_obstacle = []
                    st.rerun()

            if st.button("🗑️ 清空所有障碍物", use_container_width=True):
                data['obstacles'] = []
                save_data(data)
                st.success("✅ 已清空")

            st.markdown("---")

            if st.session_state.temp_obstacle:
                st.subheader("当前顶点")
                for i, coord in enumerate(st.session_state.temp_obstacle):
                    st.write(f"{i+1}. ({coord[0]:.6f}, {coord[1]:.6f})")

            if data['obstacles']:
                st.subheader("障碍物列表")
                for i, obs in enumerate(data['obstacles']):
                    col_obs_n, col_obs_d = st.columns([4, 1])
                    with col_obs_n:
                        st.write(f"{i+1}. **{obs['name']}** ({len(obs['coords'])}个顶点)")
                    with col_obs_d:
                        if st.button("🗑️", key=f"del_obs_{i}"):
                            del data['obstacles'][i]
                            save_data(data)
                            st.rerun()

        st.markdown("---")

        col_stat1, col_stat2 = st.columns(2)
        with col_stat1:
            st.metric("航点数量", len(data['waypoints']))
        with col_stat2:
            if len(data['waypoints']) >= 2:
                total_dist = 0
                for i in range(len(data['waypoints']) - 1):
                    lat1, lng1 = data['waypoints'][i]['lat'], data['waypoints'][i]['lng']
                    lat2, lng2 = data['waypoints'][i+1]['lat'], data['waypoints'][i+1]['lng']
                    total_dist += math.sqrt((lat2-lat1)**2 + (lng2-lng1)**2) * 111
                st.metric("航线距离", f"{total_dist:.2f} km")

    with col2:
        st.subheader("🗺️ 卫星地图")

        center_lat, center_lng = NANJING_LAT, NANJING_LNG
        all_points = []
        for wp in data['waypoints']:
            all_points.append((wp['lat'], wp['lng']))
        for obs in data['obstacles']:
            for coord in obs['coords']:
                all_points.append(coord)
        if all_points:
            center_lat = sum(p[0] for p in all_points) / len(all_points)
            center_lng = sum(p[1] for p in all_points) / len(all_points)

        m = create_satellite_map(center_lat, center_lng)

        if len(data['waypoints']) >= 2:
            route_coords = [(wp['lat'], wp['lng']) for wp in data['waypoints']]
            folium.PolyLine(route_coords, color='#3366FF', weight=4, opacity=0.8).add_to(m)

        for i, wp in enumerate(data['waypoints']):
            color = 'green' if i == 0 else ('red' if i == len(data['waypoints'])-1 else 'blue')
            folium.Marker([wp['lat'], wp['lng']], popup=f"{wp['name']} ({wp['lat']:.6f}, {wp['lng']:.6f})", icon=folium.Icon(color=color, icon='info-sign')).add_to(m)

        for obs in data['obstacles']:
            folium.Polygon(obs['coords'], color='#FF6B6B', fill=True, fillColor='#FF6B6B', fillOpacity=0.3, weight=2, popup=obs['name']).add_to(m)

        if len(st.session_state.temp_obstacle) >= 1:
            for coord in st.session_state.temp_obstacle:
                folium.CircleMarker(coord, radius=8, color='#FF6B6B', fill=True, fillColor='#FF6B6B', fillOpacity=1).add_to(m)
        if len(st.session_state.temp_obstacle) >= 2:
            folium.PolyLine(st.session_state.temp_obstacle, color='#FF6B6B', weight=2, dash_array='5,5').add_to(m)
        if len(st.session_state.temp_obstacle) >= 3:
            folium.Polygon(st.session_state.temp_obstacle, color='#FFA500', fill=True, fillColor='#FFA500', fillOpacity=0.3, weight=2).add_to(m)

        map_output = st_folium(m, width=700, height=600, key="main_map")

        if map_output and map_output.get('last_clicked'):
            lat = map_output['last_clicked'].get('lat')
            lng = map_output['last_clicked'].get('lng')
            if lat and lng:
                if st.session_state.map_click_mode == 'waypoint':
                    new_wp_name = f"航点{len(data['waypoints'])+1}"
                    data['waypoints'].append({'lat': lat, 'lng': lng, 'name': new_wp_name})
                    save_data(data)
                    st.success(f"✅ {new_wp_name} 已添加到地图点击位置！")
                    st.rerun()
                else:
                    st.session_state.temp_obstacle.append((lat, lng))
                    st.success(f"✅ 已添加第 {len(st.session_state.temp_obstacle)} 个顶点！")
                    st.rerun()

def render_flight_monitor_page():
    st.header("🚁 飞行监控")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("🎮 模拟控制")

        if st.button("▶️ 启动模拟", use_container_width=True):
            st.session_state.is_simulating = True
            st.session_state.heartbeat_data = []
            st.session_state.flight_path = []
            st.session_state.battery_level = 100.0
            st.success("✅ 模拟已启动")

        if st.button("⏹️ 停止模拟", use_container_width=True):
            st.session_state.is_simulating = False
            st.success("✅ 模拟已停止")

        st.markdown("---")

        if st.session_state.heartbeat_data:
            last_hb = st.session_state.heartbeat_data[-1]
            st.metric("心跳序号", last_hb['seq'])
            st.metric("电池电量", f"{st.session_state.battery_level:.1f}%")
            st.metric("当前位置", f"({st.session_state.current_position[0]:.6f}, {st.session_state.current_position[1]:.6f})")

    with col2:
        st.subheader("🗺️ 飞行轨迹")

        m = create_satellite_map(st.session_state.current_position[0], st.session_state.current_position[1])

        data = st.session_state.data
        if data['waypoints']:
            route_coords = [(wp['lat'], wp['lng']) for wp in data['waypoints']]
            folium.PolyLine(route_coords, color='#FFA500', weight=3, opacity=0.7).add_to(m)

            for i, wp in enumerate(data['waypoints']):
                color = 'green' if i == 0 else ('red' if i == len(data['waypoints'])-1 else 'orange')
                folium.Marker([wp['lat'], wp['lng']], popup=f"{wp['name']}", icon=folium.Icon(color=color, icon='info-sign')).add_to(m)

        if len(st.session_state.flight_path) > 1:
            folium.PolyLine(st.session_state.flight_path, color='#3366FF', weight=4, opacity=0.9).add_to(m)

        if st.session_state.flight_path:
            folium.Marker(
                st.session_state.flight_path[-1],
                popup="✈️ 当前位置",
                icon=folium.Icon(color='blue', icon='plane', prefix='glyphicon')
            ).add_to(m)

        st_folium(m, width=700, height=500)

    if st.session_state.is_simulating:
        import time
        time.sleep(1)

        seq = len(st.session_state.heartbeat_data) + 1
        st.session_state.heartbeat_data.append({'seq': seq, 'time': datetime.now().strftime("%H:%M:%S")})
        st.session_state.battery_level = max(0, st.session_state.battery_level - 0.02)

        lat = st.session_state.current_position[0] + (random.random() - 0.5) * 0.0001
        lng = st.session_state.current_position[1] + (random.random() - 0.5) * 0.0001
        st.session_state.current_position = [lat, lng]
        st.session_state.flight_path.append((lat, lng))

        st.rerun()

def main():
    init_session_state()

    st.sidebar.markdown("<h2 style='color: #00D4AA; text-align: center;'>🚁 UAV Monitor</h2>", unsafe_allow_html=True)
    st.sidebar.markdown("---")

    page = st.sidebar.radio("导航", ["🏠 首页", "🗺️ 航线规划", "🚁 飞行监控"])

    if page == "🏠 首页":
        render_home_page()
    elif page == "🗺️ 航线规划":
        render_route_planning_page()
    elif page == "🚁 飞行监控":
        render_flight_monitor_page()

if __name__ == "__main__":
    main()
