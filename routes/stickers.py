from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
import json
import uuid
import datetime
from pathlib import Path

router = APIRouter(prefix="/api/stickers")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SUBMISSIONS_FILE = DATA_DIR / "sticker_submissions.json"
RECEIPTS_DIR = DATA_DIR / "sticker_receipts"


def load_submissions():
    if not SUBMISSIONS_FILE.exists():
        return []
    with SUBMISSIONS_FILE.open("r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return []


def save_submissions(data):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with SUBMISSIONS_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@router.post("/submit")
async def submit_sticker(
    full_name: str = Form(...),
    phone: str = Form(...),
    address: str = Form(...),
    owner_name: str = Form(""),
    plate_number: str = Form(...),
    sticker_count: str = Form(...),
    amount_paid: str = Form(""),
    payment_method: str = Form(...),
    payment_name: str = Form(...),
    payment_date: str = Form(...),
    receipt: UploadFile = File(...),
):
    RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)

    submission_id = str(uuid.uuid4())[:8]
    safe_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in (receipt.filename or "file"))
    receipt_filename = f"{submission_id}_{safe_name}"
    receipt_path = RECEIPTS_DIR / receipt_filename

    contents = await receipt.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")

    with receipt_path.open("wb") as f:
        f.write(contents)

    submissions = load_submissions()
    entry = {
        "id": submission_id,
        "full_name": full_name,
        "phone": phone,
        "address": address,
        "owner_name": owner_name,
        "plate_number": plate_number,
        "sticker_count": sticker_count,
        "amount_paid": amount_paid,
        "payment_method": payment_method,
        "payment_name": payment_name,
        "payment_date": payment_date,
        "receipt_filename": receipt_filename,
        "submitted_at": datetime.datetime.utcnow().isoformat() + "Z",
    }
    submissions.append(entry)
    save_submissions(submissions)

    return JSONResponse({"status": "ok", "id": submission_id})


@router.get("/submissions")
def get_submissions():
    return JSONResponse(load_submissions())


@router.get("/receipt/{receipt_id}")
def get_receipt(receipt_id: str):
    RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
    for f in RECEIPTS_DIR.iterdir():
        if f.name.startswith(receipt_id + "_"):
            return FileResponse(str(f))
    raise HTTPException(status_code=404, detail="Receipt not found")
