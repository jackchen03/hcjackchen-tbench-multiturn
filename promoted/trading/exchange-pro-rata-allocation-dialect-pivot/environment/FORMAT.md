# Matcher interface

Run python3 /app/matcher.py BOOK_JSON OUTPUT_JSON.

The input is a JSON list of events. Each event has event_id, incoming_qty, and resting_orders; each resting order has order_id, participant_id, price, seq, and qty.

The output is a JSON list containing one object per resting order with exact keys event_id, order_id, and filled_qty, including zero fills.

