from src.bot_data import BOTClient
import os

def main():
    # The client automatically loads the token from .env if BOT_API_TOKEN is set
    try:
        client = BOTClient()
        
        print("Fetching category list...")
        categories = client.get_category_list()
        print(categories.head())

        # Example: Fetching series list for a specific category (e.g., 'EC_EI_020')
        # Replace with a valid category code if needed
        # series_list = client.get_series_list("EC_EI_020")
        # print(series_list.head())

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
