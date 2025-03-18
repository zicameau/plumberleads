from typing import Dict, Optional
from ..utils.supabase import supabase
from ..utils.errors import AuthenticationError, ValidationError

class AuthService:
    @staticmethod
    def register_plumber(data: Dict) -> Dict:
        """Register a new plumber"""
        try:
            # Register user with Supabase Auth
            auth_response = supabase.auth.sign_up({
                "email": data["email"],
                "password": data["password"]
            })
            
            if not auth_response.user:
                raise AuthenticationError("Failed to create user")
            
            # Create plumber record in database
            plumber_data = {
                "id": auth_response.user.id,
                "email": data["email"],
                "first_name": data["first_name"],
                "last_name": data["last_name"],
                "phone_number": data["phone_number"]
            }
            
            # Add optional fields if present
            if "zip_code" in data:
                plumber_data["zip_code"] = data["zip_code"]
            if "services" in data:
                plumber_data["services"] = data["services"]
            
            plumber = supabase.table("plumbers").insert(plumber_data).execute()
            
            return {
                "message": "Plumber registered successfully",
                "user": plumber.data[0]
            }
            
        except Exception as e:
            raise AuthenticationError("Failed to create user") from e
    
    @staticmethod
    def login(email: str, password: str) -> Dict:
        """Login a plumber"""
        try:
            auth_response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if not auth_response.user or not auth_response.session:
                raise AuthenticationError("Invalid credentials")
            
            return {
                "message": "Login successful",
                "token": auth_response.session.access_token,
                "user": {
                    "id": auth_response.user.id,
                    "email": auth_response.user.email
                }
            }
            
        except Exception as e:
            raise AuthenticationError("Invalid credentials") from e
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict]:
        """Verify JWT token and return user info"""
        try:
            user = supabase.auth.get_user(token)
            return {
                "id": user.id,
                "email": user.email
            }
        except Exception as e:
            raise AuthenticationError("Invalid token") from e
    
    @staticmethod
    def logout(token: str) -> bool:
        """Logout a plumber"""
        try:
            supabase.auth.sign_out()
            return True
        except Exception as e:
            raise AuthenticationError("Auth service error") from e 