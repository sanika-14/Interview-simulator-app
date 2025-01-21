import firebase_admin
from firebase_admin import credentials, auth

# Initialize Firebase

cred = credentials.Certificate("path to your firebase admin sdk file.json")
firebase_admin.initialize_app(cred)

def signup_user(email, password):
    """Create a new user with email and password."""
    try:
        user = auth.create_user(email=email, password=password)
        return {"success": True, "uid": user.uid}
    except Exception as e:
        return {"success": False, "error": str(e)}

def verify_token(id_token):
    """Verify Firebase ID Token."""
    try:
        decoded_token = auth.verify_id_token(id_token)
        return {"success": True, "uid": decoded_token["uid"]}
    except Exception as e:
        return {"success": False, "error": str(e)}
