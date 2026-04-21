import streamlit as st

from route_planning import render_route_planning_page
from flight_monitor import render_flight_monitor_page

st.set_page_config(
    page_title="无人机智能化应用系统",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 1rem;">
        <h2 style="color: #00D4AA;">🚁 UAV Monitor</h2>
        <p style="color: #888; font-size: 0.9rem;">无人机智能化应用系统</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio(
        "功能导航",
        ["🏠 首页", "🗺️ 航线规划", "🚁 飞行监控"],
        label_visibility="collapsed"
    )
    
    st.sidebar.markdown("---")
    
    with st.sidebar.expander("ℹ️ 系统信息"):
        st.markdown("""
        **版本**: v1.0.0
        
        **功能模块**:
        - 航线规划（含坐标转换）
        - 飞行监控
        - 心跳检测
        
        **技术栈**:
        - Streamlit
        - Plotly
        - OpenStreetMap
        """)
    
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 1rem; color: #666; font-size: 0.8rem;">
        南京科技职业学院<br>
        无人机智能化应用项目
    </div>
    """, unsafe_allow_html=True)
    
    if page == "🏠 首页":
        render_home_page()
    elif page == "🗺️ 航线规划":
        render_route_planning_page()
    elif page == "🚁 飞行监控":
        render_flight_monitor_page()

def render_home_page():
    st.markdown("""
    <style>
        .main-header { font-size: 2.5rem; font-weight: bold; color: #00D4AA; text-align: center; margin-bottom: 1rem; }
        .sub-header { font-size: 1.2rem; color: #888; text-align: center; margin-bottom: 2rem; }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-header">🚁 无人机智能化应用系统</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">UAV Intelligent Application System</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🗺️ 航线规划
        
        - 地图展示（支持普通地图和卫星地图）
        - A/B点坐标设置（中国范围）
        - 障碍物标记与记忆
        - 航线距离计算
        - 坐标转换（WGS-84 ↔ GCJ-02）
        """)
        if st.button("进入航线规划", key="goto_route"):
            st.session_state.page = "🗺️ 航线规划"
            st.rerun()
    
    with col2:
        st.markdown("""
        ### 🚁 飞行监控
        
        - 心跳包实时监控（每秒）
        - 掉线检测报警（3秒阈值）
        - 电池电量监控
        - 飞行姿态显示
        - 导航日志记录
        """)
        if st.button("进入飞行监控", key="goto_monitor"):
            st.session_state.page = "🚁 飞行监控"
            st.rerun()
    
    st.markdown("---")
    
    st.markdown("### 📊 系统特性")
    
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    
    with col_f1:
        st.metric("心跳间隔", "1秒/次")
    with col_f2:
        st.metric("离线阈值", "3秒")
    with col_f3:
        st.metric("数据缓存", "1000条")
    with col_f4:
        st.metric("坐标精度", "6位小数")
    
    st.markdown("---")
    
    st.markdown("""
    ### 📖 使用说明
    
    1. **航线规划**: 设置地图中心点，输入起点A和终点B坐标，在地图上查看航线。支持坐标转换功能。
    2. **飞行监控**: 点击"启动模拟"开始心跳包模拟，实时查看无人机状态。点击"模拟离线5秒"测试报警功能。
    
    > 💡 提示: 地图使用OpenStreetMap，无需API Key
    """)
    
    st.markdown("---")
    
    st.markdown("""
    <div style="text-align: center; color: #888; padding: 2rem;">
        <p>© 2024 南京科技职业学院 | 无人机智能化应用项目</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()