@router.post("/setup")
async def setup(req: LoginRequest, db: Session = Depends(get_db)):
    try:
        exists = db.query(Admin).first()
        if exists:
            raise HTTPException(
                status_code=400, 
                detail="ادمین قبلاً ساخته شده"
            )

        admin = Admin(
            username = req.username,
            password = hash_password(req.password)
        )
        db.add(admin)
        db.commit()
        return {"message": "ادمین ساخته شد ✅"}
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Setup Error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
