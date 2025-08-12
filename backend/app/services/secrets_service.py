import os
from google.cloud import secretmanager

def load_secrets_from_gcp():
    """
    Loads secrets from Google Cloud Secret Manager and sets them as environment variables.
    This function will only run if it detects it's in a Google Cloud environment.
    """
    # Check for a specific environment variable that exists in Google Cloud Run
    project_id = os.getenv("GCP_PROJECT")
    if not project_id:
        print("Not running on GCP, skipping secret loading. App will rely on .env file.")
        return

    print(f"Running on GCP project: {project_id}. Loading secrets...")
    client = secretmanager.SecretManagerServiceClient()

    # List of all the secret names we created in the Secret Manager
    secret_names = [
        "GOOGLE_API_KEY",
        "NEWS_API_KEY",
        "WEATHER_API_KEY",
        "GROQ_API_KEY",
        "ALPHA_VANTAGE_API_KEY", # <-- ADDED THIS MISSING KEY
        "firebase-service-account"
    ]

    for name in secret_names:
        try:
            # Construct the full secret resource name
            secret_path = client.secret_version_path(project_id, name, "latest")
            # Access the secret version
            response = client.access_secret_version(request={"name": secret_path})
            # Get the secret payload
            secret_value = response.payload.data.decode("UTF-8")

            if name == "firebase-service-account":
                # For the JSON file, we need to write it to a temporary file
                # so the Firebase Admin SDK can read it.
                with open("firebase-service-account.json", "w") as f:
                    f.write(secret_value)
                print(f"✓ Successfully loaded and wrote '{name}.json'")
            else:
                # For regular API keys, set them as environment variables
                os.environ[name] = secret_value
                print(f"✓ Successfully loaded secret '{name}'")
        
        except Exception as e:
            print(f"❌ FAILED to load secret '{name}': {e}")
            # In a real app, you might want to handle this failure more gracefully
            # For now, we print a clear error.
