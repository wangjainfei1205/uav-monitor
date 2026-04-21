import streamlit as st
import streamlit.components.v1 as components
import math
import json
import os

NANJING_LAT = 32.234104
NANJING_LNG = 118.749421

x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626
a = 6378245.0
ee = 0.00669342162296594323

def out_of_china(lng, lat):
    if lng < 72.004 or lng > 137.8347:
        return True
    if lat < 0.8293 or lat > 55.8271:
        return True
    return False

def transform_lat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + 0.1 * lng * lat + 0.2 * math.sqrt(abs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 * math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 * math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 * math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret

def transform_lng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + 0.1 * lng * lat + 0.1 * math.sqrt(abs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 * math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 * math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 * math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret

def wgs84_to_gcj02(lng, lat):
    if out_of_china(lng, lat):
        return lng, lat
    dlat = transform_lat(lng - 105.0, lat - 35.0)
    dlng = transform_lng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    return lng + dlng, lat + dlat

def gcj02_to_wgs84(lng, lat):
    if out_of_china(lng, lat):
        return lng, lat
    dlat = transform_lat(lng - 105.0, lat - 35.0)
    dlng = transform_lng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    return lng * 2 - (lng + dlng), lat * 2 - (lat + dlat)

OBSTACLES_FILE = 'obstacles.json'

def save_obstacles(obstacles):
    try:
        with open(OBSTACLES_FILE, 'w', encoding='utf-8') as f:
            json.dump(obstacles, f)
    except Exception as e:
        st.error(f"保存障碍物失败: {e}")

def load_obstacles():
    if os.path.exists(OBSTACLES_FILE):
        try:
            with open(OBSTACLES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def render_route_planning_page():
    st.header("🗺️ 航线规划")

    if 'obstacles' not in st.session_state:
        st.session_state.obstacles = load_obstacles()
    if 'is_drawing' not in st.session_state:
        st.session_state.is_drawing = False

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("📍 坐标设置")
        
        center_lat = st.number_input("中心纬度", min_value=-90.0, max_value=90.0, value=NANJING_LAT, step=0.0001, format="%.6f")
        center_lng = st.number_input("中心经度", min_value=-180.0, max_value=180.0, value=NANJING_LNG, step=0.0001, format="%.6f")

        st.markdown("---")
        st.markdown("**起点A**")
        lat_a = st.number_input("纬度A", min_value=-90.0, max_value=90.0, value=NANJING_LAT, step=0.0001, format="%.6f")
        lng_a = st.number_input("经度A", min_value=-180.0, max_value=180.0, value=NANJING_LNG, step=0.0001, format="%.6f")

        st.markdown("**终点B**")
        lat_b = st.number_input("纬度B", min_value=-90.0, max_value=90.0, value=32.2350, step=0.0001, format="%.6f")
        lng_b = st.number_input("经度B", min_value=-180.0, max_value=180.0, value=118.7500, step=0.0001, format="%.6f")

        st.markdown("---")
        st.subheader("🔄 坐标转换")
        
        tab1, tab2 = st.tabs(["WGS→GCJ", "GCJ→WGS"])
        
        with tab1:
            if st.button("转换A点"):
                gcj_lng, gcj_lat = wgs84_to_gcj02(lng_a, lat_a)
                st.success(f"A点 GCJ-02:\n{gcj_lat:.6f}, {gcj_lng:.6f}")
            if st.button("转换B点"):
                gcj_lng, gcj_lat = wgs84_to_gcj02(lng_b, lat_b)
                st.success(f"B点 GCJ-02:\n{gcj_lat:.6f}, {gcj_lng:.6f}")
        
        with tab2:
            gcj_lat_input = st.text_input("GCJ纬度", placeholder="32.234567")
            gcj_lng_input = st.text_input("GCJ经度", placeholder="118.749012")
            if st.button("逆向转换"):
                try:
                    wgs_lng, wgs_lat = gcj02_to_wgs84(float(gcj_lng_input), float(gcj_lat_input))
                    st.success(f"WGS-84:\n{wgs_lat:.6f}, {wgs_lng:.6f}")
                except ValueError:
                    st.error("请输入有效数字")

        st.markdown("---")
        st.subheader("🚧 障碍物管理")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            draw_btn = st.button(
                "➕ 开始圈选" if not st.session_state.is_drawing else "✓ 完成圈选",
                key="draw",
                type="primary" if st.session_state.is_drawing else "secondary",
                use_container_width=True
            )
            if draw_btn:
                st.session_state.is_drawing = not st.session_state.is_drawing
        
        with col_btn2:
            if st.button("🗑️ 清除全部", use_container_width=True):
                st.session_state.obstacles = []
                save_obstacles([])
                st.success("已清除所有障碍物")

        if st.session_state.is_drawing:
            st.warning("🖱️ 绘制模式: 点击地图添加顶点，双击完成多边形")

        st.markdown(f"**已圈选障碍物: {len(st.session_state.obstacles)} 个**")
        for i, obs in enumerate(st.session_state.obstacles):
            col_obs1, col_obs2 = st.columns([4, 1])
            with col_obs1:
                st.markdown(f"- **{obs.get('name', f'障碍物{i+1}')}**: {len(obs['coords'])} 个顶点")
            with col_obs2:
                if st.button("✕", key=f"del_{i}"):
                    st.session_state.obstacles.pop(i)
                    save_obstacles(st.session_state.obstacles)
                    st.rerun()

    with col2:
        st.subheader("🗺️ 地图视图")
        
        map_type = st.radio("地图类型", ["普通地图", "卫星地图"], horizontal=True)
        
        tile_url = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" if map_type == "普通地图" else "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
        tile_attribution = "© OpenStreetMap contributors" if map_type == "普通地图" else "© Esri"

        obstacles_json = json.dumps(st.session_state.obstacles)
        is_drawing_str = "true" if st.session_state.is_drawing else "false"

        map_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <style>
                html, body, #map { width: 100%; height: 100%; margin: 0; padding: 0; }
                .info { position: absolute; top: 10px; right: 10px; z-index: 1000; background: rgba(255,255,255,0.9); padding: 10px; border-radius: 5px; font-size: 12px; }
                .legend { position: absolute; bottom: 10px; left: 10px; z-index: 1000; background: rgba(255,255,255,0.9); padding: 8px; border-radius: 5px; font-size: 11px; }
                .drawing-hint { position: absolute; top: 10px; left: 10px; z-index: 1000; background: rgba(255,100,100,0.9); padding: 8px 12px; border-radius: 5px; font-size: 12px; color: white; }
            </style>
        </head>
        <body>
            <div id="map"></div>
            <div class="info">
                <div><strong>📍 地图信息</strong></div>
                <div>纬度: <span id="lat">""" + f"{center_lat:.6f}" + """</span></div>
                <div>经度: <span id="lng">""" + f"{center_lng:.6f}" + """</span></div>
                <div>缩放: <span id="zoom">15</span></div>
            </div>
            <div class="legend">
                <div><b>图例</b></div>
                <div>🟢 起点A</div>
                <div>🔴 终点B</div>
                <div>🔵 航线</div>
                <div>🟠 障碍物</div>
            </div>
            <script>
                var map = L.map('map').setView([""" + f"{center_lat}, {center_lng}" + """], 15);
                
                L.tileLayer('""" + tile_url + """', {
                    attribution: '""" + tile_attribution + """',
                    maxZoom: 19
                }).addTo(map);

                L.control.scale({imperial: false}).addTo(map);

                var startIcon = L.icon({
                    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png',
                    iconSize: [25, 41],
                    iconAnchor: [12, 41]
                });
                var endIcon = L.icon({
                    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
                    iconSize: [25, 41],
                    iconAnchor: [12, 41]
                });

                L.marker([""" + f"{lat_a}, {lng_a}" + """], {icon: startIcon}).addTo(map).bindPopup('起点A');
                L.marker([""" + f"{lat_b}, {lng_b}" + """], {icon: endIcon}).addTo(map).bindPopup('终点B');
                L.polyline([[""" + f"{lat_a}, {lng_a}" + """], [""" + f"{lat_b}, {lng_b}" + """]], {color: '#3366FF', weight: 4, dashArray: '10, 10'}).addTo(map);

                var obstacles = """ + obstacles_json + """;
                obstacles.forEach(function(obs, index) {
                    L.polygon(obs.coords, {
                        color: '#FFA500',
                        fillColor: '#FFA500',
                        fillOpacity: 0.3,
                        weight: 2
                    }).addTo(map).bindPopup('障碍物' + (index + 1));
                });

                var drawingMode = """ + is_drawing_str + """;
                var drawingPoints = [];
                var drawingPolyline = null;

                if (drawingMode) {
                    var hint = L.DomUtil.create('div', 'drawing-hint', map.getContainer());
                    hint.innerHTML = '🖱️ 点击添加顶点，双击完成';
                }

                map.on('click', function(e) {
                    if (!drawingMode) return;
                    drawingPoints.push([e.latlng.lat, e.latlng.lng]);
                    if (drawingPolyline) {
                        map.removeLayer(drawingPolyline);
                    }
                    if (drawingPoints.length > 1) {
                        drawingPolyline = L.polyline(drawingPoints, {
                            color: '#FF6B6B',
                            weight: 2,
                            dashArray: '5, 5'
                        }).addTo(map);
                    }
                    L.circleMarker(e.latlng, {
                        radius: 5,
                        color: '#FF6B6B',
                        fillColor: '#FF6B6B',
                        fillOpacity: 1
                    }).addTo(map);
                });

                map.on('dblclick', function(e) {
                    if (!drawingMode || drawingPoints.length < 3) return;
                    drawingPoints.push(drawingPoints[0]);
                    var newObstacle = {
                        name: '障碍物' + (obstacles.length + 1),
                        coords: drawingPoints.slice(0, -1)
                    };
                    L.polygon(newObstacle.coords, {
                        color: '#FFA500',
                        fillColor: '#FFA500',
                        fillOpacity: 0.3,
                        weight: 2
                    }).addTo(map).bindPopup(newObstacle.name);
                    drawingPoints = [];
                    if (drawingPolyline) {
                        map.removeLayer(drawingPolyline);
                        drawingPolyline = null;
                    }
                });

                map.on('zoomend', function() {
                    document.getElementById('zoom').innerText = map.getZoom();
                });
                
                map.on('moveend', function() {
                    var c = map.getCenter();
                    document.getElementById('lat').innerText = c.lat.toFixed(6);
                    document.getElementById('lng').innerText = c.lng.toFixed(6);
                });
            </script>
        </body>
        </html>
        """
        
        components.html(map_html, height=600, scrolling=True)
        
        distance = math.sqrt((lat_b - lat_a)**2 + (lng_b - lng_a)**2) * 111
        st.markdown(f"**📍 当前位置**: {center_lat:.6f}, {center_lng:.6f}")
        st.markdown(f"**📏 航线距离**: {distance:.2f} km")