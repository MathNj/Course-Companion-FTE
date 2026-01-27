# Stripe Payment Integration Guide

**Phase**: Post Phase-1 Enhancement
**Feature**: Automated Premium Subscriptions
**Payment Provider**: Stripe
**Status**: Ready to Implement

---

## Overview

This guide will help you add Stripe payment integration to your Course Companion FTE backend, enabling users to:
1. Upgrade from free to premium tier
2. Manage subscriptions
3. Handle payment webhooks
4. Receive automatic access to premium content

---

## Architecture

### Current State (Manual)
```
User → ChatGPT → "I want premium" → Manual DB update → Access granted
```

### Target State (Automated)
```
User → ChatGPT → Stripe Checkout → Payment → Webhook → Auto upgrade → Access granted
```

### Security Considerations
- ✅ Stripe handles all payment data (PCI compliance)
- ✅ Webhooks verify payment with signatures
- ✅ No credit card data stored on your servers
- ✅ Idempotent operations (safe retry)

---

## Step 1: Stripe Account Setup

### 1.1 Create Stripe Account

1. Go to https://dashboard.stripe.com/register
2. Sign up (use your email)
3. Verify your email
4. Complete account setup

### 1.2 Get API Keys

1. Go to **Developers** → **API keys**
2. Copy **Publishable key** (starts with `pk_test_` or `pk_live_`)
3. Copy **Secret key** (starts with `sk_test_` or `sk_live_`)
4. Keep these secure - never commit to git!

### 1.3 Create Products & Prices

**Option A: Stripe Dashboard**
1. Go to **Products** → **Add product**
2. Create "Premium Subscription"
   - Name: "Course Companion FTE - Premium"
   - Description: "Access to all 6 chapters including advanced topics"
   - Price: $9.99/month
3. Copy the **Price ID** (starts with `price_`)

**Option B: Stripe CLI** (Recommended for automation)
```bash
# Create product
stripe products create \
  --name="Course Companion FTE - Premium" \
  --description="Access to all 6 chapters including advanced topics"

# Create monthly price
stripe prices create \
  --product=prod_<PRODUCT_ID> \
  --unit-amount=999 \
  --currency=usd \
  --recurring-interval=month

# Create yearly price (optional, 20% discount)
stripe prices create \
  --product=prod_<PRODUCT_ID> \
  --unit-amount=9599 \
  --currency=usd \
  --recurring-interval=year
```

---

## Step 2: Backend Implementation

### 2.1 Install Stripe Library

```bash
cd backend
pip install stripe
```

Add to `requirements.txt`:
```
stripe==8.0.0
```

### 2.2 Update Environment Variables

Add to `backend/.env`:
```env
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_<YOUR_SECRET_KEY>
STRIPE_PUBLISHABLE_KEY=pk_test_<YOUR_PUBLISHABLE_KEY>
STRIPE_WEBHOOK_SECRET=whsec_<YOUR_WEBHOOK_SECRET>
STRIPE_PREMIUM_PRICE_ID=price_<YOUR_PRICE_ID>
```

Add to `backend/.env.production.example`:
```env
# Stripe Configuration (Production)
STRIPE_SECRET_KEY=sk_live_<YOUR_LIVE_SECRET_KEY>
STRIPE_PUBLISHABLE_KEY=pk_live_<YOUR_LIVE_PUBLISHABLE_KEY>
STRIPE_WEBHOOK_SECRET=whsec_<YOUR_LIVE_WEBHOOK_SECRET>
STRIPE_PREMIUM_PRICE_ID=price_<YOUR_LIVE_PRICE_ID>
```

### 2.3 Create Stripe Service

Create `backend/app/services/stripe_service.py`:

