import sqlite3
import random
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

# 🌟 전국에 골프장 100개를 가상으로 흩뿌리는 엔진 (나중엔 진짜 DB로 교체됩니다)
national_golf_courses = []
for i in range(1, 101):
    # 대한민국 위도/경도 범위 내에서 무작위 좌표 생성
    lat = 34.0 + random.random() * 3.5
    lng = 126.5 + random.random() * 2.5
    national_golf_courses.append({
        "id": i, 
        "name": f"프리미엄 CC {i}호", 
        "lat": lat, 
        "lng": lng, 
        "desc": "자연 경관이 수려한 18홀 정규 코스입니다."
    })

@app.get("/api/golf-courses")
def get_courses():
    return national_golf_courses

@app.get("/web", response_class=HTMLResponse)
def show_webpage():
    return """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>전국 프리미엄 골프 예약</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <!-- 지도 기능을 위한 외부 부품(라이브러리) -->
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css" />
        <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css" />
        
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
        <style> 
            body { background-color: #f8f9fa; }
            #map { height: 400px; width: 100%; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); z-index: 1;}
            .detail-section { display: none; background: white; border-radius: 15px; margin-top: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); overflow: hidden;}
            .hero-img { width: 100%; height: 250px; object-fit: cover; }
            .tee-time-btn { margin: 5px; padding: 10px; border-radius: 8px; border: 1px solid #ddd; width: 85px; text-align: center; }
            .available { background-color: #e8f5e9; color: #2e7d32; cursor: pointer; }
            .booked { background-color: #ffebee; color: #c62828; cursor: not-allowed; text-decoration: line-through; }
        </style>
    </head>
    <body>
        <div class="container mt-4">
            <h3 class="fw-bold mb-3 text-center">🗺️ 전국 골프장 지도</h3>
            <p class="text-muted text-center">지도를 확대하시거나 숫자가 적힌 동그라미를 눌러보세요!</p>
            
            <!-- 1. 전국 지도 영역 -->
            <div id="map"></div>

            <!-- 2. 핀을 누르면 나타날 골프장 상세페이지 영역 (처음엔 숨겨둠) -->
            <div id="detail-view" class="detail-section pb-4">
                <img src="https://images.unsplash.com/photo-1587300003388-59208cc962cb?auto=format&fit=crop&w=800&q=80" class="hero-img">
                <div class="p-4">
                    <h2 id="course-name" class="fw-bold text-primary">골프장 이름</h2>
                    <p id="course-desc" class="text-muted">골프장 소개글</p>
                    <hr>
                    <h5 class="fw-bold mt-4">⛳ 코스 소개</h5>
                    <p>도전적이고 전략적인 플레이가 요구되는 프리미엄 코스.</p>
                    <hr>
                    <h5 class="fw-bold mt-4">🕒 티타임 예약</h5>
                    <label class="mb-2">날짜 선택</label>
                    <input type="date" class="form-control mb-3" style="max-width: 200px;">
                    <div id="tee-time-list" class="d-flex flex-wrap">
                        <div class="tee-time-btn available">07:30</div>
                        <div class="tee-time-btn booked">08:10</div>
                        <div class="tee-time-btn available">12:40</div>
                        <div class="tee-time-btn available">13:20</div>
                    </div>
                    <button class="btn btn-primary w-100 mt-4 py-2 fw-bold" onclick="alert('예약 화면으로 이동합니다!')">이 골프장 예약하기</button>
                </div>
            </div>
        </div>

        <script>
            // 지도 초기화 (대한민국 중심)
            const map = L.map('map').setView([35.9, 127.7], 6);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

            // 🌟 클러스터링(묶어주기) 그룹 생성
            const markers = L.markerClusterGroup();

            // 서버에서 전국 100개 데이터 불러오기
            fetch('/api/golf-courses')
                .then(r => r.json())
                .then(data => {
                    data.forEach(g => {
                        // 핀 생성
                        const marker = L.marker([g.lat, g.lng]);
                        
                        // 🌟 핀 터치 시 동작 (상세페이지 열기)
                        marker.on('click', function() {
                            document.getElementById('detail-view').style.display = 'block'; // 상세페이지 보이기
                            document.getElementById('course-name').innerText = g.name; // 이름 바꾸기
                            document.getElementById('course-desc').innerText = g.desc; // 소개글 바꾸기
                            
                            // 상세페이지로 부드럽게 화면 스크롤 내려주기
                            document.getElementById('detail-view').scrollIntoView({ behavior: 'smooth' });
                        });

                        markers.addLayer(marker); // 그룹에 핀 추가
                    });
                    
                    map.addLayer(markers); // 지도에 그룹 올리기
                });
        </script>
    </body>
    </html>
    """
