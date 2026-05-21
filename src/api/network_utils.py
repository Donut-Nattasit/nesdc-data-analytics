import time
import requests
from typing import Any, Dict, Optional, Callable

def resilient_request(
    method: str,
    url: str,
    max_retries: int = 5,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    session: Optional[requests.Session] = None,
    **kwargs: Any
) -> requests.Response:
    """
    Execute a resilient HTTP request with exponential backoff for transient failures (5xx)
    and rate limit warnings (429).
    
    Args:
        method (str): HTTP method (GET, POST, etc.)
        url (str): Target URL
        max_retries (int): Maximum number of retry attempts
        initial_delay (float): Initial wait time in seconds
        backoff_factor (float): Multiplier applied to delay after each retry
        session (Session, optional): A persistent requests Session
        **kwargs: Additional parameters passed to requests.request or session.request
        
    Returns:
        Response: The final HTTP response if successful or after retries are exhausted.
    """
    delay = initial_delay
    caller: Callable = session.request if session else requests.request
    
    for attempt in range(1, max_retries + 1):
        try:
            response = caller(method, url, **kwargs)
            
            # Check for success
            if response.status_code == 200:
                return response
                
            # If rate limited (429), respect Retry-After header if present
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                wait_time = float(retry_after) if retry_after and retry_after.isdigit() else delay
                print(f"[Warning] Rate limited (429) on {url}. Waiting {wait_time:.1f}s (Attempt {attempt}/{max_retries})...")
                time.sleep(wait_time)
                delay *= backoff_factor
                continue
                
            # If server error, retry
            if 500 <= response.status_code < 600:
                print(f"[Warning] Server error ({response.status_code}) on {url}. Retrying in {delay:.1f}s (Attempt {attempt}/{max_retries})...")
                time.sleep(delay)
                delay *= backoff_factor
                continue
                
            # For other status codes (e.g. 400, 401, 403, 404), return immediately to let client handle it
            return response
            
        except requests.exceptions.RequestException as e:
            if attempt == max_retries:
                print(f"[Error] Request failed after {max_retries} attempts: {e}")
                raise e
            print(f"[Warning] Network error on {url}: {e}. Retrying in {delay:.1f}s (Attempt {attempt}/{max_retries})...")
            time.sleep(delay)
            delay *= backoff_factor
            
    # Fallback response execution for final try if loop completes
    return caller(method, url, **kwargs)
