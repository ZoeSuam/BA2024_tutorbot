try:
    from requests_oauthlib import OAuth2Session
    print("Import successful")
except ImportError as e:
    print(f"Import failed: {str(e)}")