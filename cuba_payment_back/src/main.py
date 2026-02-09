"""Main FastAPI application"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from datetime import timedelta
from .schemas.schemas import (
    UserLogin,
    UserRegister,
    Token,
    User,
    UserRole,
    Distance
    )
from .auth.auth import (
    create_access_token,
    get_password_hash,
    verify_password,
    get_current_user,
    get_manager_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    TokenData,
)
from .database import connect_db, close_db, get_users_collection

app = FastAPI(
    title="Cuba Payment API",
    description="Backend API for Cuba Payment application",
    version="0.1.0"
)


# Event handlers for database connection
@app.on_event("startup")
async def startup_event():
    """Connect to database on startup"""
    connect_db()


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    close_db()


# ============================================================================
# Public endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Cuba Payment API"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/auth/register", response_model=User)
async def register(user_data: UserRegister):
    """Register a new user (client or manager)"""
    users_collection = get_users_collection()

    # Check if user already exists
    existing_user = users_collection.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)

    user_dict = {
        "email": user_data.email,
        "full_name": user_data.full_name,
        "hashed_password": hashed_password,
        "role": user_data.role,
        "is_active": True
    }

    users_collection.insert_one(user_dict)

    return User(
        email=user_data.email,
        full_name=user_data.full_name,
        role=user_data.role,
        is_active=True
    )


@app.post("/auth/login", response_model=Token)
async def login(credentials: UserLogin):
    users_collection = get_users_collection()

    # Find user by email
    user_db = users_collection.find_one({"email": credentials.email})

    if not user_db or not verify_password(
        credentials.password, user_db["hashed_password"]
         ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user_db["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_db["email"], "role": user_db["role"]},
        expires_delta=access_token_expires
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        role=UserRole(user_db["role"])
    )


@app.post("/distance")
async def distance(
    distance: Distance,
    current_user: TokenData = Depends(get_current_user)
     ):
    """Calculate distance between two coordinates - Public endpoint"""
    from .geolocation.distance_calculator import route_distance
    try:
        distance_m, duration_s = route_distance(
            distance.lat1,
            distance.lon1,
            distance.lat2,
            distance.lon2
            )
    except Exception as e:
        print("Exception at distance calculator: ", e)
        return JSONResponse(
            content={
                "error": str(e),
                },
            status_code=500
        )
    return JSONResponse(
        content={
            "distance_m": distance_m,
            "duration_s": duration_s
            },
        status_code=200
        )


# ============================================================================
# Protected endpoints - Manager only
# ============================================================================

@app.get("/manager/users")
async def get_all_users(current_user: TokenData = Depends(get_manager_user)):
    """Get all users - Manager only endpoint"""
    users_collection = get_users_collection()
    users = list(users_collection.find({}, {"hashed_password": 0}))

    # Convert MongoDB ObjectId to string
    for user in users:
        user["id"] = str(user.pop("_id"))

    return {"users": users, "manager": current_user.email}


@app.patch("/manager/users/{email}/deactivate")
async def deactivate_user(
    email: str,
    current_user: TokenData = Depends(get_manager_user)
     ):
    """Deactivate a user - Manager only endpoint"""
    users_collection = get_users_collection()

    result = users_collection.update_one(
        {"email": email},
        {"$set": {"is_active": False}}
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {
        "message": f"User {email} deactivated",
        "manager": current_user.email
        }


# ============================================================================
# Protected endpoints - Any authenticated user
# ============================================================================

@app.get("/profile", response_model=User)
async def get_profile(current_user: TokenData = Depends(get_current_user)):
    """Get current user profile - Requires authentication"""
    users_collection = get_users_collection()
    user_db = users_collection.find_one({"email": current_user.email})

    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return User(
        email=user_db["email"],
        full_name=user_db["full_name"],
        role=UserRole(user_db["role"]),
        is_active=user_db["is_active"]
    )
