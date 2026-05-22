import json, pathlib
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from openai import AsyncOpenAI
from app.config import settings

app = FastAPI()
client = AsyncOpenAI(api_key=settings.openai_api_key)
BASE = pathlib.Path(__file__).parent

class AnalyzeRequest(BaseModel):
    cover_letter: str
    position: str

@app.get("/")
async def root():
    return FileResponse(BASE / "static/index.html")

@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    resp = await client.chat.completions.create(
        model=settings.model_name,
        messages=[
            {
                "role": "system",
                "content": "당신은 10년 경력의 채용 전문가입니다. 자소서를 분석하고 반드시 JSON 형식으로만 응답합니다."
            },
            {
                "role": "user",
                "content": f"""지원 직무: {req.position}

자소서:
{req.cover_letter}

다음 JSON 형식으로만 응답해주세요:
{{
    "score": 85,
    "grade": "B+",
    "strengths": ["구체적인 강점1", "구체적인 강점2", "구체적인 강점3"],
    "weaknesses": ["개선이 필요한 약점1", "개선이 필요한 약점2"],
    "suggestions": ["구체적인 개선안1", "구체적인 개선안2", "구체적인 개선안3"],
    "one_line": "한줄 총평 (20자 이내)"
}}"""
            }
        ],
        response_format={"type": "json_object"}
    )
    return JSONResponse(json.loads(resp.choices[0].message.content))
