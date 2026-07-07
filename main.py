import sqlite3
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from datetime import datetime, timedelta

# 🌟 핵심: 우리가 방금 만든 '자재 창고(data.py)'에서 골프장 리스트를 불러옵니다!
from data import premium_courses

app = FastAPI()

@app.get("/api/golf-courses")
def get_courses():
    return premium_courses

@app.get("/api/tee-times/{course_id}/{date}")
def get_tee_times(course_id: int, date: str):
    times = []
    start_time_1 = datetime.strptime("07:00", "%H:%M")
    for i in range(0, 120, 10):
        t = (start_time_1 + timedelta(minutes=i)).strftime("%H:%M")
        status = "booked" if (course_id + int(date[-1]) + i) % 3 == 0 else "available"
        times.append({"time": t, "status": status})
    
    start_time_2 = datetime.strptime("13:00", "%H:%M")
    for i in range(0, 120, 10):
        t = (start_time_2 + timedelta(minutes=i)).strftime("%H:%M")
        status = "booked" if (course_id + int(date[-1]) + i) % 4 == 0 else "available"
        times.append({"time": t, "status": status})
        
    return {"times": times}

@app.get("/web", response_class=HTMLResponse)
def show_webpage():
    return """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>프리미엄 골프 예약 시스템</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css" />
        <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css" />
        
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
        <style> 
            body { background-color: #f4f7f6; font-family: 'Malgun Gothic', sans-serif;}
            #map { height: 450px; width: 100%; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); z-index: 1;}
            .detail-section { display: none; background: white; border-radius: 15px; margin-top: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); overflow: hidden;}
            .hero-img { width: 100%; height: 320px; object-fit: cover; }
            .tee-time-btn { margin: 5px; padding: 10px; border-radius: 8px; border: 1px solid #ddd; width: 85px; text-align: center; font-size: 0.9em; transition: 0.2s;}
            .available { background-color: #e8f5e9; color: #2e7d32; cursor: pointer; }
            .available:hover { background-color: #c8e6c9; font-weight: bold; }
            .booked { background-color: #ffebee; color: #c62828; cursor: not-allowed; text-decoration: line-through; opacity: 0.6; }
        </style>
    </head>
    <body>
        <div class="container mt-4">
            <h3 class="fw-bold mb-3 text-center" style="color: #1e3c72;">⛳ 전국 프리미엄 명문 구장 예약</h3>
            
            <div id="map"></div>

            <div id="detail-view" class="detail-section pb-4">
                <img id="course-image" src="" class="hero-img" alt="골프장 대표 이미지">
                <div class="p-4">
                    <h2 id="course-name" class="fw-bold" style="color: #1e3c72;">골프장 이름</h2>
                    <p id="course-desc" class="text-muted lh-lg mt-3" style="font-size: 1.05rem;"></p>
                    <hr class="my-4">
                    
                    <h5 class="fw-bold mb-3">🕒 실시간 티타임 예약</h5>
                    <label class="mb-2 text-primary fw-bold">📅 티업 날짜 선택</label>
                    <input type="date" id="date-picker" class="form-control mb-4" style="max-width: 250px;" onchange="handleDateChange()">
                    
                    <div id="tee-time-list" class="d-flex flex-wrap bg-light p-3 rounded border"></div>
                </div>
            </div>
        </div>

        <script>
            const map = L.map('map').setView([36.2, 127.7], 7);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
            const markers = L.markerClusterGroup();
            
            let currentCourseId = null;

            fetch('/api/golf-courses')
                .then(r => r.json())
                .then(data => {
                    data.forEach(g => {
                        const marker = L.marker([g.lat, g.lng]);
                        marker.on('click', function() {
                            currentCourseId = g.id;
                            
                            document.getElementById('detail-view').style.display = 'block';
                            document.getElementById('course-name').innerText = g.name;
                            document.getElementById('course-desc').innerText = g.desc;
                            
                            // 🌟 이미지 호출 방식 개선: 이미지가 꼬이지 않도록 즉각 새로고침
                            const imgElem = document.getElementById('course-image');
                            imgElem.src = g.image; 
                            
                            const today = new Date().toISOString().split('T')[0];
                            document.getElementById('date-picker').value = today;
                            fetchTeeTimes(g.id, today);
                            
                            document.getElementById('detail-view').scrollIntoView({ behavior: 'smooth' });
                        });
                        markers.addLayer(marker);
                    });
                    map.addLayer(markers);
                });

            function handleDateChange() {
                const date = document.getElementById('date-picker').value;
                if(currentCourseId && date) {
                    fetchTeeTimes(currentCourseId, date);
                }
            }

            function fetchTeeTimes(courseId, date) {
                const list = document.getElementById('tee-time-list');
                list.innerHTML = '<p class="text-primary fw-bold w-100 text-center py-3">실시간 티업 데이터를 호출하는 중입니다...</p>';
                
                fetch(`/api/tee-times/${courseId}/${date}`)
                    .then(r => r.json())
                    .then(data => {
                        list.innerHTML = '';
                        data.times.forEach(t => {
                            const btn = document.createElement('div');
                            btn.className = `tee-time-btn ${t.status}`;
                            btn.innerText = t.time;
                            if(t.status === 'booked') {
                                btn.innerText += '\\n(마감)';
                            } else {
                                btn.onclick = () => alert(`${document.getElementById('course-name').innerText}\\n${date} ${t.time} 예약 창으로 연결됩니다.`);
                            }
                            list.appendChild(btn);
                        });
                    });
            }
        </script>
    </body>
    </html>
    """
