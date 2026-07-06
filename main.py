import sqlite3
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

# 🌟 전국 주요 명문 골프장 데이터 (핀마커용)
golf_data = [
    {"id": 1, "name": "남서울CC", "lat": 37.3975, "lng": 127.1009, "desc": "대한민국 대표 명문 코스"},
    {"id": 2, "name": "클럽나인브릿지", "lat": 33.3639, "lng": 126.3686, "desc": "제주의 아름다운 자연을 품은 곳"},
    {"id": 3, "name": "우정힐스CC", "lat": 36.7592, "lng": 127.2144, "desc": "전략적인 플레이가 필요한 챌린지 코스"}
]

@app.get("/web", response_class=HTMLResponse)
def show_webpage():
    return """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <style> #map { height: 500px; width: 100%; } </style>
    </head>
    <body>
        <div class="container mt-3">
            <h4 class="fw-bold mb-3">전국 골프장 찾기</h4>
            <div id="map"></div>
        </div>

        <script>
            const map = L.map('map').setView([36.5, 127.5], 7);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

            // 🌟 핀 마커 표시
            const golfs = """ + str(golf_data).replace("'", '"') + """;
            golfs.forEach(g => {
                L.marker([g.lat, g.lng]).addTo(map)
                 .bindPopup(`<b>${g.name}</b><br><button class="btn btn-sm btn-primary mt-1" onclick="alert('상세페이지 연결!')">상세보기</button>`);
            });
        </script>
    </body>
    </html>
    """
