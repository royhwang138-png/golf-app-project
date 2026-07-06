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

# 🌟 전국 단위 골프장 데이터베이스 (가상의 중앙 API 서버 역할)
national_golf_courses = [
    {"id": 1, "name": "서울 레이크사이드", "location": "서울", "lat": 37.5665, "lng": 126.9780},
    {"id": 2, "name": "경기 드림베이", "location": "경기", "lat": 37.2752, "lng": 127.0095},
    {"id": 3, "name": "강원 파인힐스", "location": "강원", "lat": 37.8813, "lng": 127.7298},
    {"id": 4, "name": "제주 오션뷰CC", "location": "제주", "lat": 33.4996, "lng": 126.5312},
    {"id": 5, "name": "부산 해운대비치", "location": "부산", "lat": 35.1796, "lng": 129.0756},
    {"id": 6, "name": "충청 백제CC", "location": "충청", "lat": 36.3284, "lng": 127.4268},
    {"id": 7, "name": "전라 그린파크", "location": "전라", "lat": 35.8242, "lng": 127.1480},
    {"id": 8, "name": "경상 블루원", "location": "경상", "lat": 35.8342, "lng": 129.2189}
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
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">
            <style>
                body { background-color: #f4f7f6; font-family: 'Malgun Gothic', sans-serif; }
                .hero-section { background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%); color: white; padding: 50px 0; border-radius: 0 0 30px 30px; margin-bottom: 40px; }
                .card { border: none; border-radius: 20px; box-shadow: 0 8px 15px rgba(0,0,0,0.05); transition: all 0.3s ease; }
                .card:hover { transform: translateY(-5px); box-shadow: 0 12px 20px rgba(0,0,0,0.1); }
                .btn-primary { background-color: #2c5364; border: none; border-radius: 10px; }
                .btn-primary:hover { background-color: #0f2027; }
                .map-wrapper { border-radius: 20px; overflow: hidden; display: none; margin-bottom: 30px; border: 2px solid #fff; }
                .weather-badge { display: inline-flex; align-items: center; background-color: #e0f7fa; color: #006064; padding: 6px 12px; border-radius: 20px; font-weight: 600; margin-bottom: 15px; font-size: 0.85em; }
                .login-container { max-width: 420px; margin: 120px auto; background: white; padding: 50px; border-radius: 20px; box-shadow: 0 15px 35px rgba(0,0,0,0.1); text-align: center; }
                .loader-container { display: none; text-align: center; padding: 40px 0; }
                /* 지역 필터 버튼 스타일 */
                .region-btn { margin: 5px; border-radius: 20px; font-weight: bold; }
            </style>
        </head>
        <body>
            <div id="login-section" class="login-container">
                <i class="bi bi-shield-lock-fill text-primary" style="font-size: 3rem;"></i>
                <h2 class="fw-bold mb-4 mt-3" style="color: #0f2027;">VIP 회원 인증</h2>
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
                        <a class="navbar-brand text-primary fw-bold fs-4" href="#" style="color: #0f2027 !important;"><i class="bi bi-flag-fill me-2"></i>전국 프리미엄 라운딩</a>
                        <div class="d-flex align-items-center">
                            <span id="welcome-msg" class="me-3 fw-bold text-success d-none d-sm-block"></span>
                            <button class="btn btn-outline-warning fw-bold me-2 px-3" onclick="loadMyPage()"><i class="bi bi-calendar-check me-1"></i>내 예약</button>
                            <button class="btn btn-sm btn-secondary px-3" onclick="processLogout()">로그아웃</button>
                        </div>
                    </div>
                </nav>

                <div class="hero-section text-center">
                    <div class="container">
                        <h1 class="display-5 fw-bold mb-3">전국 8도, 어디로 떠나시겠습니까?</h1>
                        <p class="lead mb-4 opacity-75">중앙 API 서버와 연동하여 전국 골프장 현황을 실시간으로 제공합니다.</p>
                        
                        <!-- 🌟 API 연동 고도화: 전국 지역별 빠른 검색 버튼 -->
                        <div class="mb-4">
                            <button class="btn btn-light region-btn" onclick="searchRegion('전국')">전국 전체보기</button>
                            <button class="btn btn-outline-light region-btn" onclick="searchRegion('서울')">서울/경기</button>
                            <button class="btn btn-outline-light region-btn" onclick="searchRegion('제주')">제주</button>
                            <button class="btn btn-outline-light region-btn" onclick="searchRegion('부산')">부산/경상</button>
                        </div>

                        <div class="row justify-content-center">
                            <div class="col-md-7 col-sm-10">
                                <div class="input-group input-group-lg shadow">
                                    <span class="input-group-text bg-white border-0"><i class="bi bi-search text-muted"></i></span>
                                    <input type="text" id="location-input" class="form-control border-0" placeholder="직접 지역 입력 (예: 강원)">
                                    <button class="btn btn-primary px-4 fw-bold" onclick="searchRegion('custom')">검색하기</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="container pb-5">
                    <div id="loading-spinner" class="loader-container">
                        <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;" role="status"></div>
                        <h5 class="mt-3 fw-bold text-secondary">전국 API 망에서 데이터를 수집 중입니다...</h5>
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
                        searchRegion('전국'); // 로그인 즉시 전국 데이터 불러오기
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

                // 🌟 외부 API 호출을 담당하는 핵심 함수
                async function searchRegion(region) {
                    let searchKeyword = region;
                    if (region === 'custom') {
                        searchKeyword = document.getElementById('location-input').value;
                    }
                    if (region === '서울') searchKeyword = '서울|경기';
                    if (region === '부산') searchKeyword = '부산|경상';

                    const contentArea = document.getElementById('content-area');
                    const mapContainer = document.getElementById('map-container');
                    const spinner = document.getElementById('loading-spinner');
                    
                    contentArea.innerHTML = ""; 
                    mapContainer.style.display = 'none';
                    spinner.style.display = 'block';

                    try {
                        // 중앙 API 서버에 데이터 요청 (Fetch)
                        let url = '/api/golf-courses';
                        if (searchKeyword !== '전국' && searchKeyword !== '') {
                            url = `/api/golf-courses?region=${searchKeyword}`;
                        }

                        const response = await fetch(url);
                        const data = await response.json();
                        
                        spinner.style.display = 'none';

                        if (data.result.length === 0) {
                            contentArea.innerHTML = "<div class='col-12 text-center mt-5'><i class='bi bi-emoji-frown fs-1 text-muted'></i><h4 class='text-muted mt-3 fw-bold'>해당 지역의 API 데이터가 없습니다.</h4></div>";
                            return;
                        }

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
                                weatherHtml = `<div class='weather-badge'><i class='bi bi-thermometer-half me-1'></i>${temp}°C</div>`;
                            } catch (error) {
                                weatherHtml = `<div class='weather-badge bg-light text-danger'><i class='bi bi-exclamation-triangle me-1'></i>오류</div>`;
                            }

                            contentArea.innerHTML += `
                                <div class="col-lg-3 col-md-4 col-sm-6">
                                    <div class="card h-100 p-3">
                                        <h5 class="card-title fw-bold mb-1" style="color: #0f2027;">${c.name}</h5>
                                        <h6 class="card-subtitle mb-2 text-secondary" style="font-size: 0.9em;"><i class="bi bi-geo-alt-fill me-1 text-danger"></i>${c.location}</h6>
                                        ${weatherHtml}
                                        <div class="mt-auto">
                                            <input type="text" id="name-${c.id}" class="form-control form-control-sm mb-2 bg-light" value="${currentUser}" readonly>
                                            <input type="date" id="date-${c.id}" class="form-control form-control-sm mb-2">
                                            <button class="btn btn-success btn-sm w-100 fw-bold shadow-sm" onclick="bookCourse(${c.id}, '${c.name}')">예약</button>
                                        </div>
                                    </div>
                                </div>
                            `;
                        }
                    } catch (error) {
                        spinner.style.display = 'none';
                        alert("API 서버 통신 장애가 발생했습니다.");
                    }
                }

                function bookCourse(id, cName) {
                    const uName = document.getElementById(`name-${id}`).value;
                    const date = document.getElementById(`date-${id}`).value;
                    if(!date) { alert("날짜를 선택해주세요!"); return; }

                    fetch('/book', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ course_name: cName, user_name: uName, date: date })
                    }).then(r => r.json()).then(data => { alert(data.message); });
                }

                function loadMyPage() {
                    document.getElementById('map-container').style.display = 'none'; 
                    fetch('/my-reservations').then(r => r.json()).then(data => {
                        const contentArea = document.getElementById('content-area');
                        contentArea.innerHTML = "<div class='col-12'><h3 class='fw-bold mb-4'>나의 예약 내역</h3></div>";
                        if (data.result.length === 0) { return; }
                        data.result.forEach(res => {
                            contentArea.innerHTML += `<div class="col-md-6"><div class="card p-4 border-start border-4 border-warning"><h5 class="fw-bold">${res.course_name}</h5><p>${res.date}</p></div></div>`;
                        });
                    });
                }
            </script>
        </body>
    </html>
    """

# 🌟 전국 단위 데이터를 제공하는 새로운 API 엔드포인트
@app.get("/api/golf-courses")
def get_golf_courses_api(region: str = None):
    if region:
        # '서울|경기' 처럼 여러 지역을 동시에 검색할 수 있도록 처리
        regions = region.split('|')
        result = [c for c in national_golf_courses if any(r in c["location"] for r in regions)]
        return {"result": result}
    return {"result": national_golf_courses}

@app.post("/book")
def make_reservation(form: ReservationForm):
    conn = sqlite3.connect('golf_app.db')
    c = conn.cursor()
    c.execute("INSERT INTO reservations (course_name, user_name, date) VALUES (?, ?, ?)", (form.course_name, form.user_name, form.date))
    conn.commit()
    conn.close()
    return {"message": f"성공! 예약이 확정되었습니다!"}

@app.get("/my-reservations")
def get_my_reservations():
    conn = sqlite3.connect('golf_app.db')
    conn.row_factory = sqlite3.Row 
    c = conn.cursor()
    c.execute("SELECT * FROM reservations ORDER BY id DESC")
    result = [{"course_name": r["course_name"], "user_name": r["user_name"], "date": r["date"]} for r in c.fetchall()]
    conn.close()
    return {"result": result}
