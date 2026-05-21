# CEIC Credentials

To access the CEIC API, you must have a valid API key.

## Environment Variable
The API key should be stored in the `.env` file in the root directory:

```env
CEIC_API_KEY=your_api_key_here
```

## Security
- **NEVER** commit the `.env` file to version control.
- Ensure `.env` is listed in `.gitignore`.
- If the key is leaked, revoke it immediately via the CEIC platform.

## Usage in Code
The `CeicSession` class in `src/api/ceic_client.py` automatically loads this key using `python-dotenv`.
