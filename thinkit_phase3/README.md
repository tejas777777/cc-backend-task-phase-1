# cc-backend-task-phase2
Models (phase1app/models.py): Profile (role), Wallet (now OneToOneField(User)), Item.seller, Order/OrderItem, Review - changes were made, including linking the one matching dev wallet to its real user and backfilling Profile(role=buyer) for the two existing accounts.

Permissions (phase1app/permissions.py): IsBuyer, IsSeller, IsItemOwner, applied explicitly per-view/per-method — verified via smoke test that a buyer gets 403 creating an item, a seller gets 403 touching the cart, and a seller gets 403 editing another seller's item.

Endpoints added: POST /api/auth/signup/, GET /api/auth/me/, GET/POST /api/wallet/+/topup/, extended GET /api/items/ (search/category/price-range/in-stock/ordering, all combinable), GET/POST /api/items/<id>/reviews/ (purchase-gated, upsert on re-rate), POST /api/checkout/ (cart→order, wallet deduction + stock decrement + order creation in one transaction.atomic() block — explicitly documented as not yet race-safe under concurrency, since that's Phase 3's job), GET /api/seller/items/ (own inventory + low-stock flag), GET /api/seller/orders/.


Changes have been made in views.py to support role based authentication and access control, creating orders, simple checkout, conditional checks to show sellers only their items, only allowing buyers to place orders, updating inventory and wallet balance when order is placed, buyers submitting reviews and ratings for items they bought

GUI: one static page at / (phase1app/templates/gui.html), signup/login, browse/search/filter/sort, cart/checkout, wallet, and role-specific seller dashboard tabs. We now have an AI generated GPU to test out all the functionality.
