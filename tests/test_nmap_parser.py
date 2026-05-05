from labmentor.nmap_parser import parse_nmap_text


def test_parse_common_nmap_services():
    text = """
PORT    STATE SERVICE     VERSION
22/tcp  open  ssh         OpenSSH 8.9p1 Ubuntu
80/tcp  open  http        Apache httpd 2.4.52
445/tcp open  microsoft-ds Samba smbd 4.15.13
"""
    services = parse_nmap_text(text)

    assert len(services) == 3
    assert services[0].port == 22
    assert services[0].name == "ssh"
    assert services[1].port == 80
    assert services[1].name == "http"
    assert services[2].port == 445
    assert services[2].name == "microsoft-ds"
