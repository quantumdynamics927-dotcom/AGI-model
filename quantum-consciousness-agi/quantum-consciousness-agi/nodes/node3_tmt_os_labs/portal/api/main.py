from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pathlib import Path
import json
import os
import shutil

app = FastAPI(title="TMT-OS Labs Portal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Default delivery root (can be overridden with env var TMTOS_DELIVERY_ROOT)
DELIVERY_ROOT = Path(os.getenv('TMTOS_DELIVERY_ROOT', str(Path(__file__).resolve().parents[3] / 'research_workspace')))
CERT_DIR = DELIVERY_ROOT  # store certificates next to deliveries

# Import local safety helpers
# Validation is deferred to startup event to avoid import-time failures during testing
def _validate_delivery_root():
    """Validate DELIVERY_ROOT is local when enforcement is enabled."""
    try:
        from security import safety
        if os.getenv('TMTOS_ENFORCE_LOCAL_PATHS', 'true').lower() == 'true' and not safety.is_local_path(str(DELIVERY_ROOT)):
            raise RuntimeError(f"Configured DELIVERY_ROOT is not a local path: {DELIVERY_ROOT}")
    except ImportError:
        pass  # security module not available - skip check

@app.on_event("startup")
async def startup_event():
    _validate_delivery_root() 


@app.get("/")
async def root():
    return FileResponse(Path(__file__).parent.parent / "frontend" / "index.html", media_type='text/html')


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/certificates")
async def list_certificates():
    # Find all .nft.json files under DELIVERY_ROOT
    if not DELIVERY_ROOT.exists():
        raise HTTPException(status_code=404, detail=f"Delivery root not found: {DELIVERY_ROOT}")

    results = []
    for p in DELIVERY_ROOT.rglob("*.nft.json"):
        try:
            data = json.loads(p.read_text())
            base = p.stem  # e.g. file.fa.nft
            results.append({
                "path": str(p),
                "name": base,
                "metadata": data
            })
        except Exception:
            continue
    return JSONResponse(results)


@app.get("/certificate/{name}")
async def get_certificate(name: str):
    # name expected to match filename (without path)
    files = list(DELIVERY_ROOT.rglob(f"{name}*.nft.json"))
    if not files:
        raise HTTPException(status_code=404, detail="Certificate not found")
    p = files[0]
    return JSONResponse(json.loads(p.read_text()))


@app.get("/certificate/{name}/image")
async def get_certificate_image(name: str):
    # Robustly find the certificate JSON by name (allow substring/prefix matches)
    # Try exact and flexible matches
    patterns = [f"{name}*.nft.json", f"*{name}*.nft.json", f"{name}.nft.json", f"{name}.json"]
    files = []
    for pat in patterns:
        files = list(DELIVERY_ROOT.rglob(pat))
        if files:
            break

    if not files:
        # Try substring search over all nft.json files
        all_nfts = list(DELIVERY_ROOT.rglob("*.nft.json"))
        for p in all_nfts:
            if name in p.name or name in p.stem:
                files.append(p)
                break

    if not files:
        raise HTTPException(status_code=404, detail="Certificate not found")

    p = files[0]

    # Candidate png names (try multiple possible naming conventions)
    candidates = []
    candidates.append(p.with_suffix(p.suffix + '.certificate.png'))  # ...nft.json.certificate.png
    candidates.append(Path(str(p) + '.certificate.png'))            # ...nft.json.certificate.png (fallback)
    candidates.append(p.with_suffix('.certificate.png'))              # replace .json with .certificate.png
    candidates.append(p.with_suffix('.png'))                          # ...nft.png
    # Also search for any png that contains the stem
    stem = p.stem
    for png in p.parent.glob(f"*{stem}*.png"):
        candidates.append(png)

    for png in candidates:
        if png and png.exists():
            return FileResponse(png, media_type='image/png')

    raise HTTPException(status_code=404, detail="Certificate image not found")


@app.post("/certificates/upload")
async def upload_certificate(nft: UploadFile = File(...), certificate_img: UploadFile = File(None), client_name: str = Form(None)):
    """Accepts an uploaded .nft.json file and optional certificate image and saves to DELIVERY_ROOT.

    For safety this endpoint is disabled by default; enable uploads by setting environment variable
    TMTOS_ALLOW_UPLOAD='true'.
    """
    # Upload protection: do not allow uploads unless explicitly enabled by env var
    if os.getenv('TMTOS_ALLOW_UPLOAD', 'false').lower() != 'true':
        raise HTTPException(status_code=403, detail="Uploads are disabled by configuration (TMTOS_ALLOW_UPLOAD must be 'true' to enable)")

    if not DELIVERY_ROOT.exists():
        raise HTTPException(status_code=500, detail="Delivery root not available")

    # Save nft.json
    name = nft.filename
    dest = CERT_DIR / name
    with dest.open('wb') as f:
        shutil.copyfileobj(nft.file, f)

    # Save image if provided
    img_path = None
    if certificate_img:
        img_name = certificate_img.filename
        img_path = CERT_DIR / img_name
        with img_path.open('wb') as f:
            shutil.copyfileobj(certificate_img.file, f)

    # Load metadata to return
    try:
        meta = json.loads(dest.read_text())
    except Exception:
        meta = {}

    return JSONResponse({"saved": str(dest), "image": str(img_path) if img_path else None, "metadata": meta})
