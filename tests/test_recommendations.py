from labmentor.models import Service
from labmentor.recommendations import recommend_next_steps


def test_recommends_smb_when_445_open():
    services = [Service(port=445, protocol="tcp", state="open", name="microsoft-ds")]

    recommendations = recommend_next_steps(services, "10.10.10.10")

    assert recommendations
    assert "SMB" in recommendations[0]["title"]
    assert any("smbclient" in command for command in recommendations[0]["commands"])


def test_recommends_web_when_http_open():
    services = [Service(port=80, protocol="tcp", state="open", name="http")]

    recommendations = recommend_next_steps(services, "10.10.10.10")

    assert any("web" in recommendation["title"].lower() for recommendation in recommendations)
