from __future__ import annotations
import time
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from ..config import PROJECT_ROOT, DEVICE
from ..symbolic.engine import solve_step_by_step, verify_step_equivalence
from ..vision.syntax_guard import is_valid_latex_syntax, normalize_latex
from .schemas import SolveRequest, SolveResponse, VerifyStepRequest, VerifyStepResponse, OCRResponse, StepSchema

app = FastAPI(
    title="Al-Khwarizmi Math AI API",
    description="Neuro-Symbolic Arabic Mathematical Reasoner & Pedagogical Explainer",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from ..reasoning.pipeline import HybridReasoningPipeline

pipeline = HybridReasoningPipeline()
_STATIC_DIR = Path(__file__).resolve().parent / "static"


@app.get("/", response_class=HTMLResponse)
@app.get("/testbed", response_class=HTMLResponse)
def get_testbed():
    index_file = _STATIC_DIR / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Al-Khwarizmi Math AI API</h1><p>Visit /docs for API documentation.</p>")


@app.get("/api/v1/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Khwarizmi Math AI",
        "device": str(DEVICE),
        "engine": "Hybrid (Cloud Qwen2.5-Math / Local Edge / SymPy 1.14 + C++ Syntax Guard)"
    }


@app.post("/api/v1/solve", response_model=SolveResponse)
def solve_equation_endpoint(req: SolveRequest):
    raw_latex = req.raw_equation
    if not raw_latex:
        raise HTTPException(status_code=400, detail="المعادلة الرياضية لا يمكن أن تكون فارغة.")
        
    result = pipeline.solve(raw_latex)
    if not result["success"]:
        raise HTTPException(status_code=422, detail="تعذر حل المعادلة أو التحقق من خطواتها رمزياً.")
        
    steps_models = [StepSchema(**s) for s in result["steps"]]
    
    return SolveResponse(
        success=True,
        equation_latex=result["equation_latex"],
        steps=steps_models,
        final_answer=result["final_answer"],
        total_steps=result["total_steps"],
        computation_time_ms=result["computation_time_ms"],
        verified=result["verified"]
    )


@app.post("/api/v1/verify", response_model=VerifyStepResponse)
def verify_step_endpoint(req: VerifyStepRequest):
    prev_eq = normalize_latex(req.previous_step_latex)
    curr_eq = normalize_latex(req.current_step_latex)
    
    valid = verify_step_equivalence(prev_eq, curr_eq)
    
    if valid:
        exp_ar = "الخطوة صحيحة رياضياً وتتسق تماماً مع الخطوة السابقة."
    else:
        exp_ar = "هناك خطأ جبري أو عدم تكافؤ بين هذه الخطوة والخطوة السابقة."
        
    return VerifyStepResponse(
        is_valid=valid,
        explanation_ar=exp_ar
    )


from ..vision.inference import recognize_latex_from_image

@app.post("/api/v1/ocr", response_model=OCRResponse)
async def ocr_endpoint(file: UploadFile = File(...)):
    contents = await file.read()
    res = recognize_latex_from_image(contents)
    return OCRResponse(
        success=True,
        latex=res["latex"],
        confidence=res["confidence"],
        is_syntax_valid=res["is_syntax_valid"]
    )
