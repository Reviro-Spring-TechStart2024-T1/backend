# import json

import pytest
from rest_framework.reverse import reverse


@pytest.mark.django_db
def test_get_empty_establishments_list_as_partner(
    jwt_auth_api_client
):
    # given: client with role partner
    client = jwt_auth_api_client(role='partner')
    # when:
    url = reverse('establishment-list')
    response = client.get(url)
    print(response.data)
    # then:
    assert response.status_code == 200
