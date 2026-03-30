from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from ai.manager import load_ai_model, predict_all

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """
    서버 시작 시 한 번만 모델을 로드하여 대기 시간을 줄입니다.
    """
    print("Starting server... Initializing AI Model...")
    load_ai_model()

@app.get("/")
async def root():
    return {"status": "ok", "message": "Server is running"}

@app.post("/api/detect")
async def detect_ai_media(file: UploadFile = File(...)):
    """
    클라이언트로부터 이미지 파일을 받아 진짜/가짜 여부를 예측합니다.
    """
    # 1. 파일 형식이 이미지인지 확인
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")
    
    # 2. 이미지 파일 읽기 (바이트 스트림)
    try:
        contents = await file.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")
    
    # 3. 모델을 이용한 추론 (5개 모델 + 메타 모델 앙상블)
    result = predict_all(contents)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
        
    # 4. 결과 반환 (React에서 사용하기 편한 형태로 제공)
    return {
        "status": "success",
        "filename": file.filename,
        "prediction": result
    }