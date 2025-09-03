#!/usr/bin/env python3
"""
Simple test script to verify Stripe integration
Run this to test if your Stripe configuration is working
"""

import os
import stripe
from dotenv import load_dotenv

def test_stripe_connection():
    """Test basic Stripe connectivity and configuration"""
    print("🧪 Testing Stripe Integration...")
    
    # Load environment variables
    load_dotenv()
    
    # Check if keys are loaded
    secret_key = os.getenv("STRIPE_SECRET_KEY")
    publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY")
    
    if not secret_key:
        print("❌ STRIPE_SECRET_KEY not found in environment variables")
        print("   Please create a .env file with your Stripe keys")
        return False
        
    if not publishable_key:
        print("❌ STRIPE_PUBLISHABLE_KEY not found in environment variables")
        print("   Please create a .env file with your Stripe keys")
        return False
    
    print(f"✅ Found Stripe keys:")
    print(f"   Secret Key: {secret_key[:12]}...")
    print(f"   Publishable Key: {publishable_key[:12]}...")
    
    # Test Stripe API connection
    try:
        stripe.api_key = secret_key
        
        # Try to retrieve account information
        account = stripe.Account.retrieve()
        print(f"✅ Stripe connection successful!")
        print(f"   Account ID: {account.id}")
        print(f"   Account Type: {account.type}")
        
        # Test creating a test checkout session
        print("\n🧪 Testing Checkout Session creation...")
        test_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Test Product',
                        'description': 'Test product for integration testing',
                    },
                    'unit_amount': 100,  # $1.00
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='https://example.com/success',
            cancel_url='https://example.com/cancel',
        )
        
        print(f"✅ Test checkout session created successfully!")
        print(f"   Session ID: {test_session.id}")
        print(f"   Checkout URL: {test_session.url}")
        
        # Clean up test session
        stripe.checkout.Session.expire(test_session.id)
        print("✅ Test session expired for cleanup")
        
        return True
        
    except stripe.error.AuthenticationError:
        print("❌ Stripe authentication failed")
        print("   Please check your STRIPE_SECRET_KEY")
        return False
        
    except stripe.error.APIConnectionError:
        print("❌ Stripe API connection failed")
        print("   Please check your internet connection")
        return False
        
    except stripe.error.StripeError as e:
        print(f"❌ Stripe error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 50)
    print("NewsPay Stripe Integration Test")
    print("=" * 50)
    
    success = test_stripe_connection()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Stripe integration is working correctly.")
        print("\nNext steps:")
        print("1. Start the server: cd server && python main.py")
        print("2. Test the client: cd client && python main.py --pay")
    else:
        print("💥 Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("1. Make sure you have a .env file with your Stripe keys")
        print("2. Verify your Stripe keys are correct")
        print("3. Check your internet connection")
        print("4. Ensure you're using test keys for development")
    print("=" * 50)

if __name__ == "__main__":
    main()
