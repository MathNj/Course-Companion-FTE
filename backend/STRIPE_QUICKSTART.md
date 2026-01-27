# Stripe Integration Quick Start

**Time to Implement**: 4-6 hours
**Difficulty**: Medium
**Prerequisites**: Stripe account

---

## 🚀 Quick Setup (30 minutes)

### Step 1: Create Stripe Account (5 min)
1. Go to https://dashboard.stripe.com/register
2. Sign up with email
3. Complete email verification
4. You're in Test Mode by default ✅

### Step 2: Get API Keys (2 min)
1. Navigate to **Developers** → **API keys**
2. Copy these keys:
   - Publishable key: `pk_test_...`
   - Secret key: `sk_test_...`

### Step 3: Create Product & Price (5 min)

**Option A: Stripe Dashboard (Easiest)**
1. Go to **Products** → **Add product**
2. Fill in:
   - Name: `Premium Subscription`
   - Description: `Access to all 6 chapters`
   - Price: `$9.99`
   - Billing: `Monthly`
3. Click **Save**
4. Copy the **Price ID** (looks like `price_...`)

**Option B: Stripe CLI**
```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Login
stripe login

# Create product
stripe products create \
  --name="Premium Subscription" \
  --description="Access to all 6 chapters"

# Create price (replace PRODUCT_ID)
stripe prices create \
  --product=prod_... \
  --unit-amount=999 \
  --currency=usd \
  --recurring-interval=month
```

### Step 4: Install Dependencies (2 min)
```bash
cd backend
pip install stripe==8.0.0
```

### Step 5: Update Environment Variables (3 min)

Add to `backend/.env`:
```env
STRIPE_SECRET_KEY=sk_test_<YOUR_SECRET_KEY>
STRIPE_PUBLISHABLE_KEY=pk_test_<YOUR_PUBLISHABLE_KEY>
STRIPE_WEBHOOK_SECRET=whsec_<WEBHOOK_SECRET>  # Get this after deploying
STRIPE_PREMIUM_PRICE_ID=price_<YOUR_PRICE_ID>
```

### Step 6: Add Payment Router (5 min)

Edit `backend/app/main.py`, add:
```python
from app.routers import payments

app.include_router(payments.router, prefix="/api/v1", tags=["Payments"])
```

### Step 7: Test Locally (10 min)

```bash
# Start backend
cd backend
uvicorn app.main:app --reload

# In another terminal, test checkout
curl -X POST http://localhost:8000/api/v1/payments/create-checkout-session \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Expected Response**:
```json
{
  "checkout_url": "https://checkout.stripe.com/...",
  "session_id": "cs_test_..."
}
```

### Step 8: Deploy to Fly.io (5 min)

```bash
# Set secrets
flyctl secrets set STRIPE_SECRET_KEY=sk_test_... --app course-companion-fte
flyctl secrets set STRIPE_PUBLISHABLE_KEY=pk_test_... --app course-companion-fte
flyctl secrets set STRIPE_PREMIUM_PRICE_ID=price_... --app course-companion-fte

# Deploy
flyctl deploy --app course-companion-fte
```

### Step 9: Configure Webhook (5 min)

**After deployment**:

1. Go to Stripe Dashboard → **Developers** → **Webhooks**
2. Click **"Add endpoint"**
3. **Webhook URL**: `https://course-companion-fte.fly.dev/api/v1/payments/webhook`
4. **Events**: Select these:
   - `checkout.session.completed`
   - `customer.subscription.deleted`
   - `invoice.payment_failed`
5. Click **"Add endpoint"**
6. Copy **Signing secret** (`whsec_...`)
7. Add to Fly.io:
   ```bash
   flyctl secrets set STRIPE_WEBHOOK_SECRET=whsec_... --app course-companion-fte
   ```

---

## 🧪 Testing (15 minutes)

### Test 1: Create Checkout
```bash
curl -X POST https://course-companion-fte.fly.dev/api/v1/payments/create-checkout-session \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

✅ Should return checkout URL

### Test 2: Complete Payment

1. Visit the checkout_url from Test 1
2. Use test card: `4242 4242 4242 4242`
3. Expiry: Any future date (e.g., `12/34`)
4. CVC: Any 3 digits (e.g., `123`)
5. Submit payment

✅ Should see success page

### Test 3: Verify Premium Access
```bash
curl https://course-companion-fte.fly.dev/api/v1/payments/subscription-status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