```python
"""
Stripe Payment Service
Handles payment processing, subscription management, and webhooks
"""

import os
import stripe
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Premium price ID from environment
PREMIUM_PRICE_ID = os.getenv("STRIPE_PREMIUM_PRICE_ID")


class StripeService:
    """Service for Stripe payment operations"""

    @staticmethod
    def create_checkout_session(
        user_email: str,
        user_id: str,
        success_url: str,
        cancel_url: str
    ) -> Dict[str, Any]:
        """
        Create a Stripe Checkout session for premium subscription

        Args:
            user_email: User's email address
            user_id: User's database ID
            success_url: URL to redirect after successful payment
            cancel_url: URL to redirect if payment cancelled

        Returns:
            Dict with checkout session data including URL
        """
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price": PREMIUM_PRICE_ID,
                        "quantity": 1,
                    }
                ],
                mode="subscription",
                success_url=success_url,
                cancel_url=cancel_url,
                customer_email=user_email,
                metadata={
                    "user_id": user_id,
                    "user_email": user_email,
                },
                subscription_data={
                    "metadata": {
                        "user_id": user_id,
                        "user_email": user_email,
                    }
                }
            )

            logger.info(f"Created checkout session for user {user_id}: {session.id}")

            return {
                "checkout_url": session.url,
                "session_id": session.id,
                "expires_at": datetime.fromtimestamp(session.expires_at)
            }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating checkout session: {str(e)}")
            raise


    @staticmethod
    def get_customer_subscriptions(customer_email: str) -> list:
        """
        Get all subscriptions for a customer email

        Args:
            customer_email: Customer's email address

        Returns:
            List of subscription objects
        """
        try:
            # Find customers by email
            customers = stripe.Customer.list(email=customer_email).auto_paging_iter()

            subscriptions = []
            for customer in customers:
                subs = stripe.Subscription.list(
                    customer=customer.id,
                    status="all"
                ).auto_paging_iter()

                for sub in subs:
                    subscriptions.append({
                        "subscription_id": sub.id,
                        "status": sub.status,
                        "current_period_end": datetime.fromtimestamp(sub.current_period_end),
                        "cancel_at_period_end": sub.cancel_at_period_end,
                        "price_id": sub["items"]["data"][0]["price"]["id"]
                    })

            return subscriptions

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error fetching subscriptions: {str(e)}")
            return []


    @staticmethod
    def cancel_subscription(subscription_id: str) -> Dict[str, Any]:
        """
        Cancel a subscription at the end of the current period

        Args:
            subscription_id: Stripe subscription ID

        Returns:
            Updated subscription object
        """
        try:
            subscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )

            logger.info(f"Cancelled subscription {subscription_id} at period end")

            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "cancelled": True
            }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error cancelling subscription: {str(e)}")
            raise


    @staticmethod
    def construct_webhook_event(payload: bytes, sig_header: str) -> stripe.Event:
        """
        Construct and verify a webhook event

        Args:
            payload: Request payload as bytes
            sig_header: Stripe-Signature header value

        Returns:
            Verified Stripe Event object

        Raises:
            ValueError: If signature verification fails
        """
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
            return event

        except ValueError as e:
            logger.error(f"Webhook signature verification failed: {str(e)}")
            raise
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid webhook signature: {str(e)}")
            raise


    @staticmethod
    def handle_checkout_session_completed(session: stripe.checkout.Session) -> Dict[str, Any]:
        """
        Handle checkout.session.completed event

        Args:
            session: Stripe checkout session object

        Returns:
            User data to update in database
        """
        customer_email = session.customer_details.email
        user_id = session.metadata.get("user_id")
        subscription_id = session.subscription

        return {
            "user_id": user_id,
            "email": customer_email,
            "subscription_id": subscription_id,
            "subscription_tier": "premium"
        }


    @staticmethod
    def handle_subscription_deleted(subscription: stripe.Subscription) -> Dict[str, Any]:
        """
        Handle customer.subscription.deleted event

        Args:
            subscription: Stripe subscription object

        Returns:
            User data to update in database
        """
        # Extract user_id from subscription metadata
        user_id = subscription.metadata.get("user_id")

        return {
            "user_id": user_id,
            "subscription_tier": "free",
            "subscription_expires_at": datetime.fromtimestamp(
                subscription.current_period_end
            )
        }
```

### 2.4 Create Payment Router

Create `backend/app/routers/payments.py`:

