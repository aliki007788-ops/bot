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

# ─── مدل‌های درخواست (Pydantic) ─────────────────
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

class ChangePasswordRequest(BaseModel):
    new_password: str

# ─── ساخت اولین ادمین (Setup) ───────────────────
@router.post("/setup")
async def setup(req: LoginRequest, db: Session = Depends(get_db)):
    exists = db.query(Admin).first()
    if exists:
        raise HTTPException(status_code=400, detail="ادمین قبلاً ساخته شده است")

    admin = Admin(
        username = req.username,
        password = hash_password(req.password)
    )
    db.add(admin)
    db.commit()
    return {"message": "ادمین با موفقیت ساخته شد ✅"}

# ─── لاگین ادمین ─────────────────────────────────
@router.post("/login")
async def login(req: LoginRequest, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(
        Admin.username == req.username
    ).first()

    if not admin or not verify_password(req.password, admin.password):
        raise HTTPException(status_code=401, detail="نام کاربری یا رمز عبور اشتباه است")

    token = create_token({"admin": True, "username": req.username})
    return {"token": token, "username": req.username}

# ─── تغییر رمز عبور ادمین ────────────────────────
@router.put("/change-password")
async def change_admin_password(
    req: ChangePasswordRequest,
    admin = Depends(get_admin),
    db: Session = Depends(get_db)
):
    # پیدا کردن ادمین بر اساس نام کاربری موجود در توکن
    admin_user = db.query(Admin).filter(
        Admin.username == admin["username"]
    ).first()

    if not admin_user:
        raise HTTPException(status_code=404, detail="ادمین پیدا نشد")

    # هش کردن رمز جدید و ذخیره در دیتابیس
    admin_user.password = hash_password(req.new_password)
    db.commit()
    
    return {"message": "رمز عبور با موفقیت تغییر کرد ✅"}

# ─── لیست مشتریان ────────────────────────────────
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
        "expires_at": c.expires_at.isoformat() if c.expires_at else None,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "msg_count":  len(c.messages)
    } for c in customers]

# ─── افزودن مشتری جدید ──────────────────────────
@router.post("/customers")
async def add_customer(
    req: CustomerCreate,
    admin = Depends(get_admin),
    db: Session = Depends(get_db)
):
    # بررسی تکراری نبودن شماره تلفن
    exists = db.query(Customer).filter(
        Customer.phone == req.phone
    ).first()
    if exists:
        raise HTTPException(status_code=400, detail="این شماره تلفن قبلاً ثبت شده است")

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
        "message":  "مشتری با موفقیت اضافه شد ✅",
        "api_key":  customer.api_key,
        "customer": customer.name
    }

# ─── ویرایش وضعیت مشتری ─────────────────────────
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
        raise HTTPException(status_code=404, detail="مشتری مورد نظر پیدا نشد")

    customer.is_active  = req.is_active
    customer.plan       = req.plan
    customer.expires_at = datetime.now() + timedelta(days=req.days)

    db.commit()
    return {"message": "اطلاعات مشتری با موفقیت به‌روزرسانی شد ✅"}

# ─── حذف مشتری ──────────────────────────────────
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
        raise HTTPException(status_code=404, detail="مشتری مورد نظر پیدا نشد")

    db.delete(customer)
    db.commit()
    return {"message": "مشتری با موفقیت حذف شد ✅"}
