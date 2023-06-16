from httpx_oauth.clients.google import GoogleOAuth2

from src.config import CLIENT_SECRET

google_oauth_client = GoogleOAuth2(
    client_secret=CLIENT_SECRET,
    client_id='1079250209238-ugnen9qhn3f7s43cl1ur0tigqdcinimg.apps.googleusercontent.com',
    scopes=["https://www.googleapis.com/auth/user.emails.read", "https://www.googleapis.com/auth/userinfo.profile"]
    #scopes=['profile'] #https://www.googleapis.com/auth/userinfo.email
)