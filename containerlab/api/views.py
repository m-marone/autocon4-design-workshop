"""API views for containerlab."""

import base64
import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from nautobot.dcim.models import Device


from nautobot.apps.api import NautobotModelViewSet

from containerlab import filters, models
from containerlab.api import serializers

local_settings = settings.PLUGINS_CONFIG.get("nautobot_containerlab", {})
# Fetch Guacamole settings from Django settings
guac_url = local_settings.get("guac_url")
guac_user = local_settings.get("guac_user")
guac_pass = local_settings.get("guac_pass")
guac_data_source = local_settings.get("guac_data_source")
guac_frontend_url = local_settings.get("guac_frontend_url")


def guacamole_token():
    # Step 1: Authenticate with Guacamole
    return requests.post(
        f"{guac_url}/guacamole/api/tokens",
        data={"username": guac_user, "password": guac_pass},
    )


def guacamole_clientid(connectionid, type, db):
    # Combine the parameters with a NULL character between them
    combined_string = f"{connectionid}\u0000{type}\u0000{db}"

    # Encode the combined string in Base64
    encoded_string = base64.b64encode(combined_string.encode("utf-8")).decode("utf-8")

    return encoded_string


class TopologyViewSet(NautobotModelViewSet):  # pylint: disable=too-many-ancestors
    """Topology viewset."""

    queryset = models.Topology.objects.all()
    serializer_class = serializers.TopologySerializer
    filterset_class = filters.TopologyFilterSet

    # Option for modifying the default HTTP methods:
    # http_method_names = ["get", "post", "put", "patch", "delete", "head", "options", "trace"]


class CLKindViewSet(NautobotModelViewSet):
    """CLKind viewset."""

    queryset = models.CLKind.objects.all()
    serializer_class = serializers.CLKindSerializer
    filterset_class = filters.CLKindFilterSet


class CreateGuacamoleDevice(APIView):
    permission_classes = [AllowAny]

    def post(self, request, pk, *args, **kwargs):
        try:
            # Retrieve the device object using the pk
            device = Device.objects.get(pk=pk)
        except Device.DoesNotExist:
            return Response(
                {"error": "Device not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Determine the name and hostname
        device_name = device.name
        primary_ip = device.primary_ip4 or device.primary_ip6
        hostname = primary_ip.address.split("/")[0] if primary_ip else device_name

        headers = {"Content-Type": "application/json"}

        # Step 1: Authenticate with Guacamole
        auth_response = guacamole_token()
        if auth_response.status_code != 200:
            return Response(
                {"error": "Failed to authenticate with Guacamole"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        token = auth_response.json().get("authToken")

        # Step 2: Check if the device already exists in Guacamole
        list_response = requests.get(
            f"{guac_url}/guacamole/api/session/data/{guac_data_source}/connections?token={token}",
            headers=headers,
        )
        if list_response.status_code != 200:
            return Response(
                {"error": "Failed to retrieve connections from Guacamole"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        connections = list_response.json()
        existing_device = None

        for conn_info in connections.values():
            if conn_info["name"] == device_name:
                existing_device = conn_info
                break

        # Prepare the payload
        payload = {
            "parentIdentifier": "ROOT",
            "name": device_name,
            "protocol": "ssh",
            "parameters": {"port": "22", "hostname": hostname},
            "attributes": {},
        }

        if existing_device:
            # Step 2: Get the details of the existing device
            detail_response = requests.get(
                f"{guac_url}/guacamole/api/session/data/{guac_data_source}/connections/{existing_device['identifier']}?token={token}",
                headers=headers,
            )
            if detail_response.status_code != 200:
                return Response(
                    {"error": "Failed to retrieve connection details from Guacamole"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            existing_details = detail_response.json()

            # Get the parameters of the existing connection
            parameter_response = requests.get(
                f"{guac_url}/guacamole/api/session/data/{guac_data_source}/connections/{existing_device['identifier']}/parameters?token={token}",
                headers=headers,
            )
            if parameter_response.status_code != 200:
                return Response(
                    {
                        "error": "Failed to retrieve connection parameters from Guacamole"
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            existing_parameters = parameter_response.json()

            # Compare the existing device's parameters with the new payload
            if (
                existing_details["protocol"] != payload["protocol"]
                or existing_parameters != payload["parameters"]
            ):
                # Update the device
                update_response = requests.put(
                    f"{guac_url}/guacamole/api/session/data/{guac_data_source}/connections/{existing_device['identifier']}?token={token}",
                    json=payload,
                    headers=headers,
                )

                if update_response.status_code != 204:
                    return Response(
                        {"error": "Failed to update the device in Guacamole"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )
                return Response(
                    {"message": "Device updated successfully in Guacamole"},
                    status=status.HTTP_202_ACCEPTED,
                )
            else:
                return Response(
                    {"message": "No changes needed"}, status=status.HTTP_200_OK
                )
        else:
            # Step 3: Create the device
            create_response = requests.post(
                f"{guac_url}/guacamole/api/session/data/{guac_data_source}/connections?token={token}",
                json=payload,
                headers=headers,
            )
            if create_response.status_code != 200:
                return Response(
                    {"error": "Failed to create the device in Guacamole"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            return Response(
                {"message": "Device created successfully in Guacamole"},
                status=status.HTTP_202_ACCEPTED,
            )


class GetGuacamoleClient(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk, *args, **kwargs):
        try:
            # Retrieve the device object using the pk
            device = Device.objects.get(pk=pk)
        except Device.DoesNotExist:
            return Response(
                {"error": "Device not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Determine the name and hostname
        device_name = device.name

        headers = {"Content-Type": "application/json"}

        # Step 1: Authenticate with Guacamole
        auth_response = guacamole_token()
        if auth_response.status_code != 200:
            return Response(
                {"error": "Failed to authenticate with Guacamole"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        token = auth_response.json().get("authToken")

        # Step 2: Check if the device already exists in Guacamole
        list_response = requests.get(
            f"{guac_url}/guacamole/api/session/data/{guac_data_source}/connections?token={token}",
            headers=headers,
        )
        if list_response.status_code != 200:
            return Response(
                {"error": "Failed to retrieve connections from Guacamole"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        connections = list_response.json()
        existing_device = None

        for conn_info in connections.values():
            if conn_info["name"] == device_name:
                existing_device = conn_info
                break
        clientid = guacamole_clientid(
            existing_device["identifier"], "c", guac_data_source
        )
        return Response(
            {
                "clientid": clientid,
                "url": f"{guac_frontend_url}/guacamole/#/client/{clientid}?token={token}",
            },
            status=status.HTTP_200_OK,
        )
