import services.db_services as svc

active_account = None


def reload_account():
    global active_account
    if not active_account:
        return

    active_account = svc.check_email_exist(active_account.email)
    pass
