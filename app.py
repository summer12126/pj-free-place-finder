import streamlit as st
import streamlit.components.v1 as components
import os, json
from dotenv import load_dotenv
load_dotenv()
# 페이지 설정
st.set_page_config(page_title="카카오맵 예제", layout="wide")
st.title("카카오맵 예제")

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
components.html(map_html, height=500)