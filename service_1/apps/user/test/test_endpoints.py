from rest_framework.test import APITestCase
from django.core.cache import cache
import json
from datetime import datetime
from apps.user.models import Customer
import os

class TestUser(APITestCase):
    def setUp(self):
        self.model = Customer
        self.user = {
            "email": "test_user@gmail.com",
            "password": "Test123$",
            "confirm_password": "Test123$" 
        }
        self.fake_user = {
            "incorrect_num_fields": {
                "incorrect_field1": "incorrect_value1",
                "incorrect_field2": "incorrect_value2",
            },
            "incorrect_fields": {
                "incorrect_field1": "incorrect_value1",
                "incorrect_field2": "incorrect_value2",
                "incorrect_field3": "incorrect_value3",
            },
            "invalid_email": {
                "email": "@invalid_emailgmail.com",
                "password": self.user.get("password"),
                "confirm_password": self.user.get("confirm_password")
            },
            "invalid_password": {
                "email": self.user.get("email"),
                "password": "fake_password",
                "confirm_password": "fake_password"
            },
            "password_do_not_match": {
                "email": self.user.get("email"),
                "password": self.user.get("password"),
                "confirm_password": "fake_password"
            },
            "incorrect_field_value": {
                "email": 12548,
                "password": self.user.get("password"),
                "confirm_password": self.user.get("confirm_password")
            }

        }
        self.urls = {
            "register": "/api/user/register",
            "verify_email": "/api/user/verify-email",
            "login": "/api/user/log-in",
            "email": "/api/user/email",
            "password_reset": "/api/user/password-reset",
            "profile": "/api/user/profile",
            "logout": "/api/user/log-out",
            "invite_link": "/api/user/invite-link",
            "google_auth": "/api/user/google-auth/"
        }
        return super().setUp()
    
    def test_register(self):
        # test with no payload
        response = self.client.post(self.urls.get("register"), data=None, format="json")
        self.assertEqual(response.status_code, 422)

        # test with incorrect number of fields
        response = self.client.post(self.urls.get("register"), data=self.fake_user.get("incorrect_num_fields"), format="json")
        self.assertEqual(response.status_code, 422)

        # test with incorrect fields
        response = self.client.post(self.urls.get("register"), data=self.fake_user.get("incorrect_fields"))
        self.assertEqual(response.status_code, 422)

        # test with invalid email
        response = self.client.post(self.urls.get("register"), data=self.fake_user.get("invalid"))
        self.assertEqual(response.status_code, 422)

        # password do not match
        response = self.client.post(self.urls.get("register"), data=self.fake_user.get("password_do_not_match"))
        self.assertEqual(response.status_code, 422)

        # test with incorrect field value
        response = self.client.post(self.urls.get("register"), data=self.fake_user.get("incorrect_field_value"))
        self.assertEqual(response.status_code, 422)

        # test with valid payload
        initial_cnt = Customer.objects.count()
        response = self.client.post(self.urls.get("register"), data=self.user, format="json")
        self.assertEqual(response.status_code, 201)
        final_cnt = Customer.objects.count()
        self.assertEqual(final_cnt, initial_cnt + 1)
        self.assertEqual(response.data.get("email"), self.user.get("email"))
        self.assertEqual(response.data.get("invite_code"), None)
        self.assertEqual(response.data.get("is_email_verified"), False)
        self.assertEqual(response.data.get("has_min_purchase"), False)
        self.assertEqual(response.data.get("type"), "customer")
        self.assertTrue(response.data.get("created_at"))
        self.assertTrue(response.data.get("updated_at"))
        self.assertTrue(response.data.get("id"))
        self.assertTrue(response.data.get("password") is None)


    def test_verify_email(self):
        # test with no payload
        response = self.client.post(self.urls.get("verify_email"), data=None, format="json")
        self.assertEqual(response.status_code, 422)

        # test with incorrect number of fields
        response = self.client.post(self.urls.get("verify_email"), data=self.fake_user.get("incorrect_num_fields"), format="json")
        self.assertEqual(response.status_code, 422)

        # test with incorrect fields
        response = self.client.post(self.urls.get("verify_email"), data=self.fake_user.get("incorrect_fields"), format="json")
        self.assertEqual(response.status_code, 422)

        # test with invalid token
        response = self.client.post(self.urls.get("verify_email"), data={"token": "invalid_token"}, format="json")
        self.assertEqual(response.status_code, 400)


    
    def test_login(self):

        # test with no payload
        response = self.client.post(self.urls.get("login"), data=None, format="json")
        self.assertEqual(response.status_code, 422)

        # test with incorrect number of fields
        response = self.client.post(self.urls.get("login"), data=self.fake_user.get("incorrect_num_fields"), format="json")
        self.assertEqual(response.status_code, 422)

        # test with incorrect fields
        response = self.client.post(self.urls.get("login"), data=self.fake_user.get("incorrect_fields"), format="json")
        self.assertEqual(response.status_code, 422)

        # test with non-existing email
        response = self.client.post(self.urls.get("login"), data={"email": "fake_user@gmail.com", "password": "Fake_password123$"}, format="json")
        self.assertEqual(response.status_code, 404)

        # test with  incorrect password
        response = self.client.post(self.urls.get("register"), data=self.user, format="json")
        self.assertEqual(response.status_code, 201)
        user = Customer.objects.get(email=self.user.get("email"))
        if not user.is_email_verified:
            user.verify_email()
        response = self.client.post(self.urls.get("login"), data={"email": self.user.get("email"), "password": "fake_Password123$"}, format="json")
        self.assertEqual(response.status_code, 401)

        # test with valid credential
        response = self.client.post(self.urls.get("login"), data={"email": self.user.get("email"), "password": self.user.get("password")}, format="json")
        self.assertEqual(response.status_code, 200)

        # check refresh and access token present in cookies
        self.assertTrue(response.cookies.get("access_token"))
        self.assertTrue(response.cookies.get("refresh_token"))
    
    def test_email(self):
        # test with no payload
        response = self.client.post(self.urls.get("email"), data=None, format="json")
        self.assertEqual(response.status_code, 400)

        # test with incorrect number of fields
        response = self.client.post(self.urls.get("email"), data=self.fake_user.get("incorrect_num_fields"), format="json")
        self.assertEqual(response.status_code, 400)

        # test with incorrect fields
        response = self.client.post(self.urls.get("email"), data=self.fake_user.get("incorrect_fields"), format="json")
        self.assertEqual(response.status_code, 400)

        # test with non-existing email
        response = self.client.post(self.urls.get("email"), data={"email": "fake_email@gmail.com"}, format="json")
        self.assertEqual(response.status_code, 404)

        # test with existing email
        response = self.client.post(self.urls.get("email"), data={"email": self.user.get("email")}, format="json")
        self.assertTrue(response.status_code, 200)

    def test_password_reset(self):
        # test with no payload
        response = self.client.post(self.urls.get("password_reset"), data=None, format="json")
        self.assertEqual(response.status_code, 422)

        # test with incorrect number of fields
        response = self.client.post(self.urls.get("password_reset"), data=self.fake_user.get("incorrect_num_fields"), format="json")
        self.assertEqual(response.status_code, 422)

        # test with incorrect fields
        response = self.client.post(self.urls.get("password_reset"), data=self.fake_user.get("incorrect_fields"), format="json")
        self.assertEqual(response.status_code, 422)

    def test_user_profile(self):

        # test without authentication
        response = self.client.get(self.urls.get("profile"))
        self.assertEqual(response.status_code, 403)

        # test with authentication
        response = self.client.post(self.urls.get('register'), data=self.user, format="json")
        user = Customer.objects.get(email=self.user.get("email"))
        user.verify_email()
        response = self.client.post(self.urls.get("login"), data={"email": self.user.get('email'), "password": self.user.get("password")}, format="json")
        response = self.client.get(self.urls.get("profile"), headers={
            "Cookie-Header": response.cookies
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get("email"), self.user.get("email"))
        self.assertTrue(response.data.get("id"))
    
    def test_logout(self):

        # test without authentication
        response = self.client.get(self.urls.get("logout"))
        self.assertEqual(response.status_code, 403)

        # test invalid access and refresh token
        response = self.client.get(self.urls.get("logout"), headers={
            "Cookie-Header": "access_token=fake_access_toke;refresh_token=fake_refresh_token"
        })
        self.assertEqual(response.status_code, 403)

        # test with authentication
        self.client.post(self.urls.get("register"), data=self.user, format="json")
        Customer.objects.get(email=self.user.get("email")).verify_email()
        response = self.client.post(self.urls.get("login"), data={"email": self.user.get("email"), "password": self.user.get("password")}, format="json")
        response = self.client.get(self.urls.get("logout"), headers={
            "Cookie-Header": response.cookies
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.cookies.get("access_token"), None)
        self.assertEqual(response.cookies.get("refresh_token"), None)
    
    def test_invite_link(self):
        # test without authentication
        response = self.client.get(self.urls.get("invite_link"))
        self.assertTrue(response.status_code, 403)

        # test with authentication
        self.client.post(self.urls.get("register"), data=self.user, format="json")
        Customer.objects.get(email=self.user.get("email")).verify_email()
        response = self.client.post(self.urls.get("login"), data={"email": self.user.get("email"), "password": self.user.get('password')}, format="json")
        response = self.client.get(self.urls.get("invite_link"), headers={
            "Cookie-Header": response.cookies
        })
        self.assertEqual(response.status_code, 200)
        invite_link = response.data.get("invite_link")
        response = self.client.get(self.urls.get("invite_link"), headers={
            "Cookie-Header": response.cookies
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get("invite_link"), invite_link)

    def test_google_auth(self):

        # test incorrect number of query paramter
        query_paramas = "fake_field1=fake_value1&fake_field2=fake_value2&fake_field3=fake_value3"
        response = self.client.get(self.urls.get("google_auth"), QUERY_STRING=query_paramas)
        self.assertEqual(response.status_code, 400)
        
        # test with incorrect parameter
        query_paramas = "fake_field1=fake_value1&fake_field2=fake_value2"
        response = self.client.get(self.urls.get("google_auth"), QUERY_STRING=query_paramas)
        self.assertEqual(response.status_code, 400)


        # test with state field absent in query parameter
        query_paramas = "code=fake_code&error=fake_error"
        response = self.client.get(self.urls.get("google_auth"), QUERY_STRING=query_paramas)
        self.assertEqual(response.status_code, 400)

        # test with invalid code value in query paramter
        query_paramas = "code=invalid_code&state=fake_state"
        response = self.client.get(self.urls.get("google_auth"), QUERY_STRING=query_paramas)
        self.assertEqual(response.status_code, 302)


    def tearDown(self):
        return super().tearDown()
