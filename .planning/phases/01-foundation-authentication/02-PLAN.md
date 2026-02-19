---
phase: 01-foundation-authentication
plan: 02
type: execute
wave: 2
depends_on: [01]
files_modified:
  - app/core/security.py
  - app/schemas/__init__.py
  - app/schemas/user.py
  - app/schemas/auth.py
  - app/services/__init__.py
  - app/services/auth.py
  - app/api/__init__.py
  - app/api/deps.py
  - app/api/auth.py
autonomous: true

must_haves:
  truths:
    - "User can POST email+password to /api/auth/login and receive JWT token"
    - "User can GET /api/auth/me with Bearer token and receive user info"
    - "Protected endpoints return 401 without valid token"
  artifacts:
    - path: "app/core/security.py"
      provides: "JWT creation/validation, password hashing"
      exports: ["create_access_token", "verify_password", "get_password_hash"]
    - path: "app/services/auth.py"
      provides: "Auth business logic"
      exports: ["AuthService"]
    - path: "app/api/deps.py"
      provides: "Current user dependency"
      exports: ["get_current_user"]
    - path: "app/api/auth.py"
      provides: "Login and me endpoints"
      contains: "router"
  key_links:
    - from: "app/api/auth.py"
      to: "app/services/auth.py"
      via: "AuthService.authenticate_user"
      pattern: "authenticate_user"
    - from: "app/api/deps.py"
      to: "app/core/security.py"
      via: "decode token"
      pattern: "create_access_token|verify_password"
---

<objective>
Implement JWT authentication system with login endpoint and protected endpoint dependency.

Purpose: Enable secure user authentication. Managers must be able to log in and receive a JWT token, which they use to access protected API endpoints.

Output: Working auth system with POST /api/auth/login, GET /api/auth/me, and get_current_user dependency for protecting other endpoints.
</objective>

<execution_context>
@~/.config/opencode/get-shit-done/workflows/execute-plan.md
@~/.config/opencode/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/research/SUMMARY.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create security utilities</name>
  <files>
    app/core/security.py
    requirements.txt
  </files>
  <action>
Create security utilities for JWT and password handling:

**Add to requirements.txt (if not present):**
```
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
```

**app/core/security.py:**
- PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")
- get_password_hash(password: str) -> str
- verify_password(plain_password: str, hashed_password: str) -> bool
- create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str
  - Uses python-jose jwt.encode()
  - Uses settings.SECRET_KEY and ALGORITHM (HS256)
  - Adds exp claim based on settings.ACCESS_TOKEN_EXPIRE_MINUTES

**Implementation pattern:**
```python
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return PWD_CONTEXT.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return PWD_CONTEXT.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
```

Do NOT use jsonwebtoken - CommonJS issues. Use python-jose.
  </action>
  <verify>
python -c "from app.core.security import create_access_token, verify_password, get_password_hash; print('Security module OK')"
  </verify>
  <done>
Password hashing and JWT token creation functions work. Can hash password, verify it, and create JWT.
  </done>
</task>

<task type="auto">
  <name>Task 2: Create Pydantic schemas and auth service</name>
  <files>
    app/schemas/__init__.py
    app/schemas/user.py
    app/schemas/auth.py
    app/services/__init__.py
    app/services/auth.py
  </files>
  <action>
Create Pydantic schemas and auth service:

**app/schemas/user.py:**
- UserBase: email (EmailStr)
- UserCreate: email, password (str, min_length=6)
- UserResponse: id (UUID), email, is_active, created_at

**app/schemas/auth.py:**
- LoginRequest: email (EmailStr), password (str)
- Token: access_token (str), token_type (str, default "bearer")
- TokenData: email (Optional[str])

**app/services/auth.py:**
- AuthService class with async methods:
  - authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]
    - Find user by email
    - Verify password with verify_password()
    - Return user if valid, None otherwise
  - get_current_user(db: AsyncSession, token: str) -> User
    - Decode JWT, extract email
    - Find user by email
    - Raise HTTPException(401) if invalid

**Import pattern:**
```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.user import User
from app.core.security import verify_password, create_access_token
```
  </action>
  <verify>
python -c "from app.services.auth import AuthService; from app.schemas.auth import LoginRequest, Token; print('Auth schemas and service OK')"
  </verify>
  <done>
Schemas validate login requests and token responses. AuthService can authenticate users.
  </done>
</task>

<task type="auto">
  <name>Task 3: Create auth API endpoints</name>
  <files>
    app/api/__init__.py
    app/api/deps.py
    app/api/auth.py
  </files>
  <action>
Create auth API endpoints with FastAPI router:

**app/api/deps.py:**
Create get_current_user dependency:
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.auth import AuthService

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    token = credentials.credentials
    return await AuthService.get_current_user(db, token)
```

**app/api/auth.py:**
Create router with two endpoints:
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserResponse
from app.services.auth import AuthService
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=Token)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await AuthService.authenticate_user(db, request.email, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    access_token = create_access_token(data={"sub": user.email})
    return Token(access_token=access_token)

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
```

**Note:** Import get_current_user from app.api.deps in auth.py.

Do NOT create main.py router registration here - that's in plan 04.
  </action>
  <verify>
python -c "from app.api.auth import router; from app.api.deps import get_current_user; print('Auth endpoints OK')"
  </verify>
  <done>
POST /auth/login accepts email+password, returns JWT. GET /auth/me returns user info with Bearer token. get_current_user dependency protects endpoints.
  </done>
</task>

</tasks>

<verification>
1. Security module: `python -c "from app.core.security import create_access_token, verify_password, get_password_hash"`
2. Schemas import: `python -c "from app.schemas.auth import LoginRequest, Token; from app.schemas.user import UserResponse"`
3. Service imports: `python -c "from app.services.auth import AuthService"`
4. API imports: `python -c "from app.api.auth import router; from app.api.deps import get_current_user"`
</verification>

<success_criteria>
- JWT token creation with configurable expiration
- Password hashing with bcrypt
- Login endpoint validates credentials and returns JWT
- /me endpoint returns user info with valid token
- get_current_user dependency raises 401 for invalid/missing tokens
</success_criteria>

<output>
After completion, create `.planning/phases/01-foundation-authentication/02-SUMMARY.md`
</output>
