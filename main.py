import sqlite3
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from datetime import datetime, timedelta

app = FastAPI()

# 🌟 [개선된 엔진] 골프장 운영 시간에 맞춰 10분 간격으로 티타임을 자동으로 생성합니다.
def generate_tee_times():
    times = []
    start_time = datetime.strptime("06:00", "%H:%M")
    # 1부(06:00~09:00), 2부(12:00~15:00) 생성
    for i in range(0, 180, 10): # 1부: 10분 간격
        t = (start_time + timedelta(minutes=i)).strftime("%H:%M")
        times.append({"time": t, "status": "available"})
    
    start_time_2 = datetime.strptime("12:00", "%H:%M")
    for i in range(0, 180, 10): # 2부: 10분 간격
        t = (start_time_2 + timedelta(minutes=i)).strftime("%H:%M")
        times.append({"time": t, "status": "available"})
    return times

@app.get("/api/tee-times/{date}")
def get_tee_times(date: str):
    # 이제는 시간이 뒤죽박죽이지 않고 10분 간격으로 정교하게 나옵니다.
    return {"times": generate_tee_times()}

@app.get("/web", response_class=HTMLResponse)
def show_webpage():
    return """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            .tee-time-btn { margin: 5px; padding: 10px; border-radius: 8px; border: 1px solid #ddd; width: 80px; text-align: center; }
            .available { background-color: #e8f5e9; color: #2e7d32; cursor: pointer; }
            .hero-img { width: 100%; height: 300px; object-fit: cover; }
        </style>
    </head>
    <body class="bg-light">
        <div class="container mt-4">
            <div class="card p-4 shadow">
                <h4 class="fw-bold">남서울 컨트리클럽</h4>
                <hr>
                <label>날짜 선택</label>
                <input type="date" id="date-picker" class="form-control mb-3" onchange="loadTeeTimes()">
                
                <h6>선택 가능한 티타임</h6>
                <div id="tee-time-list" class="d-flex flex-wrap"></div>
            </div>
        </div>
        <script>
            function loadTeeTimes() {
                const date = document.getElementById('date-picker').value;
                if(!date) return;
                fetch('/api/tee-times/' + date)
                    .then(r => r.json())
                    .then(data => {
                        const list = document.getElementById('tee-time-list');
                        list.innerHTML = '';
                        data.times.forEach(t => {
                            const btn = document.createElement('div');
                            btn.className = 'tee-time-btn available';
                            btn.innerText = t.time;
                            list.appendChild(btn);
                        });
                    });
            }
        </script>
    </body>
    </html>
    """
