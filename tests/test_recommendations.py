from labmentor.models import Service
from labmentor.recommendations import recommend_next_steps


def recommendation_titles(recommendations):
    return [recommendation["title"] for recommendation in recommendations]


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


def test_recommends_snmp_when_161_open():
    services = [Service(port=161, protocol="udp", state="open", name="snmp")]

    recommendations = recommend_next_steps(services, "10.10.10.10")

    assert "Enumerate SNMP information" in recommendation_titles(recommendations)
    assert any(
        "snmpwalk" in command
        for recommendation in recommendations
        for command in recommendation["commands"]
    )


def test_recommends_nfs_when_2049_open():
    services = [Service(port=2049, protocol="tcp", state="open", name="nfs")]

    recommendations = recommend_next_steps(services, "10.10.10.10")

    assert "Enumerate NFS exports" in recommendation_titles(recommendations)
    assert any(
        "showmount" in command
        for recommendation in recommendations
        for command in recommendation["commands"]
    )