```python
"""
Payment Routes
Handle Stripe checkout sessions and payment management
"""

from fastapi import APIRouter, HTTPException, status, Request, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import logging

from app.services.stripe_service import StripeService
from app.database import get_db
from app.models.user import User
from app.dependencies import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["Payments"])


class CheckoutRequest(BaseModel):
    """Request model for creating checkout session"""
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None


class SubscriptionResponse(BaseModel):
    """Response model for subscription status"""
    is_premium: bool
    subscription_status: Optional[str]
    subscription_id: Optional[str]
    current_period_end: Optional[str]


@router.post("/create-checkout-session")
async def create_checkout_session(
    request: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a Stripe Checkout session for premium subscription

    Returns a checkout URL that the user should be redirected to
    """
    # Default URLs (can be overridden)
    success_url = request.success_url or "https://chat.openai.com/?payment=success"
    cancel_url = request.cancel_url or "https://chat.openai.com/?payment=cancelled"

    try:
        # Create checkout session
        session_data = StripeService.create_checkout_session(
            user_email=current_user.email,
            user_id=str(current_user.id),
            success_url=success_url,
            cancel_url=cancel_url
        )

        return {
            "checkout_url": session_data["checkout_url"],
            "session_id": session_data["session_id"]
        }

    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create checkout session"
        )


@router.get("/subscription-status", response_model=SubscriptionResponse)
async def get_subscription_status(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's subscription status
    """
    try:
        # Get subscriptions from Stripe
        subscriptions = StripeService.get_customer_subscriptions(current_user.email)

        if not subscriptions:
            return {
                "is_premium": False,
                "subscription_status": None,
                "subscription_id": None,
                "current_period_end": None
            }

        # Get active subscription
        active_sub = next(
            (s for s in subscriptions if s["status"] in ["active", "trialing"]),
            None
        )

        if active_sub:
            return {
                "is_premium": True,
                "subscription_status": active_sub["status"],
                "subscription_id": active_sub["subscription_id"],
                "current_period_end": active_sub["current_period_end"].isoformat()
            }

        # User has subscription but not active (e.g., past_due, cancelled)
        return {
            "is_premium": False,
            "subscription_status": subscriptions[0]["status"],
            "subscription_id": subscriptions[0]["subscription_id"],
            "current_period_end": subscriptions[0]["current_period_end"].isoformat()
        }

    except Exception as e:
        logger.error(f"Error fetching subscription status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch subscription status"
        )


@router.post("/cancel-subscription")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Cancel user's premium subscription at period end
    """
    try:
        # Get subscriptions from Stripe
        subscriptions = StripeService.get_customer_subscriptions(current_user.email)

        if not subscriptions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No subscription found"
            )

        # Get active subscription
        active_sub = next(
            (s for s in subscriptions if s["status"] == "active"),
            None
        )

        if not active_sub:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active subscription to cancel"
            )

        # Cancel subscription in Stripe
        result = StripeService.cancel_subscription(active_sub["subscription_id"])

        # Update user in database
        await db.execute(
            update(User)
            .where(User.id == current_user.id)
            .values(subscription_tier="free")
        )
        await db.commit()

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel subscription"
        )


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle Stripe webhook events
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not sig_header:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No Stripe signature header"
        )

    try:
        # Verify webhook signature
        event = StripeService.construct_webhook_event(payload, sig_header)

        # Handle different event types
        if event["type"] == "checkout.session.completed":
            await handle_checkout_completed(event["data"]["object"], db)

        elif event["type"] == "customer.subscription.deleted":
            await handle_subscription_deleted(event["data"]["object"], db)

        elif event["type"] == "invoice.payment_failed":
            await handle_payment_failed(event["data"]["object"], db)

        else:
            logger.info(f"Unhandled webhook event type: {event['type']}")

        return {"status": "success"}

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook signature"
        )
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook processing failed"
        )


async def handle_checkout_completed(session: stripe.checkout.Session, db: AsyncSession):
    """Handle successful checkout - upgrade user to premium"""
    try:
        # Extract user data
        user_data = StripeService.handle_checkout_session_completed(session)

        # Update user in database
        await db.execute(
            update(User)
            .where(User.id == user_data["user_id"])
            .values(
                subscription_tier="premium",
                is_premium=True,
                subscription_expires_at=None  # Active subscription
            )
        )
        await db.commit()

        logger.info(f"Upgraded user {user_data['user_id']} to premium")

    except Exception as e:
        logger.error(f"Error handling checkout completed: {str(e)}")
        raise


async def handle_subscription_deleted(subscription: stripe.Subscription, db: AsyncSession):
    """Handle subscription deletion - downgrade user to free"""
    try:
        # Extract user data
        user_data = StripeService.handle_subscription_deleted(subscription)

        # Update user in database
        await db.execute(
            update(User)
            .where(User.id == user_data["user_id"])
            .values(
                subscription_tier="free",
                is_premium=False,
                subscription_expires_at=user_data.get("subscription_expires_at")
            )
        )
        await db.commit()

        logger.info(f"Downgraded user {user_data['user_id']} to free tier")

    except Exception as e:
        logger.error(f"Error handling subscription deleted: {str(e)}")
        raise


async def handle_payment_failed(invoice: stripe.Invoice, db: AsyncSession):
    """Handle payment failure - log and potentially notify user"""
    try:
        customer_id = invoice.customer
        subscription_id = invoice.subscription

        logger.warning(
            f"Payment failed for subscription {subscription_id}, "
            f"customer {customer_id}"
        )

        # Optionally: Send email notification to user
        # Optionally: Update user status to "past_due"

    except Exception as e:
        logger.error(f"Error handling payment failed: {str(e)}")
```

