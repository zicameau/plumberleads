from typing import Dict, Optional
from ..utils.supabase import supabase
from ..utils.errors import AuthenticationError, ValidationError

class AuthService:
    @staticmethod
    def register_plumber(data: Dict) -> Dict:
        """Register a new plumber with Supabase Auth and create plumber record"""
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
            
            response = supabase.table("plumbers").insert(plumber_data).execute()
            
            return {
                "id": auth_response.user.id,
                "email": data["email"],
                "first_name": data["first_name"],
                "last_name": data["last_name"],
                "phone_number": data["phone_number"]
            }
            
        except Exception as e:
            # If user was created but plumber record failed, we should clean up
            if 'auth_response' in locals() and auth_response.user:
                try:
                    # TODO: Implement user deletion in case of failure
                    pass
                except:
                    pass
            raise AuthenticationError(str(e))
    
    @staticmethod
    def login(email: str, password: str) -> Dict:
        """Login a plumber"""
        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if not response.user or not response.session:
                raise AuthenticationError("Invalid credentials")
            
            # Get plumber details
            plumber = supabase.table("plumbers").select("*").eq("id", response.user.id).single().execute()
            
            return {
                "token": response.session.access_token,
                "user": {
                    "id": response.user.id,
                    "email": response.user.email,
                    **plumber.data
                }
            }
            
        except Exception as e:
            raise AuthenticationError(str(e))
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict]:
        """Verify JWT token and return user info"""
        try:
            user = supabase.auth.get_user(token)
            if not user:
                return None
                
            # Get plumber details
            plumber = supabase.table("plumbers").select("*").eq("id", user.id).single().execute()
            
            return {
                "id": user.id,
                "email": user.email,
                **plumber.data
            }
            
        except Exception:
            return None
    
    @staticmethod
    def logout(token: str) -> bool:
        """Logout user and invalidate token"""
        try:
            supabase.auth.sign_out()
            return True
        except Exception as e:
            raise AuthenticationError(str(e)) 