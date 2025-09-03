import requests
import argparse
import json
import sys
import webbrowser
import time
import urllib.request # Added for urllib.request

class NoUserAgentAdapter(requests.adapters.HTTPAdapter):
    """Custom adapter that removes User-Agent header"""
    def add_headers(self, request, **kwargs):
        # Remove User-Agent if it exists
        if 'User-Agent' in request.headers:
            del request.headers['User-Agent']

def pretty_print_json(data):
    """Prints JSON data with indentation."""
    try:
        print(json.dumps(data, indent=2))
    except TypeError: # Handle non-serializable data if necessary
        print(data)

def main():
    parser = argparse.ArgumentParser(description="CLI client for the NewsPay News Demo server.")
    parser.add_argument(
        '--server-url',
        default="http://localhost:8000",
        help="URL of the NewsPay server."
    )

    # --- Action Group (Mutually Exclusive) ---
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument(
        '--pay',
        action='store_true',
        help="Initiate the payment flow."
    )
    action_group.add_argument(
        '--with-auth',
        metavar='TOKEN',
        help="Make an authenticated GET request using the provided Bearer token."
    )

    # --- Payment Specific Arguments (only relevant if --pay is used) ---
    parser.add_argument(
        '--category',
        default=None,
        # Ideally, fetch categories dynamically, but hardcode for now based on server
        choices=["politics", "international", "economy", "technology", "sports", "entertainment"],
        help="Purchase access for a specific category (use with --pay). If omitted, purchases access for all categories."
    )

    args = parser.parse_args()

    # --- Argument Validation ---
    if args.category and not args.pay:
        parser.error("--category can only be used with --pay")

    # --- Execution Logic ---
    if args.pay:
        # --- Payment Flow ---
        # Determine offer_id based on category presence
        offer_id = "one_category" if args.category else "all_categories"
        category_info = f" for category '{args.category}'" if args.category else " for all categories"
        print(f"Attempting payment flow ({offer_id}){category_info}...")

        # 1. Initial GET request to get 402 and payment details
        try:
            print(f"Making initial GET request to {args.server_url}...")
            
            # Method 1: Try with requests and custom adapter
            try:
                session = requests.Session()
                adapter = NoUserAgentAdapter()
                session.mount('http://', adapter)
                session.mount('https://', adapter)
                print(f"Using requests with custom adapter")
                print(f"Session headers: {dict(session.headers)}")
                
                response = session.get(args.server_url)
                print(f"Initial GET response status: {response.status_code}")
                print(f"Response headers: {dict(response.headers)}")
                
            except Exception as e:
                print(f"Requests method failed: {e}")
                print("Falling back to urllib method...")
                
                # Method 2: Fallback to urllib (guaranteed no User-Agent)
                req = urllib.request.Request(args.server_url)
                req.add_header('User-Agent', '')  # Explicitly set empty
                response = urllib.request.urlopen(req)
                print(f"urllib response status: {response.status}")
                
                # Convert urllib response to requests-like object for compatibility
                class MockResponse:
                    def __init__(self, urllib_response):
                        self.status_code = urllib_response.status
                        self.text = urllib_response.read().decode('utf-8')
                        self.headers = dict(urllib_response.getheaders())
                
                response = MockResponse(response)
                print(f"Converted response status: {response.status_code}")
            
            if response.status_code == 402:
                try:
                    l402_data = response.json()
                    print("Received 402 Payment Required. Offer details:")
                    pretty_print_json(l402_data)

                    payment_url = l402_data.get("payment_request_url")
                    payment_token = l402_data.get("payment_context_token")

                    if not payment_url or not payment_token:
                        print("Error: Missing 'payment_request_url' or 'payment_context_token' in 402 response.")
                        sys.exit(1)

                    # 2. Construct payment payload
                    payment_payload = {
                        "payment_context_token": payment_token,
                        "offer_id": offer_id
                    }
                    # Add category to payload only if it exists (implies one_category offer)
                    if args.category:
                        payment_payload["category"] = args.category

                    # 3. Make POST request to payment URL
                    print(f"\nMaking POST payment request to {payment_url}...")
                    print("Payload:")
                    pretty_print_json(payment_payload)

                    payment_response = requests.post(payment_url, json=payment_payload)
                    print(f"\nPayment POST response status: {payment_response.status_code}")

                    try:
                        payment_result = payment_response.json()
                        print("Payment response body:")
                        pretty_print_json(payment_result)
                        
                        if payment_response.ok:
                            print("\n✅ Stripe Checkout Session created successfully!")
                            checkout_url = payment_result.get("checkout_url")
                            session_id = payment_result.get("session_id")
                            
                            if checkout_url:
                                print(f"\n🔗 Opening Stripe Checkout in your browser...")
                                print(f"Checkout URL: {checkout_url}")
                                
                                # Open the checkout URL in the default browser
                                try:
                                    webbrowser.open(checkout_url)
                                    print("\n📱 Stripe Checkout opened in your browser.")
                                    print("Please complete the payment in the browser window.")
                                    print("\n⏳ Waiting for payment completion...")
                                    print("After payment, you'll be redirected to a success page with your Bearer token.")
                                    print("\n💡 Tip: You can also manually visit the checkout URL above.")
                                    
                                    # Wait a bit for user to see the message
                                    time.sleep(2)
                                    
                                    print("\n🔄 To check if payment was successful, you can:")
                                    print("1. Complete the payment in the browser")
                                    print("2. Copy the Bearer token from the success page")
                                    print("3. Use it with: python main.py --with-auth <TOKEN>")
                                    
                                except Exception as e:
                                    print(f"⚠️  Could not open browser automatically: {e}")
                                    print(f"Please manually visit: {checkout_url}")
                            else:
                                print("❌ Error: No checkout URL received from server")
                                
                        else:
                            print("\n❌ Payment failed.")

                    except json.JSONDecodeError:
                        print("Error: Could not decode JSON from payment response.")
                        print("Raw response text:")
                        print(payment_response.text)
                        sys.exit(1)

                except json.JSONDecodeError:
                    print("Error: Could not decode JSON from 402 response.")
                    print("Raw response text:")
                    print(response.text)
                    sys.exit(1)
            else:
                print(f"Error: Expected status code 402 for payment initiation, but got {response.status_code}.")
                try:
                    pretty_print_json(response.json())
                except json.JSONDecodeError:
                    print(response.text)
                sys.exit(1)

        except requests.exceptions.RequestException as e:
            print(f"Error during payment request: {e}")
            sys.exit(1)

    elif args.with_auth:
        # --- Authenticated GET Flow ---
        print(f"Making authenticated GET request to {args.server_url}...")
        auth_token = args.with_auth
        headers = {
            "Authorization": f"Bearer {auth_token}"
        }
        try:
            response = requests.get(args.server_url, headers=headers)
            print(f"Response Status Code: {response.status_code}")

            print("\nResponse Body:")
            try:
                pretty_print_json(response.json())
            except json.JSONDecodeError:
                print("Response is not valid JSON. Raw text:")
                print(response.text)

        except requests.exceptions.RequestException as e:
            print(f"Error making authenticated GET request: {e}")
            sys.exit(1)

    else:
        # --- Default Flow (Unauthenticated GET request) ---
        print(f"Making default GET request to {args.server_url}...")
        try:
            response = requests.get(args.server_url)
            print(f"Response Status Code: {response.status_code}")

            print("\nResponse Body:")
            try:
                # Attempt to parse and print JSON nicely
                pretty_print_json(response.json())
            except json.JSONDecodeError:
                # If it's not JSON (e.g., HTML for browser), print raw text
                print("Response is not valid JSON. Raw text:")
                print(response.text)

        except requests.exceptions.RequestException as e:
            print(f"Error making default GET request: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
