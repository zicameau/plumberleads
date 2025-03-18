from typing import Dict, List, Optional
from datetime import datetime
from ..utils.supabase import supabase
from ..utils.errors import ValidationError, NotFoundError

class LeadService:
    @staticmethod
    def create_lead(data: Dict) -> Dict:
        """Create a new lead"""
        # Validate required fields
        required_fields = ['name', 'email', 'phone_number', 'description', 'zip_code']
        for field in required_fields:
            if not data.get(field):
                raise ValidationError(f"Missing required field: {field}")
        
        # Add timestamps
        data['created_at'] = datetime.utcnow().isoformat()
        data['updated_at'] = data['created_at']
        data['status'] = 'new'  # Initial status
        
        try:
            result = supabase.table("leads").insert(data).execute()
            return result.data[0]
        except ValueError as e:
            # Specifically catch the ValueError from our mock client
            if "Missing required field" in str(e):
                raise ValidationError(str(e))
            raise ValidationError(f"Failed to create lead: {str(e)}")
        except Exception as e:
            raise ValidationError(f"Failed to create lead: {str(e)}")
    
    @staticmethod
    def get_lead(lead_id: str) -> Dict:
        """Get a lead by ID"""
        try:
            result = supabase.table("leads").select("*").eq("id", lead_id).single().execute()
            if not result.data:
                raise NotFoundError(f"Lead not found with ID: {lead_id}")
            return result.data
        except NotFoundError as e:
            raise e
        except Exception as e:
            if "not found" in str(e).lower():
                raise NotFoundError(f"Lead not found with ID: {lead_id}")
            raise ValidationError(f"Failed to retrieve lead: {str(e)}")
    
    @staticmethod
    def update_lead(lead_id: str, data: Dict) -> Dict:
        """Update a lead"""
        # Don't allow updating certain fields
        protected_fields = ['id', 'created_at', 'plumber_id']
        update_data = {k: v for k, v in data.items() if k not in protected_fields}
        update_data['updated_at'] = datetime.utcnow().isoformat()
        
        try:
            result = supabase.table("leads").update(update_data).eq("id", lead_id).execute()
            if not result.data:
                raise NotFoundError(f"Lead not found with ID: {lead_id}")
            return result.data[0]
        except NotFoundError as e:
            raise e
        except ValueError as e:
            if "Invalid status" in str(e):
                raise ValidationError(str(e))
            raise ValidationError(f"Failed to update lead: {str(e)}")
        except Exception as e:
            raise ValidationError(f"Failed to update lead: {str(e)}")
    
    @staticmethod
    def list_leads(filters: Optional[Dict] = None, page: int = 1, per_page: int = 10) -> Dict:
        """List leads with optional filtering and pagination"""
        try:
            query = supabase.table("leads").select("*")
            
            # Apply filters if provided
            if filters:
                if filters.get('status'):
                    query = query.eq("status", filters['status'])
                if filters.get('zip_code'):
                    query = query.eq("zip_code", filters['zip_code'])
                if filters.get('plumber_id'):
                    query = query.eq("plumber_id", filters['plumber_id'])
            
            # Apply pagination
            start = (page - 1) * per_page
            query = query.range(start, start + per_page - 1)
            
            # Get total count for pagination
            count_query = supabase.table("leads").select("id", count="exact")
            if filters:
                if filters.get('status'):
                    count_query = count_query.eq("status", filters['status'])
                if filters.get('zip_code'):
                    count_query = count_query.eq("zip_code", filters['zip_code'])
                if filters.get('plumber_id'):
                    count_query = count_query.eq("plumber_id", filters['plumber_id'])
            
            result = query.execute()
            count_result = count_query.execute()
            
            return {
                "leads": result.data,
                "pagination": {
                    "total": count_result.count,
                    "page": page,
                    "per_page": per_page,
                    "total_pages": (count_result.count + per_page - 1) // per_page
                }
            }
        except Exception as e:
            raise ValidationError(f"Failed to list leads: {str(e)}")
    
    @staticmethod
    def assign_lead(lead_id: str, plumber_id: str) -> Dict:
        """Assign a lead to a plumber"""
        try:
            # Verify plumber exists
            plumber = supabase.table("plumbers").select("*").eq("id", plumber_id).single().execute()
            if not plumber.data:
                raise NotFoundError(f"Plumber not found with ID: {plumber_id}")
            
            # Update lead
            update_data = {
                'plumber_id': plumber_id,
                'status': 'assigned',
                'updated_at': datetime.utcnow().isoformat(),
                'assigned_at': datetime.utcnow().isoformat()
            }
            
            result = supabase.table("leads").update(update_data).eq("id", lead_id).execute()
            if not result.data:
                raise NotFoundError(f"Lead not found with ID: {lead_id}")
            
            return result.data[0]
        except NotFoundError as e:
            raise e
        except Exception as e:
            raise ValidationError(f"Failed to assign lead: {str(e)}")
    
    @staticmethod
    def update_lead_status(lead_id: str, status: str) -> Dict:
        """Update a lead's status"""
        valid_statuses = ['new', 'assigned', 'in_progress', 'completed', 'cancelled']
        if status not in valid_statuses:
            raise ValidationError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        try:
            update_data = {
                'status': status,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            result = supabase.table("leads").update(update_data).eq("id", lead_id).execute()
            if not result.data:
                raise NotFoundError(f"Lead not found with ID: {lead_id}")
            
            return result.data[0]
        except NotFoundError as e:
            raise e
        except ValueError as e:
            if "Invalid status" in str(e):
                raise ValidationError(str(e))
            raise ValidationError(f"Failed to update lead status: {str(e)}")
        except Exception as e:
            raise ValidationError(f"Failed to update lead status: {str(e)}") 