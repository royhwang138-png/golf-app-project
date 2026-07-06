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
                .region-btn { margin: 5px; border-radius: 20px; font-weight: bold; }
                
                /* 긴 글씨 잘리게 하는 디자인 */
                .text-ellipsis { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
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
                        <a class="navbar-brand text-primary fw-bold fs-4" href="#" style="color: #0f2027 !important;"><i class="bi bi-flag-fill me-2"></i>리얼 데이터 라운딩</a>
                        <div class="d-flex align-items-center">
                            <span id="welcome-msg" class="me-3 fw-bold text-success d-none d-sm-block"></span>
                            <button class="btn btn-outline-warning fw-bold me-2 px-3" onclick="loadMyPage()"><i class="bi bi-calendar-check me-1"></i>내 예약</button>
                            <button class="btn btn-sm btn-secondary px-3" onclick="processLogout()">로그아웃</button>
                        </div>
                    </div>
                </nav>

                <div class="hero-section text-center">
                    <div class="container">
                        <h1 class="display-5 fw-bold mb-3">실제 운영 중인 골프장을 찾습니다</h1>
                        <p class="lead mb-4 opacity-75"><span class="badge bg-warning text-dark me-2">LIVE</span>글로벌 지도 API망과 연결되어 실제 좌표와 날씨를 수집합니다.</p>
                        
                        <div class="mb-4">
                            <button class="btn btn-light region-btn" onclick="searchRealApi('서울')">서울/경기</button>
                            <button class="btn btn-outline-light region-btn" onclick="searchRealApi('강원')">강원도</button>
                            <button class="btn btn-outline-light region-btn" onclick="searchRealApi('제주')">제주도</button>
                        </div>

                        <div class="row justify-content-center">
                            <div class="col-md-7 col-sm-10">
                                <div class="input-group input-group-lg shadow">
                                    <span class="input-group-text bg-white border-0"><i class="bi bi-search text-muted"></i></span>
                                    <input type="text" id="location-input" class="form-control border-0" placeholder="동네 이름 입력 (예: 송파구)">
                                    <button class="btn btn-primary px-4 fw-bold" onclick="searchRealApi('custom')">실시간 검색</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="container pb-5">
                    <div id="loading-spinner" class="loader-container">
                        <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;" role="status"></div>
                        <h5 class="mt-3 fw-bold text-secondary">글로벌 지도 서버에서 <span id="search-keyword-display" class="text-primary"></span> 지역의 찐 골프장을 찾고 있습니다...</h5>
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
                        searchRealApi('서울'); // 로그인 즉시 서울 데이터 불러오기
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

                // 🌟 [핵심] 가짜 데이터가 아닌, 진짜 외부망(OpenStreetMap)으로 접속하는 통신 모듈
                async function searchRealApi(region) {
                    let searchKeyword = region;
                    if (region === 'custom') {
                        searchKeyword = document.getElementById('location-input').value;
                    }
                    if (!searchKeyword) { alert("검색할 지역을 입력해주세요!"); return; }

                    document.getElementById('search-keyword-display').innerText = searchKeyword;
                    
                    const contentArea = document.getElementById('content-area');
                    const mapContainer = document.getElementById('map-container');
                    const spinner = document.getElementById('loading-spinner');
                    
                    contentArea.innerHTML = ""; 
                    mapContainer.style.display = 'none';
                    spinner.style.display = 'block';

                    try {
                        // 1. 글로벌 지도 서버에 "해당 지역 + 골프장" 키워드로 직접 요청 발송 (최대 8개)
                        const realApiUrl = `https://nominatim.openstreetmap.org/search?format=json&q=골프장+${searchKeyword}&limit=8`;
                        const response = await fetch(realApiUrl);
                        const data = await response.json();
                        
                        spinner.style.display = 'none';

                        if (data.length === 0) {
                            contentArea.innerHTML = "<div class='col-12 text-center mt-5'><i class='bi bi-emoji-frown fs-1 text-muted'></i><h4 class='text-muted mt-3 fw-bold'>해당 지역의 실제 골프장 데이터를 찾지 못했습니다.</h4></div>";
                            return;
                        }

                        // 2. 검색된 첫 번째 진짜 골프장의 위도/경도를 바탕으로 지도 렌더링
                        const first = data[0];
                        const bbox = `${parseFloat(first.lon) - 0.05},${parseFloat(first.lat) - 0.05},${parseFloat(first.lon) + 0.05},${parseFloat(first.lat) + 0.05}`;
                        document.getElementById('map-frame').src = `https://www.openstreetmap.org/export/embed.html?bbox=${bbox}&layer=mapnik&marker=${first.lat},${first.lon}`;
                        mapContainer.style.display = 'block';

                        // 3. 응답받은 실제 데이터를 화면에 그리기
                        for (let i = 0; i < data.length; i++) {
                            const c = data[i];
                            
                            // 실제 데이터는 이름이 복잡하므로 예쁘게 다듬기
                            let realName = c.name;
                            if (!realName) { realName = c.display_name.split(',')[0]; }
                            let realAddress = c.display_name.split(',').slice(0, 3).join(', ');

                            // 각 진짜 골프장의 좌표로 기상청 API에 날씨 물어보기
                            let weatherHtml = "<div class='weather-badge'><i class='bi bi-cloud-arrow-down me-2'></i>날씨 수집 중...</div>";
                            try {
                                const weatherRes = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${c.lat}&longitude=${c.lon}&current_weather=true`);
                                const weatherData = await weatherRes.json();
                                const temp = weatherData.current_weather.temperature;
                                weatherHtml = `<div class='weather-badge'><i class='bi bi-thermometer-half me-1'></i>현지 기온: ${temp}°C</div>`;
                            } catch (error) {
                                weatherHtml = `<div class='weather-badge bg-light text-danger'><i class='bi bi-exclamation-triangle me-1'></i>날씨 수집 실패</div>`;
                            }

                            contentArea.innerHTML += `
                                <div class="col-lg-3 col-md-4 col-sm-6">
                                    <div class="card h-100 p-3">
                                        <h5 class="card-title fw-bold mb-1 text-ellipsis" style="color: #0f2027;" title="${realName}">${realName}</h5>
                                        <h6 class="card-subtitle mb-2 text-secondary text-ellipsis" style="font-size: 0.85em;" title="${realAddress}"><i class="bi bi-geo-alt-fill me-1 text-danger"></i>${realAddress}</h6>
                                        ${weatherHtml}
                                        <div class="mt-auto">
                                            <input type="text" id="name-${i}" class="form-control form-control-sm mb-2 bg-light" value="${currentUser}" readonly>
                                            <input type="date" id="date-${i}" class="form-control form-control-sm mb-2">
                                            <button class="btn btn-success btn-sm w-100 fw-bold shadow-sm" onclick="bookCourse(${i}, '${realName.replace(/'/g, "\\'")}')">예약</button>
                                        </div>
                                    </div>
                                </div>
                            `;
                        }
                    } catch (error) {
                        spinner.style.display = 'none';
                        alert("글로벌 서버망 통신 장애가 발생했습니다.");
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
