import random

from requests import request, Response

from pylooke.encripta.encripta_crypto import EncriptaCrypto
from pylooke.utils import body, device

class Looke:
    """
    Looke class for interacting with the Looke API to retrieve media details, handle entitlements, and acquire licenses.
    """
    def __init__(self, authentication_ticket: str = "looke@looke:v7c8ad@#$"):
        """
        Initializes the Looke class with authentication ticket and required URLs.

        :param authentication_ticket: Authentication ticket required for API access.
        """
        self.authentication_ticket = authentication_ticket
        self.encripta_crypto = EncriptaCrypto()
        self.urls = {
            "service": "https://looke-service.delightfulwave-5cfdd77b.brazilsouth.azurecontainerapps.io",
            "service_media": "https://looke-service-media.delightfulwave-5cfdd77b.brazilsouth.azurecontainerapps.io",
            "license": "https://license.ottvs.com.br/Widevine/API/LicenseProxy"
        }

    def find_media(self, media_id: int, media_type: int = 31, **kwargs) -> dict:
        """
        Sends a POST request to the 'find_media' to retrieve media details by media ID.

        :param media_id: The ID of the media.
        :param media_type: The type of media to be used in the request.
        :param kwargs: Additional optional parameters for entities, groups, or options to include in the request.

        :return: Media details result.
        """
        response = self.send_request(
            method="POST",
            url="{host}/{path}".format(
                host=self.urls["service_media"],
                path="v1/android/findmedia"
            ),
            json={
                "AuthenticationTicket": self.authentication_ticket,
                "Criteria": {
                    "MediaId": media_id,
                    "MediaType": media_type
                },
                "Entities": body.get_entities(kwargs.get("entities")),
                "Groups": body.get_groups(kwargs.get("groups")),
                "Options": body.get_options(kwargs.get("options"))
            }
        )

        result = response.json()["FindMediaResult"].get("Movies", [])

        if result:
            return result[0]

        raise Looke.Exceptions.FindMediaError(response.json())

    def login_essentials(self, username: str, password: str) -> dict:
        """
        Authenticates the user and registers the machine ID for login access.

        This function first authenticates the user using the provided username and password.
        If the authentication is successful, it proceeds to register a machine ID (using the
        JoinDomain API) to authorize the device for subsequent access.

        :param username: The username of the user to authenticate.
        :param password: The password associated with the username.

        :return: Login essentials, including the user details and the registered machine ID.
        """
        response_login_essentials = self.send_request(
            method="POST",
            url="{host}/{path}".format(
                host=self.urls["service"],
                path="v1/android/LoginEssentials"
            ),
            json={
                "AuthenticationTicket": self.authentication_ticket,
                "Password": password,
                "Username": username
            }
        )

        login_essentials_result = response_login_essentials.json()["LoginEssentialsResult"]

        if login_essentials_result.get("Result") != 0:
            raise Looke.Exceptions.LoginEssentialsError(login_essentials_result["Message"])

        machine_id = "".join(random.choices("0123456789abcdef", k=16))

        response_join_domain = self.send_request(
            method="POST",
            url="{host}/{path}".format(
                host=self.urls["service"],
                path="v1/android/JoinDomain"
            ),
            json={
                "Alias": "Android Device",
                "AuthenticationTicket": self.authentication_ticket,
                "MachineId": machine_id,
                "UserId": login_essentials_result["User"]["UserId"]
            }
        )

        join_domain_result = response_join_domain.json()["JoinDomainResult"]

        if join_domain_result.get("Message") != "Success":
            raise Looke.Exceptions.JoinDomainError(join_domain_result["Message"])

        login_essentials_result["MachineId"] = machine_id

        return login_essentials_result

    def entitle(self, media_id: int, encrypted_user_id: bytes, transaction_source: int = 3) -> dict:
        """
        Sends a POST request to the 'Entitle' to authorize access to the specified media for a user.

        :param media_id: The ID of the media to be entitled.
        :param encrypted_user_id: The encrypted user ID as bytes.
        :param transaction_source: The source of the transaction.

        :return: Entitlement result.
        """
        response = self.send_request(
            method="POST",
            url="{host}/{path}".format(
                host=self.urls["service_media"],
                path="v1/android/Entitle"
            ),
            json={
                "AuthenticationTicket": self.authentication_ticket,
                "EncUserID": encrypted_user_id.hex().upper(),
                "MediaID": media_id,
                "TransactionSource": transaction_source
            }
        )

        return response.json()["EntitleResult"]

    def get_concurrent(self, media_id: int, user_id: int) -> dict:
        """
        Sends a POST request to the 'GetConcurrent' to check concurrent access
        for the specified media and user.

        :param media_id: The ID of the media to check.
        :param user_id: The ID of the user to verify concurrent access.

        :return: Get Concurrent result.
        """
        response = self.send_request(
            method="POST",
            url="{host}/{path}".format(
                host=self.urls["service_media"],
                path="v1/android/GetConcurrent"
            ),
            json={
                "AuthenticationTicket": self.authentication_ticket,
                "MediaId": media_id,
                "UserId": user_id
            }
        )

        return response.json()["GetConcurrentResult"]

    def get_license(self, challenge: bytes, media_id: int, user_id: int, machine_id: str) -> bytes:
        """
        Get License.

        :param challenge: EME license request.
        :param media_id: The ID of the media.
        :param user_id: The ID of the user.
        :param machine_id: The ID of the machine.

        :return: EME license response.
        """
        encrypted_user_id = self.encripta_crypto.encrypt(
            data=str(user_id)
        )

        encrypted_device_id = self.encripta_crypto.encrypt(
            data=device.identifier_with_time(
                machine_id=machine_id
            )
        )

        entitle_result = self.entitle(
            media_id=media_id,
            encrypted_user_id=encrypted_user_id
        )

        if entitle_result["Result"] != 0:
            raise Looke.Exceptions.EntitleError(entitle_result)

        get_concurrent_result = self.get_concurrent(
            media_id=media_id,
            user_id=user_id
        )

        if get_concurrent_result["Result"] != 0:
            raise Looke.Exceptions.GetConcurrentError(get_concurrent_result)

        response = self.send_request(
            method="POST",
            url=self.urls["license"],
            params={
                "userId": encrypted_user_id.hex().upper(),
                "deviceId": encrypted_device_id.hex().upper()
            },
            headers={
                "Content-Type": "application/octet-stream",
                "User-Agent": "Android Device"
            },
            data=challenge
        )

        if response.status_code == 200:
            return response.content

        raise Looke.Exceptions.LicenseError(response.text)

    @staticmethod
    def send_request(**kwargs) -> Response:
        """
        Sends an HTTP request with the provided parameters.

        :param kwargs: Keyword arguments containing method, URL, headers, and data for the request.

        :return: Response object from the HTTP request.
        """
        headers = {
            "Accept": "*/*",
            "User-Agent": "okhttp/4.10.0",
            **kwargs.get("headers", {})
        }

        response = request(
            method=kwargs["method"],
            url=kwargs["url"],
            headers=headers,
            params=kwargs.get("params", {}),
            json=kwargs.get("json", None),
            data=kwargs.get("data", None)
        )

        return response

    class Exceptions:
        class LicenseError(Exception):
            """License request issues."""

        class FindMediaError(Exception):
            """Find media issues."""

        class EntitleError(Exception):
            """Entitlement check issues."""

        class GetConcurrentError(Exception):
            """Get concurrent check issues."""

        class LoginEssentialsError(Exception):
            """Login essentials issues."""

        class JoinDomainError(Exception):
            """Machine registration issues."""