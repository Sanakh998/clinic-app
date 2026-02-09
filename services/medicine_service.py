from database.medicine_database import MedicineDatabaseManager

class MedicineService:
    def __init__(self, db_manager: MedicineDatabaseManager):
        self.db = db_manager

    def create_medicine(self, name, category, manufacturer="", is_restricted=False, notes=""):
        # Validation: Check if name already exists? (Maybe database constraint handles this?)
        # For now, let's trust the database or handle errors.
        
        # Upper case name for consistency
        name = name.strip().upper()
        
        medicine_id = self.db.create_medicine(name, category, manufacturer, is_restricted, notes)
        return medicine_id

    def add_variant(self, medicine_id, potency, form, bottle_size, unit_type, min_stock_level, expiry_date=None):
        # Additional validation logic here if needed
        return self.db.create_variant(medicine_id, potency, form, bottle_size, unit_type, min_stock_level, expiry_date)

    def get_medicine_details(self, medicine_id):
        # Prepare a full object with variants
        master = self.db.get_medicine_master(medicine_id)
        if not master:
            return None
            
        variants = self.db.get_variants_for_medicine(medicine_id)
        
        return {
            "id": master[0],
            "name": master[1],
            "category": master[2],
            "manufacturer": master[3],
            "is_restricted": bool(master[5]),
            "notes": master[6],
            "variants": [
                {
                    "id": v[0],
                    "potency": v[2],
                    "form": v[3],
                    "bottle_size": v[4],
                    "unit_type": v[5],
                    "min_stock_level": v[6],
                    "expiry_date": v[7],
                    "stock": v[8] if len(v) > 8 else 0
                }
                for v in variants
            ]
        }
        
    def search_medicines(self, query):
        return self.db.search_medicines(query)
