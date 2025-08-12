print("Attempting to load the embedding model...")
try:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("\n--- SUCESS! ---")
    print("The embedding model was downloaded and loaded correctly.")
    print("This means the problem is not with the model. Please let me know you see this message.")
except Exception as e:
    print("\n--- FAILURE! ---")
    print("We found the error. The embedding model failed to download or load.")
    print("Please send me this full error message:")
    print(e)