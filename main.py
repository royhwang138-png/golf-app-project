import sqlite3
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

# 🌟 골프장 데이터와 티타임 상태를 관리하는 서버
@app.get("/api/course-detail/{course_id}")
def get_course_detail(course_id: int):
    # 실제로는 여기서 외부 골프장 API를 호출합니다.
    # 여기서는 시뮬레이션을 위해 상태값(예약가능/마감)을 반환합니다.
    return {
        "name": "남서울 컨트리클럽",
        "description": "품격 있는 코스와 완벽한 관리를 자랑하는 명문 골프장",
        "tee_times": [
            {"time": "07:30", "status": "available", "price": "220,000원"},
            {"time": "08:15", "status": "booked", "price": "220,000원"},
            {"time": "12:40", "status": "available", "price": "180,000원"},
            {"time": "13:30", "status": "booked", "price": "180,000원"}
        ]
    }

@app.get("/web", response_class=HTMLResponse)
def show_webpage():
    return """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            .tee-time-btn { margin: 5px; padding: 10px; border-radius: 10px; border: 1px solid #ccc; width: 100px; }
            .available { background-color: #d1e7dd; color: #0f5132; cursor: pointer; }
            .booked { background-color: #f8d7da; color: #842029; cursor: not-allowed; }
        </style>
    </head>
    <body class="bg-light">
        <div class="container mt-5">
            <div id="detail-view" class="card p-4 shadow">
                <h2 id="course-name" class="fw-bold">...</h2>
                <p id="course-desc" class="text-muted"></p>
                <hr>
                <h5>티타임 선택</h5>
                <div id="tee-time-list" class="d-flex flex-wrap"></div>
                <div id="price-info" class="mt-4 p-3 bg-white border rounded">가격을 확인하려면 시간을 선택하세요.</div>
            </div>
        </div>
        <script>
            fetch('/api/course-detail/1').then(r=>r.json()).then(data => {
                document.getElementById('course-name').innerText = data.name;
                document.getElementById('course-desc').innerText = data.description;
                const list = document.getElementById('tee-time-list');
                data.tee_times.forEach(t => {
                    const btn = document.createElement('div');
                    btn.className = `tee-time-btn ${t.status}`;
                    btn.innerText = t.time;
                    btn.onclick = () => { 
                        if(t.status === 'available') document.getElementById('price-info').innerHTML = `선택한 시간: <strong>${t.time}</strong> <br> 가격: <strong>${t.price}</strong>`;
                        else alert('이미 예약된 시간입니다!');
                    };
                    list.appendChild(btn);
                });
            });
        </script>
    </body>
    </html>
    """
