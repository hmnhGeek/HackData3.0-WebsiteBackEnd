def valid_email(email):
    try:
        username, domain = email.split('@')
        try:
            server, category = domain.split('.')
            return 1
        except ValueError:
            return 0
    except ValueError:
        return 0
        
