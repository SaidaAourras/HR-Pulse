from fastapi import APIRouter , Depends  , HTTPException
from sqlalchemy.orm import Session
from backend.app.api.db.schemas.user import UserCreate , LoginRequest , TokenResponse
from backend.app.api.db.database import get_db
from backend.app.services.user_services import create_user , verify_user_is_exists
from backend.app.services.auth_services import  create_token


auth_router = APIRouter(prefix='/auth' ,tags=["authentication"])


@auth_router.post('/register')
def register(user:UserCreate , db:Session=Depends(get_db)):
    
    user_exists = verify_user_is_exists(user , db)
    
    if user_exists:
        raise HTTPException(
        status_code=400,
        detail="Email deja exists"
    )
        
    else:
        return create_user(user , db)
    
    


@auth_router.post('/login' , response_model=TokenResponse)
def login(user:LoginRequest , db:Session = Depends(get_db)):
    user_exists = verify_user_is_exists(user , db)
    
    if user_exists:
        token_payload = {
            "sub": str(user_exists.id),
            "email": user_exists.email
        }
        access_token = create_token(token_payload)
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer"
        )
            
    raise HTTPException(
        status_code=401,
        detail="Email ou mot de passe incorrect"
    )


@auth_router.post("/logout")
def logout():
    return {"message": "OK"}