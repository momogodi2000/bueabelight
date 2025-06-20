from django.apps import AppConfig


class BackendConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend'
    verbose_name = 'BueaDelights Backend'
    
    def ready(self):
        """
        Perform initialization when the app is ready.
        This method is called when Django starts.
        """
        import backend.signals  # Import signals if you have any
        
        # Initialize business settings if not exists
        self.create_business_settings()
    
    def create_business_settings(self):
        """Create default business settings if they don't exist"""
        try:
            from backend.models import BusinessSettings
            
            if not BusinessSettings.objects.exists():
                BusinessSettings.objects.create(
                    business_name='BueaDelights',
                    business_description='Local Flavors at Your Fingertips',
                    phone='+237699808260',
                    email='info@bueadelights.com',
                    address='Buea, Southwest Region, Cameroon',
                    operating_hours='Monday - Sunday: 8:00 AM - 10:00 PM',
                    delivery_fee=1500,
                    delivery_areas='Buea, Limbe, Tiko, Douala',
                    is_accepting_orders=True
                )
        except Exception:
            # Ignore errors during startup (e.g., during migrations)
            pass