"""
Stripe Payment Service
Handles payment processing, subscription management, and webhooks
"""

import os
import stripe
from typing import Optional, Dict, Any, List
from datetime import datetime
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
    def get_customer_subscriptions(customer_email: str) -> List[Dict[str, Any]]:
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