### 2.5 Update Main Router

Edit `backend/app/main.py`:

```python
# Add payments router
from app.routers import payments

app.include_router(payments.router, prefix="/api/v1", tags=["Payments"])
```

---

## Step 3: Update ChatGPT Instructions

Add to `chatgpt-app/instructions.md` after "Freemium Awareness" section:

```markdown
### Premium Upgrade Flow (NEW)

**When student wants to upgrade**:
1. Explain premium benefits (chapters 4-6, advanced topics)
2. Call create_checkout_session() to get payment link
3. Provide the checkout URL to student
4. Student completes payment on Stripe
5. Webhook automatically upgrades their account
6. Student gets immediate access to premium content

**Example conversation**:
```
Student: "I want to upgrade to premium"

You: "Great choice! Premium gives you access to:
- Chapter 4: Advanced Prompting Techniques
- Chapter 5: AI Safety and Ethics
- Chapter 6: Real-World AI Applications

Let me create a secure checkout link for you..."

[Call POST /payments/create-checkout-session()]

You: "I've created a secure payment link. Click here to upgrade:
{checkout_url}

This is a one-time secure payment page powered by Stripe.
After payment, you'll get immediate access to all premium chapters!

The subscription is $9.99/month and you can cancel anytime."
```

**After payment confirmation**:
```
Student: "I just paid!"

You: "Welcome to Premium! 🎉

You now have access to all 6 chapters:
✓ Chapters 1-3 (Free - already completed)
✓ Chapter 4: Advanced Prompting Techniques (NEW!)
✓ Chapter 5: AI Safety and Ethics (NEW!)
✓ Chapter 6: Real-World AI Applications (NEW!)

Would you like to start with Chapter 4, or explore what interests you most?"
```
```

---

## Step 4: Deploy to Production

### 4.1 Update Fly.io Environment Variables

```bash
# Set Stripe secrets (production)
flyctl secrets set STRIPE_SECRET_KEY=sk_live_... --app course-companion-fte
flyctl secrets set STRIPE_PUBLISHABLE_KEY=pk_live_... --app course-companion-fte
flyctl secrets set STRIPE_WEBHOOK_SECRET=whsec_... --app course-companion-fte
flyctl secrets set STRIPE_PREMIUM_PRICE_ID=price_... --app course-companion-fte
```

### 4.2 Redeploy Application

```bash
flyctl deploy --app course-companion-fte
```

### 4.3 Configure Stripe Webhook

**Important**: After deployment, configure webhook in Stripe Dashboard:

1. Go to **Developers** → **Webhooks**
2. Click **"Add endpoint"**
3. **Webhook URL**: `https://course-companion-fte.fly.dev/api/v1/payments/webhook`
4. **Events to listen for**:
   - `checkout.session.completed`
   - `customer.subscription.deleted`
   - `invoice.payment_failed`
5. Click **"Add endpoint"**
6. Copy the **Webhook Secret** (`whsec_...`)
7. Add to Fly.io secrets: `STRIPE_WEBHOOK_SECRET`

---

## Step 5: Testing

### 5.1 Test Mode (Test Cards)

Use Stripe test cards for testing:

**Successful payment**:
```
Card number: 4242 4242 4242 4242
Expiry: Any future date
CVC: Any 3 digits
ZIP: Any 5 digits
```

