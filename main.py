import sqlite3
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

# 🌟 메인 화면을 그리는 코드입니다.
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
                .hero-section { padding: 40px 0; background: #ffffff; text-align: center; }
                /* 지역 버튼 디자인 */
                .region-btn { width: 100px; height: 100px; border-radius: 20px; font-weight: bold; border: none; background: #eef2f5; transition: 0.3s; }
                .region-btn:hover { background: #0b1a40; color: white; }
                /* 인기 골프장 카드 */
                .card { border-radius: 20px; border: none; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
            </style>
        </head>
        <body>
            <div class="container mt-5">
                <div class="hero-section">
                    <h2 class="fw-bold mb-4">어디로 떠나시나요?</h2>
                    <!-- 🌟 중앙에 배치된 지역별 골프장 버튼들 -->
                    <div class="d-flex justify-content-center gap-3 flex-wrap">
                        <button class="region-btn" onclick="alert('서울/경기 지역 골프장을 보여줄게요!')">서울/경기</button>
                        <button class="region-btn" onclick="alert('강원 지역 골프장을 보여줄게요!')">강원</button>
                        <button class="region-btn" onclick="alert('충청/전라 지역 골프장을 보여줄게요!')">충청/전라</button>
                        <button class="region-btn" onclick="alert('제주 지역 골프장을 보여줄게요!')">제주</button>
                    </div>
                </div>
                
                <h4 class="fw-bold mt-5 mb-3">오늘의 인기 골프장</h4>
                <div class="row g-3">
                    <div class="col-md-4"><div class="card p-3">남서울CC</div></div>
                    <div class="col-md-4"><div class="card p-3">우정힐스CC</div></div>
                    <div class="col-md-4"><div class="card p-3">클럽나인브릿지</div></div>
                </div>
            </div>
        </body>
    </html>
    """
