from core.util.ssh import get_pubkey_fingerprint


def test_ssh_fingerprint_happy():
    pub_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDW4TP4Y7AsTgNn14Ax+tc6KLqUcj0RUOdFX3k/Z3xf0HQXfJiqI+06XuFYGaETRRgflepGCO/xP6jtCwNPUEjO9bRpu3mChDBJOFHGUkKHPzHnUvFuuA8OCk1QISwMn1X1bn1JFQr5eI8zGf3XaJ3Xr80qXUCGgcV2N3WVBFikVL7HWMg5dpiFDnlUUZvPSGiBsu6rNEK43LJuypUvMsKkmyAlcYkcmqGdyqanzE2lvfjKi0xNJ0Q3jhfhheinZ1+ox0BTeANw+/kszvkvNo4QPDJYXL/gZw3ElfyYQ7YVnZfxpgw34fL/VE1WNEzGQrU3pKQ3mu5wGowXfpnfayJ7ywxOHcoWw8oGJEu+Y3FhP1eG1MZocc6STCnfZne4wTmbvqJ8W7810d5faSfEpgv6CwXEuoU3+iQZK2N6oLFE8LgpLa4mmSzxAD1EVMzDCK+BNp+fV+zfO6hBQYl3JyHwkJRHxxhFYA+I5H4Q5AfQC303b417HImv7bSaCIH6c88= robko@robko-workstation"
    fingerprint = get_pubkey_fingerprint(pub_key)
    expected = "SHA256:hNZw1eNpCeV1GH1syS5i8uqYeO/2a1vWBfJisZvT4oY"
    assert expected == fingerprint


def test_ssh_fingerprint_invalid():
    pub_key = "invalid data :)"
    fingerprint = get_pubkey_fingerprint(pub_key)
    expected = None
    assert expected == fingerprint


if __name__ == '__main__':
    test_ssh_fingerprint_happy()
    test_ssh_fingerprint_invalid()
