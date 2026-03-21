from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models.profiles import Profile
from ..schemas import user as UserSchemas
from ..config.supabase import get_supabase
from ..config.database import get_db

router = APIRouter()

@router.post("/sign_up", response_model=UserSchemas.UserSession)
async def sign_up(new_user: UserSchemas.UserCreate,
                  db: Session = Depends(get_db),
                  supabase = Depends(get_supabase)):

        response = supabase.auth.sign_up(
                {
                        "email": new_user.email,
                        "password": new_user.password,
                }
        )

        if not response.user:
                raise HTTPException(status_code=400, detail="Signup failed")
        
        try:
                profile = Profile(user_id=response.user.id)
                db.add(profile)
                db.commit()
        except Exception:
                db.rollback()
                raise

        session = response.session

        if not response.session:
                raise HTTPException(
                        status_code=400,
                        detail="Signup succeeded but no session returned (email confirmation may be required)"
                )
        
        return {
                "access_token": session.access_token, 
                "refresh_token": session.refresh_token, 
                "expires_in": session.expires_in, 
                "token_type": session.token_type,
        }

@router.post("/login", response_model=UserSchemas.UserSession)
async def login(user: UserSchemas.UserLogin,
                supabase = Depends(get_supabase)):

        response = supabase.auth.sign_in_with_password(
                {
                        "email": user.email,
                        "password": user.password,
                }
        )
        if not response.user:
                raise HTTPException(status_code=400, detail="Login failed")

        session = response.session
        if not response.session:
                raise HTTPException(
                        status_code=400,
                        detail="Login succeeded but no session returned (email confirmation may be required)"
                )
        return {
                "access_token": session.access_token, 
                "refresh_token": session.refresh_token, 
                "expires_in": session.expires_in, 
                "token_type": session.token_type,
        }