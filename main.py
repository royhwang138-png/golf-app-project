import sqlite3
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()

def init_db():
    conn = sqlite3.connect('golf_app.db')
    c = conn.cursor()
    # 🌟 기존 장부를 파기하고 '시간(time)' 칸이 추가된 새 장부(Table)를 만듭니다.
    c.execute('DROP TABLE IF EXISTS reservations')
    c.execute('''CREATE TABLE reservations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, course_name TEXT, user_name TEXT, date TEXT, time TEXT)''')
    conn.commit()
    conn.close()

init_db()

premium_golf_courses = [
    {"id": 1, "name": "남서울 컨트리클럽", "location": "경기 성남", "lat": 37.3975, "lng": 127.1009},
    {"id": 2, "name": "88 컨트리클럽", "location": "경기 용인", "lat": 37.3013, "lng": 127.1558},
    {"id": 3, "name": "안양 컨트리클럽", "location": "경기 군포", "lat": 37.3486, "lng": 126.9366},
    {"id": 4, "name": "세이지우드 홍천", "location": "강원 홍천", "lat": 37.8286, "lng": 128.0255},
    {"id": 5, "name": "우정힐스 컨트리클럽", "location": "충남 천안", "lat": 36.7592, "lng": 127.2144},
    {"id": 6, "name": "클럽나인브릿지", "location": "제주 서귀포", "lat": 33.3639, "lng": 126.3686}
]

