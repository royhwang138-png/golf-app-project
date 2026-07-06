import sqlite3
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()

def init_db():
    conn = sqlite3.connect('golf_app.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reservations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, course_name TEXT, user_name TEXT, date TEXT)''')
    conn.commit()
    conn.close()

init_db()

golf_courses = [
    {"id": 1, "name": "신한CC", "location": "서울", "lat": 37.5665, "lng": 126.9780},
    {"id": 2, "name": "드림골프장", "location": "경기", "lat": 37.2752, "lng": 127.0095},
    {"id": 3, "name": "파인힐스", "location": "강원", "lat": 37.8813, "lng": 127.7298}
]

class ReservationForm(BaseModel):
    course_name: str
    user_name: str
    date: str

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
            <style>
                body { background-color: #f8f9fa; font-family: 'Malgun Gothic', sans-serif; }
                .hero-section { background: linear-gradient(135deg, #0b1a40 0%, #1a3673 100%); color: white; padding: 40px 0; border-radius: 0 0 20px 20px; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
                .card { border: none; border-radius: 15px; box-shadow: 0 6px 12px rgba(0,0,0,0.05); }
                .btn-primary { background-color: #0b1a40; border: none; }
                .map-wrapper { border-radius: 15px; overflow: hidden; display: none; margin-bottom: 20px;}
                .weather-badge { display: inline-block; background-color: #e3f2fd; color: #0277bd; padding: 5px 10px; border-radius: 8px; font-weight: bold; margin-bottom: 15px; font-size: 0.9em; }
            </style>
        </head>
        <body>
            <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm">
                <div class="container">
                    <a class="navbar-brand text-primary fw-bold" href="#" style="color: #0b1a40 !important;">⛳ 프리미엄 예약</a>
                    <button class="btn btn-outline-warning fw-bold" onclick="loadMyPage()">나의 예약 내역</button>
                </div>
            </nav>

            <div class="hero-section text-center">
                <div class="container">
                    <h1 class="display-6 fw-bold mb-3">최상의 라운딩을 경험하세요</h1>
                    <div class="row justify-content-center">
                        <div class="col-md-6 col-sm-10">
                            <div class="input-group input-group-lg shadow-sm">
                                <input type="text" id="location-input" class="form-control" placeholder="지역 입력 (예: 서울)">
                                <button class="btn btn-primary px-4" onclick="loadGolfCourses()">검색</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="container pb-5">
                <div id="map-container" class="map-wrapper">
                    <iframe id="map-frame" width="100%" height="350" style="border:0;"></iframe>
                </div>
                <div id="content-area" class="row g-4"></div>
            </div>

            <script>
                async function loadGolfCourses() {
                    const loc = document.getElementById('location-input').value;
                    let url = '/search';
                    if (loc) { url = '/search?location=' + loc; }

                    const response = await fetch(url);
                    const data = await response.json();
                    
                    const contentArea = document.getElementById('content-area');
                    const mapContainer = document.getElementById('map-container');
                    const mapFrame = document.getElementById('map-frame');
                    contentArea.innerHTML = ""; 
                    
                    if (data.result.length === 0) {
                        contentArea.innerHTML = "<h4 class='text-muted text-center mt-5 w-100'>해당 지역에는 골프장이 없습니다.</h4>";
                        mapContainer.style.display = 'none'; return;
                    }

                    const first = data.result[0];
                    const bbox = `${first.lng - 0.02},${first.lat - 0.02},${first.lng + 0.02},${first.lat + 0.02}`;
                    mapFrame.src = `https://www.openstreetmap.org/export/embed.html?bbox=${bbox}&layer=mapnik&marker=${first.lat},${first.lng}`;
                    mapContainer.style.display = 'block';

                    // 🌟 날씨 API 연동: 외부 전문가에게 날씨 물어보기
                    for (const c of data.result) {
                        let weatherHtml = "<div class='weather-badge'>☁️ 날씨 정보 불러오는 중...</div>";
                        
                        try {
                            const weatherRes = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${c.lat}&longitude=${c.lng}&current_weather=true`);
                            const weatherData = await weatherRes.json();
                            const temp = weatherData.current_weather.temperature;
                            weatherHtml = `<div class='weather-badge'>🌡️ 실시간 기온: ${temp}°C</div>`;
                        } catch (error) {
                            weatherHtml = `<div class='weather-badge'>⚠️ 날씨 정보 일시 오류</div>`;
                        }

                        contentArea.innerHTML += `
                            <div class="col-md-4 col-sm-6">
                                <div class="card h-100 p-3">
                                    <div class="card-body">
                                        <h4 class="card-title fw-bold">🏌️‍♂️ ${c.name}</h4>
                                        <h6 class="card-subtitle mb-3 text-muted">📍 위치: ${c.location}</h6>
                                        ${weatherHtml}
                                        <input type="text" id="name-${c.id}" class="form-control mb-2" placeholder="예약자 성함">
                                        <input type="date" id="date-${c.id}" class="form-control mb-2">
                                        <button class="btn btn-success w-100 fw-bold" onclick="bookCourse(${c.id}, '${c.name}')">예약 확정하기</button>
                                    </div>
                                </div>
                            </div>
                        `;
                    }
                }

                function bookCourse(id, cName) {
                    const uName = document.getElementById(`name-${id}`).value;
                    const date = document.getElementById(`date-${id}`).value;
                    if(!uName || !date) { alert("입력해주세요!"); return; }

                    fetch('/book', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ course_name: cName, user_name: uName, date: date })
                    }).then(r => r.json()).then(data => { alert(data.message); });
                }

                function loadMyPage() {
                    document.getElementById('map-container').style.display = 'none'; 
                    fetch('/my-reservations').then(r => r.json()).then(data => {
                        const contentArea = document.getElementById('content-area');
                        contentArea.innerHTML = "<h3 class='fw-bold w-100 mb-3'>🗓️ 나의 예약 내역</h3>";
                        if (data.result.length === 0) { contentArea.innerHTML += "<p>예약 내역이 없습니다.</p>"; return; }
                        data.result.forEach(res => {
                            contentArea.innerHTML += `
                                <div class="col-md-6">
                                    <div class="card p-3 border-warning border-2 border-start-0 border-end-0 border-bottom-0">
                                        <h5 class="fw-bold">🎫 ${res.course_name}</h5>
                                        <p class="mb-0">👤 예약자: ${res.user_name} | 📅 예약일: ${res.date}</p>
                                    </div>
                                </div>
                            `;
                        });
                    });
                }
            </script>
        </body>
    </html>
    """

@app.get("/search")
def search_golf(location: str = None):
    if location: return {"result": [c for c in golf_courses if c["location"] == location]}
    return {"result": golf_courses}

@app.post("/book")
def make_reservation(form: ReservationForm):
    conn = sqlite3.connect('golf_app.db')
    c = conn.cursor()
    c.execute("INSERT INTO reservations (course_name, user_name, date) VALUES (?, ?, ?)", (form.course_name, form.user_name, form.date))
    conn.commit()
    conn.close()
    return {"message": f"🎉 성공! {form.user_name}님, 정상적으로 예약이 확정되었습니다!"}

@app.get("/my-reservations")
def get_my_reservations():
    conn = sqlite3.connect('golf_app.db')
    conn.row_factory = sqlite3.Row 
    c = conn.cursor()
    c.execute("SELECT * FROM reservations ORDER BY id DESC")
    result = [{"course_name": r["course_name"], "user_name": r["user_name"], "date": r["date"]} for r in c.fetchall()]
    conn.close()
    return {"result": result}

@app.delete("/cancel/{res_id}")
def cancel_reservation(res_id: int):
    conn = sqlite3.connect('golf_app.db')
    c = conn.cursor()
    c.execute("DELETE FROM reservations WHERE id = ?", (res_id,))
    conn.commit()
    conn.close()
    return {"message": "예약이 성공적으로 취소되었습니다."}

@app.get("/admin", response_class=HTMLResponse)
def show_admin_page():
    conn = sqlite3.connect('golf_app.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM reservations ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    
    html_content = """
    <!DOCTYPE html>
    <html lang="ko">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>시스템 통합 관리자</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body class="bg-light p-4">
            <h2 class="fw-bold mb-4">⚙️ 시스템 통합 관리자 대시보드</h2>
            <div class="table-responsive bg-white p-3 rounded shadow-sm">
                <table class="table table-hover align-middle">
                    <thead class="table-light">
                        <tr><th>ID</th><th>골프장명</th><th>예약자 성함</th><th>예약 날짜</th><th>관리</th></tr>
                    </thead>
                    <tbody>
    """
    for r in rows:
        html_content += f"""
                        <tr>
                            <td>{r['id']}</td><td>{r['course_name']}</td><td>{r['user_name']}</td><td>{r['date']}</td>
                            <td><button class="btn btn-sm btn-danger" onclick="cancelReservation({r['id']})">예약 취소</button></td>
                        </tr>
        """
    html_content += """
                    </tbody>
                </table>
            </div>
            <script>
                function cancelReservation(id) {
                    if(confirm("삭제하시겠습니까?")) {
                        fetch('/cancel/' + id, { method: 'DELETE' }).then(r => r.json()).then(data => { alert(data.message); location.reload(); });
                    }
                }
            </script>
        </body>
    </html>
    """
    return html_content
