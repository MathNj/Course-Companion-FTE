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
