from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
import uuid
import datetime
import os
from supabase import create_client, Client

router = APIRouter(prefix="/api/stickers")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
BUCKET = "sticker-receipts"

_client: Client | None = None


def get_supabase() -> Client:
    global _client
    if _client is None:
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client


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
    contents = await receipt.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")

    submission_id = str(uuid.uuid4())[:8]
    safe_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in (receipt.filename or "file"))
    receipt_filename = f"{submission_id}_{safe_name}"

    sb = get_supabase()

    # Upload receipt to Supabase Storage
    sb.storage.from_(BUCKET).upload(
        path=receipt_filename,
        file=contents,
        file_options={"content-type": receipt.content_type or "application/octet-stream"},
    )

    receipt_url = sb.storage.from_(BUCKET).get_public_url(receipt_filename)

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
        "receipt_url": receipt_url,
        "submitted_at": datetime.datetime.utcnow().isoformat() + "Z",
    }

    sb.table("sticker_submissions").insert(entry).execute()

    return JSONResponse({"status": "ok", "id": submission_id})


@router.get("/submissions")
def get_submissions():
    sb = get_supabase()
    result = sb.table("sticker_submissions").select("*").order("submitted_at", desc=True).execute()
    return JSONResponse(result.data)


@router.patch("/submission/{submission_id}")
async def update_submission(submission_id: str, request: Request):
    body = await request.json()
    allowed = {"sticker_count", "plate_number", "amount_paid", "payment_name", "payment_method", "payment_date", "phone", "address", "owner_name"}
    updates = {k: v for k, v in body.items() if k in allowed}
    if not updates:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    sb = get_supabase()
    result = sb.table("sticker_submissions").update(updates).eq("id", submission_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Submission not found")
    return JSONResponse({"status": "ok"})


@router.post("/manual-add")
async def manual_add(request: Request):
    body = await request.json()
    required = {"full_name", "phone", "address", "plate_number", "sticker_count"}
    if not required.issubset(body.keys()):
        raise HTTPException(status_code=400, detail="Missing required fields")

    entry = {
        "id": str(uuid.uuid4())[:8],
        "full_name": body.get("full_name", ""),
        "phone": body.get("phone", ""),
        "address": body.get("address", ""),
        "owner_name": body.get("owner_name", ""),
        "plate_number": body.get("plate_number", ""),
        "sticker_count": str(body.get("sticker_count", 1)),
        "amount_paid": str(body.get("amount_paid", "")),
        "payment_method": body.get("payment_method", ""),
        "payment_name": body.get("payment_name", ""),
        "payment_date": body.get("payment_date", ""),
        "receipt_filename": "",
        "receipt_url": "",
        "submitted_at": datetime.datetime.utcnow().isoformat() + "Z",
        "added_by_admin": True,
    }

    get_supabase().table("sticker_submissions").insert(entry).execute()
    return JSONResponse({"status": "ok", "id": entry["id"]})


@router.get("/receipt/{receipt_id}")
def get_receipt(receipt_id: str):
    sb = get_supabase()
    result = sb.table("sticker_submissions").select("receipt_filename,receipt_url").eq("id", receipt_id).maybe_single().execute()
    if not result.data or not result.data.get("receipt_url"):
        raise HTTPException(status_code=404, detail="Receipt not found")
    return RedirectResponse(url=result.data["receipt_url"])
