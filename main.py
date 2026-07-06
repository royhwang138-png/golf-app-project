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

# (임시 더미 데이터) 다음 단계에서 이 부분을 전국 데이터 API로 교체할 예정입니다.
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
            <!-- 🌟 UI 고도화: 예쁜 아이콘 라이브러리 추가 -->
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">
            <style>
                body { background-color: #f4f7f6; font-family: 'Malgun Gothic', sans-serif; }
                .hero-section { background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%); color: white; padding: 50px 0; border-radius: 0 0 30px 30px; margin-bottom: 40px; box-shadow: 0 10px 20px rgba(0,0,0,0.1); }
                .card { border: none; border-radius: 20px; box-shadow: 0 8px 15px rgba(0,0,0,0.05); transition: all 0.3s ease; }
                .card:hover { transform: translateY(-5px); box-shadow: 0 12px 20px rgba(0,0,0,0.1); }
                .btn-primary { background-color: #2c5364; border: none; border-radius: 10px; }
                .btn-primary:hover { background-color: #0f2027; }
                .map-wrapper { border-radius: 20px; overflow: hidden; display: none; margin-bottom: 30px; box-shadow: 0 8px 15px rgba(0,0,0,0.05); border: 2px solid #fff; }
                .weather-badge { display: inline-flex; align-items: center; background-color: #e0f7fa; color: #006064; padding: 6px 12px; border-radius: 20px; font-weight: 600; margin-bottom: 15px; font-size: 0.85em; }
                .login-container { max-width: 420px; margin: 120px auto; background: white; padding: 50px; border-radius: 20px; box-shadow: 0 15px 35px rgba(0,0,0,0.1); text-align: center; }
                /* 🌟 UI 고도화: 로딩 스피너 디자인 */
                .loader-container { display: none; text-align: center; padding: 40px 0; }
            </style>
        </head>
        <body>
            <div id="login-section" class="login-container">
                <i class="bi bi-shield-lock-fill text-primary" style="font-size: 3rem;"></i>
                <h2 class="fw-bold mb-4 mt-3" style="color: #0f2027;">VIP 회원 인증</h2>
                <p class="text-muted mb-4">안전한 서비스 이용을 위해 로그인해 주세요.</p>
                <div class="form-floating mb-3">
                    <input type="text" id="login-id" class="form-control" placeholder="아이디" value="vip">
                    <label for="login-id">아이디</label>
                </div>
                <div class="form-floating mb-4">
                    <input type="password" id="login-pw" class="form-control" placeholder="비밀번호" value="1234">
                    <label for="login-pw">비밀번호</label>
                </div>
                <button class="btn btn-primary w-100 py-3 fw-bold fs-5" onclick="processLogin()">로그인 접속</button>
            </div>

            <div id="main-app-section" style="display: none;">
                <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm py-3">
                    <div class="container d-flex justify-content-between align-items-center">
                        <a class="navbar-brand text-primary fw-bold fs-4" href="#" style="color: #0f2027 !important;"><i class="bi bi-flag-fill me-2"></i>프리미엄 라운딩</a>
                        <div class="d-flex align-items-center">
                            <span id="welcome-msg" class="me-3 fw-bold text-success d-none d-sm-block"></span>
                            <button class="btn btn-outline-warning fw-bold me-2 px-3" onclick="loadMyPage()"><i class="bi bi-calendar-check me-1"></i>내 예약</button>
                            <button class="btn btn-sm btn-secondary px-3" onclick="processLogout()"><i class="bi bi-box-arrow-right me-1"></i>로그아웃</button>
                        </div>
                    </div>
                </nav>

                <div class="hero-section text-center">
                    <div class="container">
                        <h1 class="display-5 fw-bold mb-3">어디로 라운딩을 떠나시나요?</h1>
                        <p class="lead mb-4 opacity-75">실시간 날씨와 함께 최적의 골프장을 찾아드립니다.</p>
                        <div class="row justify-content-center">
                            <div class="col-md-7 col-sm-10">
                                <div class="input-group input-group-lg shadow">
                                    <span class="input-group-text bg-white border-0"><i class="bi bi-search text-muted"></i></span>
                                    <input type="text" id="location-input" class="form-control border-0" placeholder="지역 입력 (예: 서울)">
                                    <button class="btn btn-primary px-4 fw-bold" onclick="loadGolfCourses()">검색하기</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="container pb-5">
                    <!-- 🌟 UI 고도화: 로딩 스피너 UI (통신 중일 때만 표시됨) -->
                    <div id="loading-spinner" class="loader-container">
                        <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;" role="status"></div>
                        <h5 class="mt-3 fw-bold text-secondary">전국 골프장 데이터를 불러오는 중입니다...</h5>
                        <p class="text-muted small">실시간 기상 정보를 함께 수집하고 있습니다.</p>
                    </div>

                    <div id="map-container" class="map-wrapper">
                        <iframe id="map-frame" width="100%" height="400" style="border:0;"></iframe>
                    </div>
                    <div id="content-area" class="row g-4"></div>
                </div>
            </div>

            <script>
                let currentUser = ""; 

                function processLogin() {
                    const id = document.getElementById('login-id').value;
                    const pw = document.getElementById('login-pw').value;
                    if (id === 'vip' && pw === '1234') {
                        currentUser = "VIP회원"; 
                        document.getElementById('login-section').style.display = 'none';
                        document.getElementById('main-app-section').style.display = 'block';
                        document.getElementById('welcome-msg').innerText = "환영합니다, " + currentUser + "님!";
                    } else {
                        alert("❌ 인증 실패: 아이디 또는 비밀번호가 일치하지 않습니다.");
                    }
                }

                function processLogout() {
                    currentUser = "";
                    document.getElementById('main-app-section').style.display = 'none';
                    document.getElementById('login-section').style.display = 'block';
                    document.getElementById('content-area').innerHTML = "";
                    document.getElementById('map-container').style.display = 'none';
                }

                async function loadGolfCourses() {
                    const loc = document.getElementById('location-input').value;
                    let url = '/search';
                    if (loc) { url = '/search?location=' + loc; }

                    const contentArea = document.getElementById('content-area');
                    const mapContainer = document.getElementById('map-container');
                    const spinner = document.getElementById('loading-spinner');
                    
                    // 🌟 통신 시작 전 화면 초기화 및 로딩 스피너 켜기
                    contentArea.innerHTML = ""; 
                    mapContainer.style.display = 'none';
                    spinner.style.display = 'block';

                    try {
                        const response = await fetch(url);
                        const data = await response.json();
                        
                        // 통신 완료 후 로딩 스피너 끄기
                        spinner.style.display = 'none';

                        if (data.result.length === 0) {
                            contentArea.innerHTML = "<div class='col-12 text-center mt-5'><i class='bi bi-emoji-frown fs-1 text-muted'></i><h4 class='text-muted mt-3 fw-bold'>검색 결과가 없습니다.</h4></div>";
                            return;
                        }

                        const first = data.result[0];
                        const bbox = `${first.lng - 0.02},${first.lat - 0.02},${first.lng + 0.02},${first.lat + 0.02}`;
                        document.getElementById('map-frame').src = `https://www.openstreetmap.org/export/embed.html?bbox=${bbox}&layer=mapnik&marker=${first.lat},${first.lng}`;
                        mapContainer.style.display = 'block';

                        for (const c of data.result) {
                            let weatherHtml = "<div class='weather-badge'><i class='bi bi-cloud-arrow-down me-2'></i>날씨 수집 중...</div>";
                            try {
                                const weatherRes = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${c.lat}&longitude=${c.lng}&current_weather=true`);
                                const weatherData = await weatherRes.json();
                                const temp = weatherData.current_weather.temperature;
                                weatherHtml = `<div class='weather-badge'><i class='bi bi-thermometer-half me-1'></i>실시간 기온: ${temp}°C</div>`;
                            } catch (error) {
                                weatherHtml = `<div class='weather-badge bg-light text-danger'><i class='bi bi-exclamation-triangle me-1'></i>날씨 정보 오류</div>`;
                            }

                            contentArea.innerHTML += `
                                <div class="col-lg-4 col-md-6">
                                    <div class="card h-100 p-4">
                                        <h4 class="card-title fw-bold mb-1" style="color: #0f2027;">${c.name}</h4>
                                        <h6 class="card-subtitle mb-3 text-secondary"><i class="bi bi-geo-alt-fill me-1 text-danger"></i>${c.location}</h6>
                                        ${weatherHtml}
                                        <div class="mt-auto">
                                            <div class="input-group mb-2 shadow-sm">
                                                <span class="input-group-text bg-light border-0"><i class="bi bi-person-fill text-secondary"></i></span>
                                                <input type="text" id="name-${c.id}" class="form-control border-0 bg-light" value="${currentUser}" readonly>
                                            </div>
                                            <div class="input-group mb-3 shadow-sm">
                                                <span class="input-group-text bg-light border-0"><i class="bi bi-calendar-event text-secondary"></i></span>
                                                <input type="date" id="date-${c.id}" class="form-control border-0 bg-light">
                                            </div>
                                            <button class="btn btn-success w-100 fw-bold shadow-sm" onclick="bookCourse(${c.id}, '${c.name}')"><i class="bi bi-check-circle me-1"></i>예약 확정</button>
                                        </div>
                                    </div>
                                </div>
                            `;
                        }
                    } catch (error) {
                        spinner.style.display = 'none';
                        alert("서버와 통신하는 중 문제가 발생했습니다.");
                    }
                }

                function bookCourse(id, cName) {
                    const uName = document.getElementById(`name-${id}`).value;
                    const date = document.getElementById(`date-${id}`).value;
                    if(!date) { alert("예약 날짜를 선택해주세요!"); return; }

                    fetch('/book', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ course_name: cName, user_name: uName, date: date })
                    }).then(r => r.json()).then(data => { alert(data.message); });
                }

                function loadMyPage() {
                    document.getElementById('map-container').style.display = 'none'; 
                    fetch('/my-reservations').then(r => r.json()).then(data => {
                        const contentArea = document.getElementById('content-area');
                        contentArea.innerHTML = "<div class='col-12'><h3 class='fw-bold mb-4'><i class='bi bi-journal-check me-2'></i>나의 예약 내역</h3></div>";
                        if (data.result.length === 0) { 
                            contentArea.innerHTML += "<div class='col-12 text-center'><p class='text-muted'>예약 내역이 없습니다.</p></div>"; return; 
                        }
                        data.result.forEach(res => {
                            contentArea.innerHTML += `
                                <div class="col-md-6">
                                    <div class="card p-4 border-start border-4 border-warning">
                                        <h5 class="fw-bold mb-2 text-dark">${res.course_name}</h5>
                                        <p class="mb-1 text-secondary"><i class="bi bi-person me-2"></i>예약자: ${res.user_name}</p>
                                        <p class="mb-0 text-secondary"><i class="bi bi-calendar me-2"></i>예약일: <span class="fw-bold text-primary">${res.date}</span></p>
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
    # 관리자 코드는 이전과 동일하게 유지
    pass # (생략 방지)
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
