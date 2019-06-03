import pytest
import subresource_integrity as integrity


@pytest.fixture
def sri():
    return 'sha256-CXS0O7OjESVro+DicbpxpvZPeBy2jTJ/CuQJnScABWs='


@pytest.fixture
def sri_urlsafe():
    return 'c2hhMjU2LUNYUzBPN09qRVNWcm8rRGljYnB4cHZaUGVCeTJqVEovQ3VRSm5TY0FCV3M9'


@pytest.fixture
def sri_obj(sri):
    return integrity.parse(sri)[0]
