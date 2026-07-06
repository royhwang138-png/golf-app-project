import sqlite3
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

# 🌟 날짜별로 다른 티업 시간을 보여주는 '스마트 장부' 시스템
@app.get("/api/tee-times/{date}")
def get_tee_times(date: str):
    # 실제 운영 시에는 여기서 골프장 DB를 조회합니다.
    # 여기선 테스트를 위해 날짜에 따라 시간을 다르게 보여주는 로직을 넣었습니다.
    if "07" in date: # 7일에는 시간이 꽉 찼다고 가정
        return {"times": [{"time": "07:30", "status": "booked"}, {"time": "12:40", "status": "booked"}]}
    else:
        return {"times": [{"time": "07:30", "status": "available"}, {"time": "12:40", "status": "available"}]}

@app.get("/web", response_class=HTMLResponse)
def show_webpage():
    return """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            .tee-time-btn { margin: 5px; padding: 10px; border-radius: 10px; border: 1px solid #ccc; width: 100px; text-align: center; }
            .available { background-color: #d1e7dd; color: #0f5132; cursor: pointer; }
            .booked { background-color: #f8d7da; color: #842029; cursor: not-allowed; }
            .hero-img { width: 100%; height: 300px; object-fit: cover; }
        </style>
    </head>
    <body class="bg-light">
        <img src="https://images.unsplash.com/photo-1593111736653-538640192e42?auto=format&fit=crop&w=800&q=80" class="hero-img">
        <div class="container mt-4 pb-5">
            <div class="card p-4 shadow">
                <h2 class="fw-bold">남서울 컨트리클럽</h2>
                <hr>
                <!-- 날짜 선택 달력 -->
                <h5>날짜 선택</h5>
                <input type="date" id="date-picker" class="form-control mb-3" onchange="loadTeeTimes()">
                
                <!-- 날짜 찍으면 바뀔 시간표 -->
                <h5>티업 시간 선택</h5>
                <div id="tee-time-list" class="d-flex flex-wrap">
                    <p class="text-muted">날짜를 먼저 선택해 주세요.</p>
                </div>
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
                            btn.className = `tee-time-btn ${t.status}`;
                            btn.innerText = t.time + (t.status === 'booked' ? ' (마감)' : '');
                            list.appendChild(btn);
                        });
                    });
            }
        </script>
    </body>
    </html>
    """
