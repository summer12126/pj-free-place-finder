import streamlit as st
from st_supabase_connection import SupabaseConnection
import pandas as pd
import json
import os
from dotenv import load_dotenv
load_dotenv()


# 페이지 설정
st.set_page_config(page_title="SpaceFinder Seoul", layout="wide")
st.title("SpaceFinder Seoul")

# Supabase 연결 초기화
conn = st.connection("supabase", type=SupabaseConnection)

# 검색 UI 구성
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

# 운영시간 표시
st.write("운영시간: 09:00 - 18:00 (월-금)")

# # 공간 데이터 쿼리 구성
# base_query = """
# SELECT 
#     id, name, address, capacity, open_hours, features,
#     ST_X(location::geometry) as longitude,
#     ST_Y(location::geometry) as latitude
# FROM spaces
# """

# # 필터 조건 적용
# filters = []
# if search_query:
#     filters.append(f"address LIKE '%{search_query}%'")
# if free_space:
#     filters.append("'무료대여' = ANY(features)")
# if large_capacity:
#     filters.append("capacity >= 50")
# if parking:
#     filters.append("'주차가능' = ANY(features)")
# if subway:
#     filters.append("'지하철역 도보 5분' = ANY(features)")

# if filters:
#     where_clause = " WHERE " + " AND ".join(filters)
#     full_query = base_query + where_clause
# else:
#     full_query = base_query

# # 데이터 가져오기 - execute_query 메서드 사용
# try:
#     # 최신 API 사용
#     spaces_data = conn.execute_query(full_query, ttl="10m")
#     spaces_df = pd.DataFrame(spaces_data.data) if hasattr(spaces_data, 'data') and spaces_data.data else pd.DataFrame()
# except AttributeError:
#     try:
#         # 대체 API 시도
#         spaces_data = conn.table("spaces").select("*").execute()
#         spaces_df = pd.DataFrame(spaces_data.data) if hasattr(spaces_data, 'data') and spaces_data.data else pd.DataFrame()
        
#         # 필터 적용 (클라이언트 측에서)
#         if search_query:
#             spaces_df = spaces_df[spaces_df['address'].str.contains(search_query, na=False)]
#         if free_space:
#             spaces_df = spaces_df[spaces_df['features'].apply(lambda x: '무료대여' in x if isinstance(x, list) else False)]
#         if large_capacity:
#             spaces_df = spaces_df[spaces_df['capacity'] >= 50]
#         if parking:
#             spaces_df = spaces_df[spaces_df['features'].apply(lambda x: '주차가능' in x if isinstance(x, list) else False)]
#         if subway:
#             spaces_df = spaces_df[spaces_df['features'].apply(lambda x: '지하철역 도보 5분' in x if isinstance(x, list) else False)]
#     except Exception as e:
#         st.error(f"데이터를 가져오는 중 오류가 발생했습니다: {str(e)}")
#         spaces_df = pd.DataFrame()



# 카카오맵 API 키
kakao_key = os.environ.get("KAKAO_MAPS_API_KEY")
# 마커 데이터 (서초문화원 강당 예시)
places = [
    {
        "name": "서초문화원 강당",
        "latitude": 37.5697752,
        "longitude": 126.9877752,
        "capacity": 100,
        "open_hours": "10:00 - 20:00 (월-토)"
    }
]

# 카카오맵 HTML 컴포넌트
map_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>카카오맵 마커 예제</title>
</head>
<body>
    <div id="map" style="width:100%;height:500px;"></div>
    <script type="text/javascript" src="//dapi.kakao.com/v2/maps/sdk.js?appkey={kakao_key}"></script>
    <script>
        var container = document.getElementById('map');
        var options = {{
            center: new kakao.maps.LatLng(37.566826, 126.9786567),
            level: 7
        }};
        var map = new kakao.maps.Map(container, options);
        
        var places = {json.dumps(places)};
        
        places.forEach(function(place) {{
            var marker = new kakao.maps.Marker({{
                map: map,
                position: new kakao.maps.LatLng(place.latitude, place.longitude),
                title: place.name
            }});
            
            var infowindow = new kakao.maps.InfoWindow({{
                content: '<div style="padding:5px;width:200px;"><strong>' + place.name + 
                         '</strong><br>수용인원: ' + place.capacity + '명<br>' +
                         '운영시간: ' + place.open_hours + '</div>'
            }});
            
            kakao.maps.event.addListener(marker, 'click', function() {{
                infowindow.open(map, marker);
            }});
        }});
    </script>
</body>
</html>
"""

# HTML 컴포넌트로 지도 표시
# st.components.html(map_html, height=500)

st.components.v1.html(map_html, height=500)



# 서울시 공공 데이터 정보 표시
st.sidebar.title("프로젝트 정의")
st.sidebar.markdown("""
### 목표
- 공공 대여 공간 데이터를 수집해 지도에 시각화하고 웹 사이트로 배포
- 실패해도 되는 안전한 환경에서 원하는 프로젝트, 기술 경험 쌓기

### 기능
1. 사용자는 지도에서 공공 대여 공간 정보를 조회할 수 있다.
2. 사용자는 지도에서 공공 대여 공간 정보를 검색할 수 있다.
3. 사용자는 지도에서 대여 공간 인근 편의시설 정보를 조회할 수 있다.
""")

# 데이터 출처 표시
st.sidebar.markdown("""
### 데이터 출처
- 서울시 교통빅데이터플랫폼 (오픈 API)
- 소상공인시장진흥공단_상가(상권)정보_20241231
""")
