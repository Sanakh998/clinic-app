from database.medicine_database import MedicineDatabaseManager

class InventoryService:
    def __init__(self, db_manager: MedicineDatabaseManager):
        self.db = db_manager

    def add_stock(self, variant_id, quantity, reference_type="PURCHASE", reference_id=None, notes=""):
        """Add stock to inventory."""
        if quantity <= 0:
            return False, "Quantity must be positive"
        
        success = self.db.add_stock(variant_id, quantity, reference_type, reference_id, notes)
        return success, "Stock added successfully" if success else "Failed to add stock"

    def dispense_stock(self, variant_id, quantity, reference_type="PRESCRIPTION", reference_id=None, notes=""):
        """Dispense/deduct stock from inventory."""
        if quantity <= 0:
            return False, "Quantity must be positive"
        
        success = self.db.deduct_stock(variant_id, quantity, reference_type, reference_id, notes)
        return success, "Stock dispensed successfully" if success else "Insufficient stock or error"

    def adjust_stock(self, variant_id, quantity_change, notes=""):
        """Adjust stock (can be positive or negative)."""
        if quantity_change > 0:
            return self.add_stock(variant_id, quantity_change, "ADJUSTMENT", None, notes)
        elif quantity_change < 0:
            return self.dispense_stock(variant_id, abs(quantity_change), "ADJUSTMENT", None, notes)
        else:
            return False, "No change in quantity"

    def expire_stock(self, variant_id, quantity, notes="Expired medicine"):
        """Mark stock as expired."""
        if quantity <= 0:
            return False, "Quantity must be positive"
        
        success = self.db.deduct_stock(variant_id, quantity, "DISPOSAL", None, notes)
        return success, "Stock marked as expired" if success else "Failed to expire stock"

    def check_low_stock(self):
        """Get list of medicines with low stock."""
        return self.db.get_low_stock_medicines()

    def get_stock_level(self, variant_id):
        """Get current stock level for a variant."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT quantity_available FROM inventory_stock WHERE variant_id = ?", (variant_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else 0
