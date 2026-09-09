from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.database import get_db
from backend.models import Admin, Customer, Message, Payment
from backend.auth import (
    hash_password, verify_password,
    create_token, get_admin, generate_api_key
)
from datetime import datetime, timedelta

router = APIRouter(prefix="/admin", tags=["Admin"])

# ─── مدل‌ها ───────────────────────────────────
class LoginRequest(BaseModel):
    username: str
    password: str

class CustomerCreate(BaseModel):
    name:     str
    business: str
    phone:    str
    category: str
    plan:     str = "basic"
    days:     int = 30

class CustomerUpdate(BaseModel):
    is_active: bool = True
    plan:      str  = "basic"
    days:      int  = 30

# ─── لاگین ادمین ──────────────────────────────
@router.post("/login")
async def login(req: LoginRequest, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(
        Admin.username == req.username
    ).first()

    if not admin or not verify_password(req.password, admin.password):
        raise HTTPException(status_code=401, detail="اطلاعات اشتباه است")

    token = create_token({"admin": True, "username": req.username})
    return {"token": token, "username": req.username}

# ─── لیست مشتریان ─────────────────────────────
@router.get("/customers")
async def get_customers(
    admin = Depends(get_admin),
    db: Session = Depends(get_db)
):
    customers = db.query(Customer).all()
    return [{
        "id":         c.id,
        "name":       c.name,
        "business":   c.business,
        "phone":      c.phone,
        "category":   c.category,
        "plan":       c.plan,
        "is_active":  c.is_active,
        "api_key":    c.api_key,
        "expires_at": c.expires_at,
        "created_at": c.created_at,
        "msg_count":  len(c.messages)
    } for c in customers]

# ─── افزودن مشتری ─────────────────────────────
@router.post("/customers")
async def add_customer(
    req: CustomerCreate,
    admin = Depends(get_admin),
    db: Session = Depends(get_db)
):
    # چک تکراری
    exists = db.query(Customer).filter(
        Customer.phone == req.phone
    ).first()
    if exists:
        raise HTTPException(status_code=400, detail="این شماره قبلاً ثبت شده")

    customer = Customer(
        name       = req.name,
        business   = req.business,
        phone      = req.phone,
        category   = req.category,
        plan       = req.plan,
        api_key    = generate_api_key(),
        expires_at = datetime.now() + timedelta(days=req.days)
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    return {
        "message":  "مشتری اضافه شد ✅",
        "api_key":  customer.api_key,
        "customer": customer.name
    }

# ─── ویرایش مشتری ─────────────────────────────
@router.put("/customers/{customer_id}")
async def update_customer(
    customer_id: int,
    req: CustomerUpdate,
    admin = Depends(get_admin),
    db: Session = Depends(get_db)
):
    customer = db.query(Customer).filter(
        Customer.id == customer_id
    ).first()

    if not customer:
        raise HTTPException(status_code=404, detail="مشتری پیدا نشد")

    customer.is_active  = req.is_active
    customer.plan       = req.plan
    customer.expires_at = datetime.now() + timedelta(days=req.days)

    db.commit()
    return {"message": "مشتری آپدیت شد ✅"}

# ─── حذف مشتری ────────────────────────────────
@router.delete("/customers/{customer_id}")
async def delete_customer(
    customer_id: int,
    admin = Depends(get_admin),
    db: Session = Depends(get_db)
):
    customer = db.query(Customer).filter(
        Customer.id == customer_id
    ).first()

    if not customer:
        raise HTTPException(status_code=404, detail="مشتری پیدا نشد")

    db.delete(customer)
    db.commit()
    return {"message": "مشتری حذف شد ✅"}

# ─── ساخت ادمین اول ───────────────────────────
@router.post("/setup")
async def setup(req: LoginRequest, db: Session = Depends(get_db)):
    exists = db.query(Admin).first()
    if exists:
        raise HTTPException(status_code=400, detail="ادمین قبلاً ساخته شده")

    admin = Admin(
        username = req.username,
        password = hash_password(req.password)
    )
    db.add(admin)
    db.commit()
    return {"message": "ادمین ساخته شد ✅"}