**Payment declined**:
```
Card number: 4000 0000 0000 0002
```

**Requires authentication** (3D Secure):
```
Card number: 4000 0025 0000 3155
```

### 5.2 Test Checkout Flow

```bash
# 1. Create checkout session
curl -X POST https://course-companion-fte.fly.dev/api/v1/payments/create-checkout-session \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'

# Response: {"checkout_url": "https://checkout.stripe.com/...", "session_id": "..."}

# 2. Visit checkout_url and complete payment with test card

# 3. Check subscription status
curl https://course-companion-fte.fly.dev/api/v1/payments/subscription-status \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Response: {"is_premium": true, ...}

# 4. Verify premium content access
curl https://course-companion-fte.fly.dev/api/v1/chapters/chapter-4 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Response: Full chapter content (previously blocked)
```

### 5.3 Test Webhook Locally

Use Stripe CLI for local testing:

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Login
stripe login

# Forward webhooks to local server
stripe listen --forward-to localhost:8000/api/v1/payments/webhook

# Trigger test events
stripe trigger checkout.session.completed
stripe trigger customer.subscription.deleted
```

---

## Step 6: Update OpenAPI Spec

Add payment endpoints to `backend/openapi.yaml` or let FastAPI auto-generate:

```yaml
/api/v1/payments/create-checkout-session:
  post:
    tags:
      - Payments
    summary: Create Stripe checkout session
    security:
      - BearerAuth: []
    requestBody:
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/CheckoutRequest'
    responses:
      '200':
        description: Checkout session created
        content:
          application/json:
            schema:
              type: object
              properties:
                checkout_url:
                  type: string
                session_id:
                  type: string

/api/v1/payments/subscription-status:
  get:
    tags:
      - Payments
    summary: Get subscription status
    security:
      - BearerAuth: []
    responses:
      '200':
        description: Subscription status
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SubscriptionResponse'

/api/v1/payments/webhook:
  post:
    tags:
      - Payments
    summary: Stripe webhook endpoint
    responses:
      '200':
        description: Webhook processed
```

---

## Security Best Practices

### ✅ Implemented
- Webhook signature verification
- No credit card data stored
- HTTPS only
- Idempotent operations
- Secure API keys in environment variables

### 📝 Recommended
- Rate limiting on payment endpoints
- Monitor webhook failures
- Alert on payment failures
- Regular security audits
- PCI compliance maintained by Stripe

---

## Costs & Pricing

### Stripe Fees
- **Card transactions**: 2.9% + $0.30 per transaction
- **International cards**: Additional 1%
- **Subscription pricing**: $9.99/month recommended

### Revenue Calculation
```
Monthly revenue = $9.99 × number of premium users
Stripe fees = $9.99 × 0.029 + $0.30 = $0.59 per user
Net revenue = $9.99 - $0.59 = $9.40 per user

Example:
- 100 premium users = $940/month net revenue
- 1000 premium users = $9,400/month net revenue
```

---

## Troubleshooting

### Webhook Not Receiving Events
- Check firewall rules allow Stripe IPs
- Verify webhook URL is publicly accessible
- Test with Stripe CLI: `stripe trigger checkout.session.completed`
- Check Fly.io logs: `flyctl logs --app course-companion-fte`

### Payment Successful But User Not Upgraded
- Check webhook processing logs
- Verify database update succeeded
- Check for race conditions
- Test webhook manually with Stripe CLI

### Checkout Session Fails
- Verify Stripe API keys are correct
- Check product/price IDs exist
- Ensure success/cancel URLs are valid
- Test in Stripe Dashboard first

---

## Summary

After implementing this guide, your Course Companion FTE will have:

✅ Automated payment processing via Stripe
✅ Secure checkout flow
✅ Automatic premium tier upgrade
✅ Subscription management (cancel, status check)
✅ Webhook handling for payment events
✅ Production-ready payment integration

**Estimated Implementation Time**: 4-6 hours
**Complexity**: Medium
**Dependencies**: Stripe account, payment methods enabled

---

## Next Steps

1. Create Stripe account
2. Create product and prices
3. Implement backend code
4. Deploy to production
5. Configure webhook
6. Test with test cards
7. Go live with real payments
8. Monitor and optimize

Good luck! 🚀
