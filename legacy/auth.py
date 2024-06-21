#Moodle Auth2 -Google try
from requests_oauthlib import OAuth2Session

# Einstellungen für Google OAuth2
GOOGLE_CLIENT_ID = secret_key
GOOGLE_CLIENT_SECRET = secret_key
GOOGLE_AUTH_URL = secret_key
GOOGLE_TOKEN_URL = secret_key
REDIRECT_URI = "http://zoesuam.pythonanywhere.com/auth"

SCOPES = [

    "openid",
    "https://www.googleapis.com/auth/userinfo.email"



]
@app.route('/auth_url', methods=['GET'])
def auth_url():
    google_session = OAuth2Session(
        GOOGLE_CLIENT_ID,
        redirect_uri=REDIRECT_URI,
        scope=SCOPES
    )
    auth_url, _ = google_session.authorization_url(GOOGLE_AUTH_URL)
    return jsonify({"auth_url": auth_url})


@app.route('/auth', methods=['GET'])
def auth():
    code = request.args.get('code')

    if not code:
        return jsonify({"error": "Authorization code missing"}), 400

    # Create an OAuth2 session
    google_session = OAuth2Session(
        GOOGLE_CLIENT_ID,
        redirect_uri=REDIRECT_URI,
        scope=SCOPES
    )

    try:
        token = google_session.fetch_token(
            GOOGLE_TOKEN_URL,
            client_secret=GOOGLE_CLIENT_SECRET,
            code=code
        )

        # Save the token
        with open('token.json', 'w') as token_file:
            json.dump(token, token_file)

        return redirect("/")
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/')
def index():
    return "Authentication successful. Please use '/get_user_info' to retrieve user information."

@app.route('/get_user_info')
def get_user_info():
    # Lade Token aus Datei
    with open('token.json', 'r') as token_file:
        token = json.load(token_file)

    # Erstelle OAuth2Session mit gespeichertem Token
    google_session = OAuth2Session(GOOGLE_CLIENT_ID, token=token)

    # Abfrage des Profils
    user_info = google_session.get("https://openidconnect.googleapis.com/v1/userinfo").json()

    return jsonify(user_info)

@app.route('/get_course_completion', methods=['GET'])
def get_course_completion():
    # Lade Token aus Datei
    with open('token.json', 'r') as token_file:
        token = json.load(token_file)

    # Moodle-API-URL und Parameter
    moodle_url = "https://your.moodle.site/webservice/rest/server.php"
    params = {
        "wstoken": token.get("access_token"),  # Verwende den OAuth2-Token
        "wsfunction": "core_completion_get_course_completion_status",
        "courseid": 12345,  # Hier die richtige Kurs-ID einsetzen
        "moodlewsrestformat": "json"
    }

    # Anfrage senden
    response = requests.get(moodle_url, params=params)
    return jsonify(response.json())


