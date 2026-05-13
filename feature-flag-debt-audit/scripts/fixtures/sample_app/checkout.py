FLAGS = {
    "checkout_v2": True,
    "kill_checkout_payments": False,
}


def checkout_enabled(flag_client):
    if flag_client.enabled("kill_checkout_payments"):
        return False
    return flag_client.enabled("checkout_v2")
