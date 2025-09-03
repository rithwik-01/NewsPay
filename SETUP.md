# NewsPay Stripe Integration Setup Guide

This guide will help you set up the Stripe integration for NewsPay.

## Prerequisites

- Python 3.7+
- A Stripe account (free at [stripe.com](https://stripe.com))

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Get Stripe API Keys

1. **Sign up for Stripe** (if you haven't already)
   - Go to [stripe.com](https://stripe.com) and create an account
   - Complete the basic account setup

2. **Get your API keys**
   - Go to [Dashboard > API Keys](https://dashboard.stripe.com/apikeys)
   - You'll see two keys:
     - **Publishable key** (starts with `pk_test_` or `pk_live_`)
     - **Secret key** (starts with `sk_test_` or `sk_live_`)

3. **Use test keys for development**
   - Always start with test keys (starting with `pk_test_` and `sk_test_`)
   - Test keys let you make test payments without real money
   - Switch to live keys only when deploying to production

## Step 3: Configure Environment Variables

1. **Copy the environment template**
   ```bash
   cp env.template .env
   ```

2. **Edit the .env file**
   ```bash
   # Replace with your actual Stripe keys
   STRIPE_SECRET_KEY=sk_test_your_actual_secret_key_here
   STRIPE_PUBLISHABLE_KEY=pk_test_your_actual_publishable_key_here
   ```

3. **Never commit your .env file**
   - The `.env` file is already in `.gitignore`
   - Keep your secret keys private and secure

## Step 4: Test the Integration

1. **Run the test script**
   ```bash
   python test_stripe.py
   ```

2. **Expected output**
   ```
   🧪 Testing Stripe Integration...
   ✅ Found Stripe keys:
      Secret Key: sk_test_1234...
      Publishable Key: pk_test_1234...
   ✅ Stripe connection successful!
      Account ID: acct_1234567890
      Account Type: standard
   
   🧪 Testing Checkout Session creation...
   ✅ Test checkout session created successfully!
      Session ID: cs_test_1234567890
      Checkout URL: https://checkout.stripe.com/pay/cs_test_...
   ✅ Test session expired for cleanup
   
   🎉 All tests passed! Stripe integration is working correctly.
   ```

## Step 5: Start the Server

```bash
cd server
python main.py
```

The server will start on `http://localhost:8000`

## Step 6: Test the Payment Flow

1. **In another terminal, test the client**
   ```bash
   cd client
   python main.py --pay
   ```

2. **Expected behavior**
   - Client creates a Stripe Checkout Session
   - Browser opens to Stripe's hosted checkout page
   - Complete payment using test card: `4242 4242 4242 4242`
   - You'll be redirected to a success page with your Bearer token

## Test Cards

Use these test card numbers for development:

| Card Number | Result | Use Case |
|-------------|--------|----------|
| `4242 4242 4242 4242` | ✅ Success | Normal payments |
| `4000 0000 0000 0002` | ❌ Decline | Test declined payments |
| `4000 0000 0000 9995` | ❌ Insufficient funds | Test insufficient funds |

**For all test cards:**
- **Expiry**: Any future date (e.g., 12/25)
- **CVC**: Any 3 digits (e.g., 123)
- **ZIP**: Any valid ZIP code (e.g., 12345)

## Troubleshooting

### "STRIPE_SECRET_KEY not found"
- Make sure you created a `.env` file
- Check that the key names match exactly
- Verify the file is in the project root directory

### "Stripe authentication failed"
- Check your secret key is correct
- Ensure you're using the right key type (test vs live)
- Verify your Stripe account is active

### "Stripe API connection failed"
- Check your internet connection
- Verify Stripe's services are available
- Check if your firewall is blocking the connection

### Payment not working in browser
- Make sure you're using test card numbers
- Check the browser console for errors
- Verify the success/cancel URLs are accessible

## Production Deployment

When deploying to production:

1. **Switch to live keys**
   - Get live keys from your Stripe Dashboard
   - Update your `.env` file with live keys
   - Test thoroughly with small amounts first

2. **Configure webhooks** (recommended)
   - Go to [Dashboard > Webhooks](https://dashboard.stripe.com/webhooks)
   - Add your production webhook endpoint
   - Select `checkout.session.completed` event
   - Copy the webhook secret to your `.env` file

3. **Security considerations**
   - Use HTTPS in production
   - Keep your secret keys secure
   - Monitor your Stripe Dashboard for suspicious activity
   - Set up proper error handling and logging

## Support

- **Stripe Documentation**: [docs.stripe.com](https://docs.stripe.com)
- **Stripe Support**: [support.stripe.com](https://support.stripe.com)
- **Project Issues**: Check the project repository for known issues
