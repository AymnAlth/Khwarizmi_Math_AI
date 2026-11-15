from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field

class StepSchema(BaseModel):
    step_num: int = Field(..., description="رقم الخطوة التسلسلي")
    rule_code: str = Field(..., description="رمز القاعدة الرياضية المطبقة")
    rule_name_ar: str = Field("خطوة استدلالية منهجية", description="اسم القاعدة باللغة العربية")
    latex: str = Field(..., description="الصيغة الرياضية بصيغة LaTeX")
    explanation_ar: str = Field(..., description="الشرح التربوي المبسط باللغة العربية")
    status: str = Field("VERIFIED", description="حالة الفحص الرمزي: VERIFIED أو INVALID")

class SolveRequest(BaseModel):
    equation_latex: Optional[str] = Field(None, example="2x + 4 = 10", description="المعادلة الرياضية بصيغة نصية أو LaTeX")
    equation: Optional[str] = Field(None, example="6/8", description="اسم حقل بديل للمعادلة لمرونة الربط")
    curriculum_stage: Optional[str] = Field("auto", description="مستوى المنهج: basic_algebra, advanced_algebra, calculus, auto")

    @property
    def raw_equation(self) -> str:
        return (self.equation_latex or self.equation or "").strip()

class SolveResponse(BaseModel):
    success: bool
    equation_latex: str
    steps: List[StepSchema]
    final_answer: str
    total_steps: int
    computation_time_ms: float
    verified: bool

class VerifyStepRequest(BaseModel):
    previous_step_latex: str = Field(..., description="الخطوة السابقة")
    current_step_latex: str = Field(..., description="خطوة الطالب المراد التحقق منها")
    claimed_rule: Optional[str] = None

class VerifyStepResponse(BaseModel):
    is_valid: bool
    explanation_ar: str
    symbolic_delta: Optional[str] = None

class OCRResponse(BaseModel):
    success: bool
    latex: str
    confidence: float
    is_syntax_valid: bool
