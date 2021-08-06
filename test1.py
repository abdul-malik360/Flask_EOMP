import unittest
from app import app


class Testing(unittest.TestCase):
    def test_registration(self):
        test = app.test_client(self)
        response = test.get('/api/register/')
        status = response.status_code
        self.assertEqual(status, 405)

    def test_show_users(self):
        test = app.test_client(self)
        response = test.get('/api/show-users/')
        status = response.status_code
        self.assertEqual(status, 401)

    def test_view_user(self):
        test = app.test_client(self)
        response = test.get('/api/show-users/')
        status = response.status_code
        self.assertEqual(status, 401)

    def test_add_products(self):
        test = app.test_client(self)
        response = test.get('/api/add-product/')
        status = response.status_code
        self.assertEqual(status, 405)

    def test_show_products(self):
        test = app.test_client(self)
        response = test.get('/api/show-products/')
        status = response.status_code
        self.assertEqual(status, 200)

    def test_view_product(self):
        test = app.test_client(self)
        response = test.get('/api/view-product/<int:prod_list>')
        status = response.status_code
        self.assertEqual(status, 404)

    def test_edit_product(self):
        test = app.test_client(self)
        response = test.get('/edit-product/<int:prod_list>')
        status = response.status_code
        self.assertEqual(status, 404)

    def test_delete_product(self):
        test = app.test_client(self)
        response = test.get('/api/delete-product/<int:prod_list>')
        status = response.status_code
        self.assertEqual(status, 404)


if __name__ == '__main__':
    unittest.main()
