import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from pipeline.stage1_intent import extract_intent
from pipeline.stage2_architecture import design_architecture
from pipeline.stage3_schemas import generate_schemas
from pipeline.stage4_refinement import refine_bundle
from runtime.executor import run_runtime_checks

app = FastAPI(
    title="App Compiler API",
    description="Natural language to app schema compiler",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    prompt: str


class GenerateResponse(BaseModel):
    success: bool
    app_name: str
    is_valid: bool
    repair_attempts: int
    total_issues: int
    bundle: dict
    pipeline_log: list
    runtime: dict


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest):
    log = []

    if not request.prompt or len(request.prompt.strip()) < 10:
        raise HTTPException(
            status_code=400,
            detail="Prompt is too short. Please describe your app in more detail."
        )

    try:
        log.append("Stage 1 — Extracting intent...")
        intent = extract_intent(request.prompt)
        log.append(f"Intent extracted: {intent.app_name}")

        log.append("Stage 2 — Designing architecture...")
        arch = design_architecture(intent)
        log.append(f"Architecture designed: {len(arch.entities)} entities")

        log.append("Stage 3 — Generating schemas...")
        bundle = generate_schemas(intent, arch)
        log.append("Schemas generated: UI + API + DB + Auth")

        log.append("Stage 4 — Validating and repairing...")
        bundle = refine_bundle(bundle)
        log.append(f"Validation complete. Valid: {bundle.is_valid}")

        log.append("Runtime — Executing schemas...")
        runtime_result = run_runtime_checks(bundle)
        log.append(f"Runtime DB: {'✅ passed' if runtime_result['db']['success'] else '❌ failed'} — {len(runtime_result['db']['tables_created'])} tables created")
        log.append(f"Runtime API: {'✅ passed' if runtime_result['api']['success'] else '❌ failed'} — {len(runtime_result['api']['endpoints_validated'])} endpoints validated")
        log.append(f"Runtime overall: {'✅ PASSED' if runtime_result['success'] else '❌ FAILED'}")

        return GenerateResponse(
            success=True,
            app_name=intent.app_name,
            is_valid=bundle.is_valid,
            repair_attempts=bundle.repair_attempts,
            total_issues=len(bundle.validation_issues),
            bundle=bundle.model_dump(),
            pipeline_log=log,
            runtime=runtime_result
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline failed: {str(e)}"
        )


@app.get("/eval/results")
def eval_results():
    import json
    results_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "eval", "results.json")
    if not os.path.exists(results_path):
        return {"metrics": {}, "message": "No eval results yet. Run eval/runner.py first."}
    with open(results_path, "r") as f:
        results = json.load(f)
    from eval.metrics import compute_metrics
    return {"metrics": compute_metrics(results)}


# Serve React frontend — must be last
UI_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ui", "dist")

if os.path.exists(UI_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(UI_DIR, "assets")), name="assets")

    @app.get("/")
    def serve_frontend():
        return FileResponse(os.path.join(UI_DIR, "index.html"))

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        return FileResponse(os.path.join(UI_DIR, "index.html"))
else:
    @app.get("/")
    def root():
        return {"status": "App Compiler is running!"}