✅ Should show `"is_premium": true`

### Test 4: Access Premium Content
```bash
curl https://course-companion-fte.fly.dev/api/v1/chapters/chapter-4 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

✅ Should return full chapter content (previously blocked)

---

## 📝 ChatGPT App Integration

Add to your ChatGPT App instructions:

```markdown
### Premium Upgrade Flow

When student wants to upgrade:

1. Call create_checkout_session() API
2. Provide checkout URL to student
3. Student completes payment
4. Webhook auto-upgrades account
5. Immediate premium access

**Example**:
Student: "I want premium"

You: "Great choice! Premium gives you access to chapters 4-6.
Let me create a secure checkout link..."

[Call API]

You: "Click here to upgrade: {checkout_url}

After payment ($9.99/month), you'll get immediate access!
Cancel anytime from your account."
```

---

## ✅ Success Checklist

- [ ] Stripe account created
- [ ] API keys obtained
- [ ] Product & price created
- [ ] Code implemented
- [ ] Local testing successful
- [ ] Deployed to production
- [ ] Webhook configured
- [ ] End-to-end testing complete
- [ ] ChatGPT instructions updated
- [ ] Ready for real payments

---

## 🎯 Going Live

When ready to accept real payments:

### 1. Switch to Live Mode
- Go to Stripe Dashboard
- Toggle **"Test Mode"** OFF
- Get live API keys (`sk_live_...`, `pk_live_...`)

### 2. Create Live Product
- Create product in live mode
- Copy live price ID

### 3. Update Production Secrets
```bash
flyctl secrets set STRIPE_SECRET_KEY=sk_live_... --app course-companion-fte
flyctl secrets set STRIPE_PUBLISHABLE_KEY=pk_live_... --app course-companion-fte
flyctl secrets set STRIPE_PREMIUM_PRICE_ID=price_... --app course-companion-fte
```

### 4. Update Webhook
- Create new webhook endpoint for production
- URL: Same `https://course-companion-fte.fly.dev/api/v1/payments/webhook`
- Copy live webhook secret
- Update `STRIPE_WEBHOOK_SECRET`

### 5. Deploy
```bash
flyctl deploy --app course-companion-fte
```

---

## 💰 Pricing Strategy

### Recommended: Tiered Pricing

**Free Tier** (Current):
- Chapters 1-3
- Community support
- Basic quizzes

**Premium Tier** ($9.99/month):
- All 6 chapters
- Advanced quizzes
- Progress tracking
- Streaks & achievements
- Priority support

**Alternative: Annual Plan** ($95.99/year - 20% savings):
- Save ~$24/year
- Better retention
- Upfront cash flow

---

## 📊 Revenue Projections

**Conservative** (100 users):
- Monthly: $9.99 × 100 = $999
- Yearly: $11,988
- After fees (2.9% + $0.30): $923/month

**Moderate** (1,000 users):
- Monthly: $9,990
- Yearly: $119,880
- After fees: $9,233/month

**Optimistic** (10,000 users):
- Monthly: $99,900
- Yearly: $1,198,800
- After fees: $92,334/month

---

## 🛡️ Security Notes

✅ **Secure by Design**:
- Stripe handles all card data (PCI compliant)
- Webhooks signed with secret
- HTTPS only
- No sensitive data in logs

⚠️ **Important**:
- Never commit API keys to git
- Rotate keys if compromised
- Monitor for suspicious activity
- Set up Stripe Radar (fraud protection)

---

## 🐛 Troubleshooting

**Problem**: Webhook not receiving events
- Check webhook URL is accessible
- Verify firewall allows Stripe IPs
- Test with Stripe CLI

**Problem**: User not upgraded after payment
- Check webhook processing logs
- Verify database update succeeded
- Test webhook manually

**Problem**: Test card declined
- Use correct test card: `4242 4242 4242 4242`
- Check expiry date is future
- Verify CVC is 3 digits

---

## 📚 Resources

- Stripe Docs: https://stripe.com/docs
- Stripe API Reference: https://stripe.com/docs/api
- Test Cards: https://stripe.com/docs/testing
- Webhooks Guide: https://stripe.com/docs/webhooks

---

**Ready to go live? Follow the "Going Live" section above!** 🚀
