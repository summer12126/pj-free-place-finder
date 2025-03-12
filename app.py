import streamlit as st
import pandas as pd
from st_supabase_connection import SupabaseConnection
import json

# 페이지 설정
st.set_page_config(page_title="SpaceFinder Seoul", layout="wide")
st.title("SpaceFinder Seoul")

# Supabase 연결 설정
conn = st.connection("supabase", type=SupabaseConnection)

# 검색 필터 UI
col1, col2 = st.columns([3, 1])
with col1:
    search_query = st.text_input("지역구 검색 (예: 서초구)", placeholder="예: 서초구")
with col2:
    search_button = st.button("검색", type="primary")

# 필터 옵션
filter_cols = st.columns(4)
with filter_cols[0]:
    free_space = st.checkbox("무료 공간")
with filter_cols[1]:
    large_capacity = st.checkbox("50인 이상")
with filter_cols[2]:
    parking = st.checkbox("주차가능")
with filter_cols[3]:
    subway = st.checkbox("지하철역 5분거리")

# 필터 조건 구성
filters = []
if free_space:
    filters.append("'무료대여' = ANY(features)")
if large_capacity:
    filters.append("capacity >= 50")
if parking:
    filters.append("'주차가능' = ANY(features)")
if subway:
    filters.append("'지하철역 도보 5분' = ANY(features)")

# 검색 쿼리 구성
where_clause = " AND ".join(filters)
if search_query:
    if where_clause:
        where_clause = f"address LIKE '%{search_query}%' AND ({where_clause})"
    else:
        where_clause = f"address LIKE '%{search_query}%'"

# 데이터 쿼리
query = f"""
SELECT 
    id, name, address, capacity, open_hours, features,
    ST_X(location::geometry) as longitude,
    ST_Y(location::geometry) as latitude
FROM spaces
{f"WHERE {where_clause}" if where_clause else ""}
"""

# 데이터 가져오기
spaces = conn.query(query, ttl="10m").execute()
spaces_df = pd.DataFrame(spaces.data)

# 카카오맵 표시
st.markdown("""
<div id="map" style="width:100%;height:500px;"></div>
<script type="text/javascript" src="//dapi.kakao.com/v2/maps/sdk.js?appkey=발급받은_API키를_입력하세요"></script>
<script>
    var container = document.getElementById('map');
    var options = {
        center: new kakao.maps.LatLng(37.566826, 126.9786567),
        level: 7
    };
    var map = new kakao.maps.Map(container, options);
    
    // 마커 데이터 설정
    var positions = %s;
    
    // 마커 생성
    positions.forEach(function(position) {
        var marker = new kakao.maps.Marker({
            map: map,
            position: new kakao.maps.LatLng(position.latitude, position.longitude),
            title: position.name
        });
        
        // 인포윈도우 생성
        var infowindow = new kakao.maps.InfoWindow({
            content: '<div style="padding:5px;width:200px;">' + 
                     '<strong>' + position.name + '</strong><br>' +
                     '수용인원: ' + position.capacity + '명<br>' +
                     '운영시간: ' + position.open_hours + '</div>'
        });
        
        // 마커 클릭 이벤트
        kakao.maps.event.addListener(marker, 'click', function() {
            infowindow.open(map, marker);
        });
    });
</script>
""" % json.dumps(spaces_df.to_dict('records')), unsafe_allow_html=True)

# 공간 목록 표시
if not spaces_df.empty:
    for _, space in spaces_df.iterrows():
        with st.container():
            st.subheader(space['name'])
            st.write(f"주소: {space['address']}")
            st.write(f"수용인원: {space['capacity']}명")
            st.write(f"운영시간: {space['open_hours']}")
            st.write(f"특징: {', '.join(space['features'])}")
            st.divider()
else:
    st.info("검색 결과가 없습니다.")
