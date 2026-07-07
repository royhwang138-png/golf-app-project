import sqlite3
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from datetime import datetime, timedelta

# 📁 자재 창고(data.py)에서 전국 골프장 리스트를 가져옵니다.
from data import premium_courses

app = FastAPI()

# 💾 실시간 예약 장부 (서버 메모리 데이터베이스)
reservations_db = []

@app.get("/api/golf-courses")
def get_courses():
    return premium_courses

@app.get("/api/tee-times/{course_id}/{date}")
def get_tee_times(course_id: int, date: str):
    times = []
    start_time_1 = datetime.strptime("07:00", "%H:%M")
    for i in range(0, 120, 10):
        t = (start_time_1 + timedelta(minutes=i)).strftime("%H:%M")
        # 장부에 이미 예약된 시간인지 확인하는 로직
        is_booked = any(r for r in reservations_db if r["course_id"] == course_id and r["date"] == date and r["time"] == t)
        status = "booked" if is_booked else ("booked" if (course_id + int(date[-1]) + i) % 3 == 0 else "available")
        times.append({"time": t, "status": status})
    return {"times": times}

# 📡 사용자의 예약 요청을 처리하는 서버 창구 (POST API)
@app.post("/api/reserve")
def make_reservation(data: dict):
    if not data.get("booker_name") or not data.get("phone"):
        return {"success": False, "message": "필수 입력 항목이 누락되었습니다."}
    
    reservation_id = len(reservations_db) + 1
    new_booking = {
        "id": reservation_id,
        "course_id": int(data.get("course_id")),
        "date": data.get("date"),
        "time": data.get("time"),
        "booker_name": data.get("booker_name"),
        "phone": data.get("phone")
    }
    reservations_db.append(new_booking)
    return {"success": True, "reservation_id": f"RES-{reservation_id:04d}"}

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
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <style> 
            body { background-color: #f4f7f6; font-family: 'Malgun Gothic', sans-serif;}
            #map { height: 450px; width: 100%; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); z-index: 1;}
            .detail-section { display: none; background: white; border-radius: 15px; margin-top: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); overflow: hidden;}
            .hero-img { width: 100%; height: 320px; object-fit: cover; }
            .tee-time-btn { margin: 5px; padding: 10px; border-radius: 8px; border: 1px solid #ddd; width: 85px; text-align: center; font-size: 0.9em; transition: 0.2s;}
            .available { background-color: #e8f5e9; color: #2e7d32; cursor: pointer; }
            .available:hover { background-color: #c8e6c9; font-weight: bold; }
            .booked { background-color: #ffebee; color: #c62828; cursor: not-allowed; text-decoration: line-through; opacity: 0.6; }
            .selected-time { background-color: #1e3c72 !important; color: white !important; font-weight: bold; }
            .booking-form { display: none; }
        </style>
    </head>
    <body>
        <div class="container mt-4 mb-5">
            <h3 class="fw-bold mb-3 text-center" style="color: #1e3c72;">⛳ 전국 프리미엄 명문 구장 예약</h3>
            <div id="map"></div>

            <div id="detail-view" class="detail-section pb-4">
                <img id="course-image" src="" class="hero-img">
                <div class="p-4">
                    <h2 id="course-name" class="fw-bold" style="color: #1e3c72;">골프장 이름</h2>
                    <p id="course-desc" class="text-muted lh-lg mt-3" style="font-size: 1.05rem;"></p>
                    <hr class="my-4">
                    
                    <h5 class="fw-bold mb-3">🕒 실시간 티타임 예약</h5>
                    <label class="mb-2 text-primary fw-bold">📅 티업 날짜 선택</label>
                    <input type="date" id="date-picker" class="form-control mb-4" style="max-width: 250px;" onchange="handleDateChange()">
                    
                    <div id="tee-time-list" class="d-flex flex-wrap bg-light p-3 rounded border"></div>

                    <div id="booking-form-section" class="booking-form mt-4 p-4 border rounded bg-white">
                        <h5 class="fw-bold text-dark mb-3">👤 예약자 정보 입력</h5>
                        <p class="text-muted">선택한 티타임: <span id="summary-time" class="badge bg-primary fs-6"></span></p>
                        <div class="mb-3">
                            <label class="form-label fw-bold">예약자명</label>
                            <input type="text" id="booker-name" class="form-control" placeholder="이름을 입력하세요">
                        </div>
                        <div class="mb-3">
                            <label class="form-label fw-bold">연락처</label>
                            <input type="text" id="booker-phone" class="form-control" placeholder="숫자만 입력하세요">
                        </div>
                        <button class="btn btn-success w-100 py-2 fw-bold fs-5" onclick="submitReservation()">예약 확정하기</button>
                    </div>
                </div>
            </div>
        </div>

        <div class="modal fade" id="successModal" tabindex="-1" aria-hidden="true">
          <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content p-3 text-center">
              <div class="modal-body">
                <h2 class="text-success fw-bold mb-2">🎉 예약 완료!</h2>
                <p class="lead mb-4">골프장 예약이 정상적으로 접수되었습니다.</p>
                <div class="bg-light p-3 rounded border text-start mb-4">
                    <p class="mb-1"><strong>예약 번호:</strong> <span id="pop-res-id" class="text-primary fw-bold"></span></p>
                    <p class="mb-1"><strong>골프장:</strong> <span id="pop-course"></span></p>
                    <p class="mb-1"><strong>일시:</strong> <span id="pop-datetime"></span></p>
                    <p class="mb-0"><strong>예약자:</strong> <span id="pop-name"></span></p>
                </div>
                <button type="button" class="btn btn-primary px-5 py-2 fw-bold" data-bs-dismiss="modal">확인</button>
              </div>
            </div>
          </div>
        </div>

        <script>
            const map = L.map('map').setView([36.2, 127.7], 7);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
            const markers = L.markerClusterGroup();
            
            let currentCourseId = null;
            let selectedTime = null;

            fetch('/api/golf-courses')
                .then(r => r.json())
                .then(data => {
                    data.forEach(g => {
                        const marker = L.marker([g.lat, g.lng]);
                        marker.on('click', function() {
                            currentCourseId = g.id;
                            selectedTime = null;
                            document.getElementById('booking-form-section').style.display = 'none';
                            
                            document.getElementById('detail-view').style.display = 'block';
                            document.getElementById('course-name').innerText = g.name;
                            document.getElementById('course-desc').innerText = g.desc;
                            document.getElementById('course-image').src = g.image; 
                            
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
                    selectedTime = null;
                    document.getElementById('booking-form-section').style.display = 'none';
                    fetchTeeTimes(currentCourseId, date);
                }
            }

            function fetchTeeTimes(courseId, date) {
                const list = document.getElementById('tee-time-list');
                list.innerHTML = '<p class="text-primary fw-bold w-100 text-center py-3">실시간 데이터를 호출하는 중입니다...</p>';
                
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
                                btn.onclick = () => {
                                    document.querySelectorAll('.tee-time-btn').forEach(b => b.classList.remove('selected-time'));
                                    btn.classList.add('selected-time');
                                    selectedTime = t.time;
                                    document.getElementById('summary-time').innerText = `${date} ${t.time}`;
                                    document.getElementById('booking-form-section').style.display = 'block';
                                };
                            }
                            list.appendChild(btn);
                        });
                    });
            }

            // 📡 서버에 예약 주문서를 전송하는 함수
            function submitReservation() {
                const name = document.getElementById('booker-name').value;
                const phone = document.getElementById('booker-phone').value;
                const date = document.getElementById('date-picker').value;

                if(!name || !phone) {
                    alert('예약자명과 연락처를 입력해 주세요.');
                    return;
                }

                fetch('/api/reserve', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        course_id: currentCourseId,
                        date: date,
                        time: selectedTime,
                        booker_name: name,
                        phone: phone
                    })
                })
                .then(r => r.json())
                .then(res => {
                    if(res.success) {
                        // 🪟 모달 팝업 데이터 세팅 및 띄우기
                        document.getElementById('pop-res-id').innerText = res.reservation_id;
                        document.getElementById('pop-course').innerText = document.getElementById('course-name').innerText;
                        document.getElementById('pop-datetime').innerText = `${date} ${selectedTime}`;
                        document.getElementById('pop-name').innerText = name;

                        const myModal = new bootstrap.Modal(document.getElementById('successModal'));
                        myModal.show();

                        // 폼 초기화 및 티타임 목록 새로고침
                        document.getElementById('booker-name').value = '';
                        document.getElementById('booker-phone').value = '';
                        document.getElementById('booking-form-section').style.display = 'none';
                        fetchTeeTimes(currentCourseId, date);
                    } else {
                        alert('예약 실패: ' + res.message);
                    }
                });
            }
        </script>
    </body>
    </html>
    """
