import os
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2AuthorizationCodeBearer
import requests
import json
from typing import Optional

load_dotenv(dotenv_path=".env", override=True)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
SESSION_SECRET = os.getenv("SESSION_SECRET")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


def env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


BYPASS_OAUTH = env_bool("BYPASS_OAUTH", False)

router = APIRouter(prefix="/auth", tags=["authentication"])

# In-memory session storage (in production, use Redis or database)
sessions = {}


def get_session_user(session_id: Optional[str]) -> Optional[dict]:
    if not session_id:
        return None
    return sessions.get(session_id)

@router.get("/login")
async def login():
    """Redirect to Google OAuth login"""
    if BYPASS_OAUTH:
        mock_email = os.getenv("BYPASS_EMAIL", "student@ucsb.edu")
        mock_name = os.getenv("BYPASS_NAME", "UCSB Student")
        session_id = f"session_{hash(mock_email)}"
        sessions[session_id] = {
            "email": mock_email,
            "name": mock_name,
            "picture": "https://ui-avatars.com/api/?name=UCSB+Student&background=003660&color=febc11&size=120",
            "verified": True,
        }
        return RedirectResponse(url=f"{FRONTEND_URL}?session={session_id}")

    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Google Client ID not configured")
    
    redirect_uri = "http://localhost:8000/auth/callback"
    scope = "openid email profile"
    
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?" \
               f"client_id={GOOGLE_CLIENT_ID}&" \
               f"redirect_uri={redirect_uri}&" \
               f"response_type=code&" \
               f"scope={scope}&" \
               f"access_type=offline"
    
    return RedirectResponse(url=auth_url)

@router.get("/callback")
async def callback(code: str):
    """Handle Google OAuth callback"""
    try:
        # Exchange authorization code for access token
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": "http://localhost:8000/auth/callback"
        }
        
        response = requests.post(token_url, data=data)
        token_data = response.json()
        
        if "error" in token_data:
            raise HTTPException(status_code=400, detail=f"OAuth error: {token_data['error']}")
        
        access_token = token_data.get("access_token")
        
        # Get user info
        user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        user_response = requests.get(user_info_url, headers=headers)
        user_data = user_response.json()
        
        # Validate email domain
        email = user_data.get("email", "")
        if not email.endswith("@ucsb.edu"):
            raise HTTPException(
                status_code=403, 
                detail="Access denied. Only @ucsb.edu email addresses are allowed."
            )
        
        # Create session
        session_id = f"session_{hash(email)}"
        sessions[session_id] = {
            "email": email,
            "name": user_data.get("name", ""),
            "picture": user_data.get("picture", ""),
            "verified": user_data.get("verified_email", False)
        }
        
        # Redirect to frontend with session info
        frontend_url = f"{FRONTEND_URL}?session={session_id}"
        return RedirectResponse(url=frontend_url)
        
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Token exchange failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")

@router.get("/me")
async def get_user(session: str):
    """Get current user info from session"""
    if session not in sessions:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    return {
        "email": sessions[session]["email"],
        "name": sessions[session]["name"],
        "picture": sessions[session]["picture"],
        "verified": sessions[session]["verified"]
    }

@router.post("/logout")
async def logout(session: str):
    """Logout user and invalidate session"""
    if session in sessions:
        del sessions[session]
    
    return {"message": "Logged out successfully"}

@router.get("/check")
async def check_session(session: str):
    """Check if session is valid"""
    return {"valid": session in sessions}
