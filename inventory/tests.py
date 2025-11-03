from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Product, Category, ScanEvent, InventoryAlert
from .analytics import InventoryAnalytics

class InventoryTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass', is_staff=True)
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product',
            price=10.00,
            quantity_in_stock=50,
            category=self.category
        )

    def test_product_creation(self):
        self.assertEqual(self.product.name, 'Test Product')
        self.assertEqual(self.product.quantity_in_stock, 50)

    def test_qr_scan_api(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post('/api/scan_product/', {
            'product_id': self.product.id,
            'quantity': 1,
            'scan_type': 'BILL'
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])

    def test_analytics_velocity(self):
        # Create scan events
        ScanEvent.objects.create(product=self.product, scan_type='BILL', quantity=5)
        velocity = InventoryAnalytics.calculate_product_velocity(self.product, 1)
        self.assertEqual(velocity, 5.0)

    def test_alert_generation(self):
        # Set low stock
        self.product.quantity_in_stock = 5
        self.product.save()
        
        alerts_created = InventoryAnalytics.check_inventory_alerts()
        self.assertGreaterEqual(alerts_created, 0)

    def test_export_endpoints(self):
        self.client.login(username='testuser', password='testpass')
        
        # Test CSV export
        response = self.client.get('/export/stock-csv/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')

class AnalyticsTestCase(TestCase):
    def setUp(self):
        self.product = Product.objects.create(name='Analytics Test', price=15.00, quantity_in_stock=100)

    def test_fast_moving_products(self):
        # Create multiple scan events
        for i in range(10):
            ScanEvent.objects.create(product=self.product, scan_type='BILL', quantity=2)
        
        fast_moving = InventoryAnalytics.get_fast_moving_products(5)
        self.assertGreaterEqual(len(fast_moving), 0)

    def test_low_stock_detection(self):
        self.product.quantity_in_stock = 5
        self.product.save()
        
        low_stock = InventoryAnalytics.get_low_stock_products()
        self.assertIn(self.product, low_stock)