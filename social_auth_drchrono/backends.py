import os
from social.backends.oauth import BaseOAuth2
import requests

class drchronoOAuth2(BaseOAuth2):
    """
    drchrono OAuth authentication backend
    """

    name = 'drchrono'
    AUTHORIZATION_URL = 'https://drchrono.com/o/authorize/'
    ACCESS_TOKEN_URL = 'https://drchrono.com/o/token/'
    ACCESS_TOKEN_METHOD = 'POST'
    REDIRECT_STATE = False
    USER_DATA_URL = 'https://drchrono.com/api/users/current'
    EXTRA_DATA = [
        ('refresh_token', 'refresh_token'),
        ('expires_in', 'expires_in')
    ]
    # TODO: setup proper token refreshing

    def get_user_details(self, response):
        """
        Return user details from drchrono account
        """

        access_token = response.get('access_token')
        headers = {
            'Authorization': 'Bearer ' + access_token,
        }

        # Getting logged-in doctor details
        doctors_url = 'https://drchrono.com/api/doctors'
        while doctors_url:
            data = requests.get(doctors_url, headers=headers).json()

            for doc in data['results']:
                if doc['id'] == response.get('doctor'):
                    return {'username': response.get('username'), 'first_name': doc['first_name'], 'last_name': doc['last_name'], 'email': doc['email'], }

            doctors_url = data['next'] # A JSON null on the last page


        return {'username': response.get('username'),}

    def user_data(self, access_token, *args, **kwargs):
        """
        Load user data from the service
        """
        return self.get_json(
            self.USER_DATA_URL,
            headers=self.get_auth_header(access_token)
        )

    def get_auth_header(self, access_token):
        return {'Authorization': 'Bearer {0}'.format(access_token)}
