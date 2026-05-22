import tempfile
import os

from app.database import get_db
from app.models import User
from app.crud import hash_password
import csv
from fastapi import UploadFile, File, Depends, HTTPException, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

router = APIRouter()


BATCH_SIZE = 1000

@router.post("/upload-users")
async def upload_users(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV allowed")

    tmp_path = None

    try:
        # stream upload to disk
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            while chunk := await file.read(1024 * 1024):
                tmp.write(chunk)
            tmp_path = tmp.name

        batch = []
        inserted_count = 0

        with open(tmp_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            # print(reader)

            for row in reader:
                identification = str(row.get("Identification No.", "")).strip()

                if "/" not in identification:
                    continue

                parts = identification.split("/")
                if len(parts) < 2:
                    continue

                regno = parts[1].strip()

                if not regno or regno.lower() == "nan":
                    continue

                user = User(
                    regno=regno,
                    first_name=str(row.get("First Name", "")).strip(),
                    last_name=str(row.get("Last Name", "")).strip(),
                    password_hash=hash_password(regno),#"00000000"),
                    is_staff=False,
                )

                batch.append(user)

                # batch insert
                if len(batch) >= BATCH_SIZE:
                    db.add_all(batch)
                    await db.commit()
                    inserted_count += len(batch)
                    batch.clear()

            # final batch
            if batch:
                db.add_all(batch)
                await db.commit()
                inserted_count += len(batch)

        return {
            "message": "CSV import successful",
            "count": inserted_count
        }

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)