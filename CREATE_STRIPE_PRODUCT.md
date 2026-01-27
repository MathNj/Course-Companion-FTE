# Create Stripe Product - Quick Guide

## Option 1: Stripe Dashboard (Easiest - 3 minutes)

### Step-by-Step:

1. **Go to Products Page**
   - URL: https://dashboard.stripe.com/test/products
   - Click "Products" in left sidebar

2. **Click "Add Product"** (top right button)

3. **Fill in Product Details**:
   ```
   Name: Course Companion FTE - Premium Subscription
   Description: Access to all 6 chapters including advanced prompt techniques, AI safety, and real-world applications
   ```

4. **Set Pricing**:
   - Price: `9.99`
   - Currency: `USD`
   - Billing interval: Select `Monthly` (recurring)

5. **Click "Save product"**

6. **Copy the Price ID**
   - After saving, you'll see the product details
   - Look for "Pricing" section
   - Copy the Price ID (looks like: `price_1OxXyz...`)

**That's it!** 🎉

---

## Option 2: Stripe CLI (Fastest - 30 seconds)

### Install Stripe CLI (if not installed):

**Windows** (using PowerShell):
```powershell
# Using winget
winget install Stripe.Stripe-CLI

# Or download directly
# Go to: https://stripe.com/docs/stripe-cli
```

**Or install with npm**:
```bash
npm install -g stripe-cli
```

### Login to Stripe:
```bash
stripe login
```
This will open your browser for authentication.

### Create Product:
```bash
stripe products create \
  --name="Course Companion FTE - Premium Subscription" \
  --description="Access to all 6 chapters including advanced topics"
```

**You'll get output like**:
```json
{
  "id": "prod_1OxXyzAbCD1234efGhIjKlMnO",
  "name": "Course Companion FTE - Premium Subscription",
  ...
}
```

**Copy the `id` value** (this is your Product ID)

### Create Price (Monthly):
```bash
stripe prices create \
  --product="prod_1OxXyzAbCD1234efGhIjKlMnO" \
  --unit-amount=999 \
  --currency=usd \
  --recurring-interval=month
```

**Replace `prod_...` with your actual Product ID from above**

**You'll get output like**:
```json
{
  "id": "price_1OxXyzAbCD1234efGhIjKlMnO",
  "nickname": null,
  ...
}
```

**Copy the `id` value** - **this is your Price ID!**

---

## What You'll Get:

After creating the product and price, you'll have:

**Product ID**: `prod_1OxXyzAbCD1234efGhIjKlMnO`

**Price ID**: `price_1OxXyzAbCD1234efGhIjKlMnO` ← **We need this one!**

---

## Next Step:

Once you have your Price ID, update your `.env` file:

```env
STRIPE_PREMIUM_PRICE_ID=price_1OxXyzAbCD1234efGhIjKlMnO
```

Then tell me your Price ID and we'll continue! 🚀