class ReservationForm(BaseModel):
    course_name: str
    user_name: str
    date: str
    time: str  # 🌟 티타임 정보가 추가되었습니다.

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
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">
            <style>
                body { background-color: #f4f7f6; font-family: 'Malgun Gothic', sans-serif; }
                .hero-section { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 50px 0; border-radius: 0 0 30px 30px; margin-bottom: 40px; box-shadow: 0 10px 20px rgba(0,0,0,0.1); }
                .card { border: none; border-radius: 20px; box-shadow: 0 8px 15px rgba(0,0,0,0.05); transition: all 0.3s ease; border-top: 4px solid #1e3c72;}
                .card:hover { transform: translateY(-5px); box-shadow: 0 12px 20px rgba(0,0,0,0.15); }
                .btn-primary { background-color: #1e3c72; border: none; border-radius: 10px; }
                .map-wrapper { border-radius: 20px; overflow: hidden; display: none; margin-bottom: 30px; border: 2px solid #fff; box-shadow: 0 8px 15px rgba(0,0,0,0.05); }
                .weather-badge { display: inline-flex; align-items: center; background-color: #e3f2fd; color: #1565c0; padding: 6px 12px; border-radius: 20px; font-weight: 600; margin-bottom: 15px; font-size: 0.85em; }
                .login-container { max-width: 420px; margin: 120px auto; background: white; padding: 50px; border-radius: 20px; box-shadow: 0 15px 35px rgba(0,0,0,0.1); text-align: center; }
                .loader-container { display: none; text-align: center; padding: 40px 0; }
                .region-btn { margin: 5px; border-radius: 20px; font-weight: bold; }
                .premium-badge { position: absolute; top: -10px; right: -10px; background: #ff9800; color: white; padding: 5px 15px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            </style>
        </head>
        <body>
            <div id="login-section" class="login-container">
                <i class="bi bi-shield-check text-primary" style="font-size: 3.5rem;"></i>
                <h2 class="fw-bold mb-4 mt-3" style="color: #1e3c72;">VIP 프리미엄 인증</h2>
                <div class="form-floating mb-3">
                    <input type="text" id="login-id" class="form-control" placeholder="아이디" value="vip">
                    <label for="login-id">아이디</label>
                </div>
                <div class="form-floating mb-4">
                    <input type="password" id="login-pw" class="form-control" placeholder="비밀번호" value="1234">
                    <label for="login-pw">비밀번호</label>
                </div>
                <button class="btn btn-primary w-100 py-3 fw-bold fs-5" onclick="processLogin()">안전하게 접속하기</button>
            </div>

            <div id="main-app-section" style="display: none;">
                <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm py-3">
                    <div class="container d-flex justify-content-between align-items-center">
                        <a class="navbar-brand text-primary fw-bold fs-4" href="#" style="color: #1e3c72 !important;"><i class="bi bi-award-fill me-2 text-warning"></i>프리미엄 라운딩</a>
                        <div class="d-flex align-items-center">
                            <span id="welcome-msg" class="me-3 fw-bold text-success d-none d-sm-block"></span>
                            <button class="btn btn-outline-warning fw-bold me-2 px-3" onclick="loadMyPage()"><i class="bi bi-calendar-check me-1"></i>내 예약</button>
                            <button class="btn btn-sm btn-secondary px-3" onclick="processLogout()">로그아웃</button>
                        </div>
                    </div>
                </nav>

                <div class="hero-section text-center">
                    <div class="container">
                        <h1 class="display-5 fw-bold mb-3">검증된 명문 골프장만 안내합니다</h1>
                        <div class="mb-4">
                            <button class="btn btn-light region-btn" onclick="fetchPremiumApi('전국')">전국 전체</button>
                            <button class="btn btn-outline-light region-btn" onclick="fetchPremiumApi('경기')">서울/경기</button>
                            <button class="btn btn-outline-light region-btn" onclick="fetchPremiumApi('강원')">강원</button>
                            <button class="btn btn-outline-light region-btn" onclick="fetchPremiumApi('제주')">제주</button>
                        </div>
                    </div>
                </div>

                <div class="container pb-5">
                    <div id="loading-spinner" class="loader-container">
                        <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;" role="status"></div>
                        <h5 class="mt-3 fw-bold text-secondary">프리미엄 데이터를 불러오는 중입니다...</h5>
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
                        fetchPremiumApi('전국'); 
                    } else {
                        alert("❌ 인증 실패");
                    }
                }

                function processLogout() {
                    currentUser = "";
                    document.getElementById('main-app-section').style.display = 'none';
                    document.getElementById('login-section').style.display = 'block';
                    document.getElementById('content-area').innerHTML = "";
                    document.getElementById('map-container').style.display = 'none';
                }

                async function fetchPremiumApi(region) {
                    const contentArea = document.getElementById('content-area');
                    const mapContainer = document.getElementById('map-container');
                    const spinner = document.getElementById('loading-spinner');
                    
                    contentArea.innerHTML = ""; 
                    mapContainer.style.display = 'none';
                    spinner.style.display = 'block';

                    try {
                        let url = '/api/premium-golf-courses';
                        if (region !== '전국') { url = `/api/premium-golf-courses?region=${region}`; }

                        const response = await fetch(url);
                        const data = await response.json();
                        spinner.style.display = 'none';

                        if (data.result.length === 0) return;

                        const first = data.result[0];
                        const bbox = `${first.lng - 0.05},${first.lat - 0.05},${first.lng + 0.05},${first.lat + 0.05}`;
                        document.getElementById('map-frame').src = `https://www.openstreetmap.org/export/embed.html?bbox=${bbox}&layer=mapnik&marker=${first.lat},${first.lng}`;
                        mapContainer.style.display = 'block';

                        for (const c of data.result) {
                            let weatherHtml = "<div class='weather-badge'><i class='bi bi-cloud-arrow-down me-2'></i>날씨 수집 중...</div>";
                            try {
                                const weatherRes = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${c.lat}&longitude=${c.lng}&current_weather=true`);
                                const weatherData = await weatherRes.json();
                                const temp = weatherData.current_weather.temperature;
                                weatherHtml = `<div class='weather-badge'><i class='bi bi-thermometer-half me-1'></i>현지 기온: ${temp}°C</div>`;
                            } catch (error) {}

                            // 🌟 핵심 추가: 티타임 선택 드롭다운(시간표) 메뉴
                            contentArea.innerHTML += `
                                <div class="col-lg-4 col-md-6 position-relative">
                                    <div class="card h-100 p-4">
                                        <div class="premium-badge">정규 18홀</div>
                                        <h4 class="card-title fw-bold mb-1 mt-2" style="color: #1e3c72;">${c.name}</h4>
                                        <h6 class="card-subtitle mb-3 text-secondary"><i class="bi bi-geo-alt-fill me-1 text-danger"></i>${c.location}</h6>
                                        ${weatherHtml}
                                        <div class="mt-auto pt-3 border-top">
                                            <input type="text" id="name-${c.id}" class="form-control mb-2 bg-light" value="${currentUser}" readonly>
                                            
                                            <!-- 날짜 선택 -->
                                            <div class="input-group mb-2">
                                                <span class="input-group-text bg-white"><i class="bi bi-calendar"></i></span>
                                                <input type="date" id="date-${c.id}" class="form-control">
                                            </div>
                                            
                                            <!-- 🌟 티타임 선택 메뉴 -->
                                            <div class="input-group mb-3">
                                                <span class="input-group-text bg-white"><i class="bi bi-clock"></i></span>
                                                <select id="time-${c.id}" class="form-select">
                                                    <option value="">티타임 선택</option>
                                                    <option value="07:30 (1부)">07:30 (1부)</option>
                                                    <option value="08:15 (1부)">08:15 (1부)</option>
                                                    <option value="12:40 (2부)">12:40 (2부)</option>
                                                    <option value="13:30 (2부)">13:30 (2부)</option>
                                                    <option value="17:00 (3부 야간)">17:00 (3부 야간)</option>
                                                </select>
                                            </div>

                                            <button class="btn btn-primary w-100 fw-bold shadow-sm py-2" onclick="bookCourse(${c.id}, '${c.name}')"><i class="bi bi-check2-circle me-1"></i>티타임 예약 확정</button>
                                        </div>
                                    </div>
                                </div>
                            `;
                        }
                    } catch (error) {
                        spinner.style.display = 'none';
                        alert("API 서버 통신에 실패했습니다.");
                    }
                }

                function bookCourse(id, cName) {
                    const uName = document.getElementById(`name-${id}`).value;
                    const date = document.getElementById(`date-${id}`).value;
                    const time = document.getElementById(`time-${id}`).value; // 🌟 시간 정보 가져오기
                    
                    if(!date) { alert("라운딩 날짜를 선택해주세요!"); return; }
                    if(!time) { alert("원하시는 티타임(시간)을 선택해주세요!"); return; }

                    // 🌟 서버로 이름, 날짜, 시간에 더해 티타임까지 4가지 정보를 포장해서 보냄
                    fetch('/book', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ course_name: cName, user_name: uName, date: date, time: time })
                    }).then(r => r.json()).then(data => { alert(data.message); });
                }

                function loadMyPage() {
                    document.getElementById('map-container').style.display = 'none'; 
                    fetch('/my-reservations').then(r => r.json()).then(data => {
                        const contentArea = document.getElementById('content-area');
                        contentArea.innerHTML = "<div class='col-12'><h3 class='fw-bold mb-4'><i class='bi bi-journal-text me-2'></i>나의 티타임 예약 내역</h3></div>";
                        if (data.result.length === 0) { return; }
                        data.result.forEach(res => {
                            contentArea.innerHTML += `
                            <div class="col-md-6">
                                <div class="card p-4 border-start border-4 border-primary shadow-sm">
                                    <h5 class="fw-bold mb-3">${res.course_name}</h5>
                                    <p class="mb-1 text-muted"><i class="bi bi-calendar-event me-2"></i>날짜: <strong>${res.date}</strong></p>
                                    <p class="mb-0 text-muted"><i class="bi bi-clock me-2"></i>시간: <strong class="text-primary">${res.time}</strong></p>
                                </div>
                            </div>`;
                        });
                    });
                }
            </script>
        </body>
    </html>
    """

@app.get("/api/premium-golf-courses")
def get_premium_golf_courses_api(region: str = None):
    if region:
        result = [c for c in premium_golf_courses if region in c["location"]]
        return {"result": result}
    return {"result": premium_golf_courses}

@app.post("/book")
def make_reservation(form: ReservationForm):
    conn = sqlite3.connect('golf_app.db')
    c = conn.cursor()
    # 🌟 DB 장부에 시간(time)을 추가로 기록
    c.execute("INSERT INTO reservations (course_name, user_name, date, time) VALUES (?, ?, ?, ?)", (form.course_name, form.user_name, form.date, form.time))
    conn.commit()
    conn.close()
    return {"message": f"🎉 예약 완료! {form.user_name}님, {form.date} {form.time}에 뵙겠습니다!"}

@app.get("/my-reservations")
def get_my_reservations():
    conn = sqlite3.connect('golf_app.db')
    conn.row_factory = sqlite3.Row 
    c = conn.cursor()
    c.execute("SELECT * FROM reservations ORDER BY id DESC")
    # 🌟 내 예약 목록을 가져올 때 시간(time)도 같이 가져옴
    result = [{"course_name": r["course_name"], "user_name": r["user_name"], "date": r["date"], "time": r["time"]} for r in c.fetchall()]
    conn.close()
    return {"result": result}

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
            <h2 class="fw-bold mb-4">⚙️ VVIP 통합 관리자 대시보드 (티타임 포함)</h2>
            <div class="table-responsive bg-white p-3 rounded shadow-sm">
                <table class="table table-hover align-middle">
                    <thead class="table-dark">
                        <tr><th>ID</th><th>골프장명</th><th>예약자 성함</th><th>날짜</th><th>티타임</th></tr>
                    </thead>
                    <tbody>
    """
    for r in rows:
        html_content += f"""
                        <tr>
                            <td>{r['id']}</td><td class="fw-bold">{r['course_name']}</td><td>{r['user_name']}</td><td>{r['date']}</td><td class="text-primary fw-bold">{r['time']}</td>
                        </tr>
        """
    html_content += """
                    </tbody>
                </table>
            </div>
        </body>
    </html>
    """
    return html_content
