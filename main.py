import sqlite3
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

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
            .hero-img { width: 100%; height: 300px; object-fit: cover; border-radius: 0 0 20px 20px; }
        </style>
    </head>
    <body class="bg-light">
        <div class="container-fluid p-0">
            <!-- 1. 골프장 이미지 -->
            <img src="https://images.unsplash.com/photo-1593111736653-538640192e42?auto=format&fit=crop&w=800&q=80" class="hero-img" alt="골프장">
        </div>
        
        <div class="container mt-4 pb-5">
            <div class="card p-4 shadow">
                <!-- 2. 골프장 소개 -->
                <h2 class="fw-bold">남서울 컨트리클럽</h2>
                <p class="text-muted">대한민국 최고의 명문 골프장입니다.</p>
                <hr>
                
                <!-- 3. 코스 소개 -->
                <h5>코스 소개</h5>
                <p>전략적이고 아름다운 자연경관을 자랑하는 18홀 정규 코스입니다.</p>
                <hr>
                
                <!-- 4. 티업 날짜 및 시간 선택 -->
                <h5>티업 시간 선택</h5>
                <input type="date" class="form-control mb-3">
                <div id="tee-time-list" class="d-flex flex-wrap">
                    <div class="tee-time-btn available">07:30</div>
                    <div class="tee-time-btn booked">08:15 (마감)</div>
                    <div class="tee-time-btn available">12:40</div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
