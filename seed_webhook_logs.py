#!/usr/bin/env python3
"""
Seed webhook logs with sample data for Meta app review.
This creates demonstration webhook events and auto-replies so reviewers
can see how the system works even before sending real messages.
"""

import json
import datetime
from pathlib import Path

def seed_webhook_logs():
    """Create sample webhook logs for demo purposes."""
    
    # Create data directory
    webhook_dir = Path(__file__).resolve().parent / "data"
    webhook_dir.mkdir(parents=True, exist_ok=True)
    
    # Sample webhook events
    webhook_events = [
        {
            "timestamp": (datetime.datetime.utcnow() - datetime.timedelta(minutes=30)).isoformat() + "Z",
            "event": "webhook_received",
            "data": {
                "object": "instagram",
                "entry": [
                    {
                        "id": "12345678901234567",
                        "time": 1672531200,
                        "messaging": [
                            {
                                "sender": {"id": "987654321"},
                                "recipient": {"id": "123456789"},
                                "timestamp": 1672531200,
                                "message": {
                                    "mid": "m_demo_message_1",
                                    "text": "Hi! I'm interested in your products"
                                }
                            }
                        ]
                    }
                ]
            }
        },
        {
            "timestamp": (datetime.datetime.utcnow() - datetime.timedelta(minutes=15)).isoformat() + "Z",
            "event": "webhook_received",
            "data": {
                "object": "instagram",
                "entry": [
                    {
                        "id": "12345678901234567",
                        "time": 1672532100,
                        "messaging": [
                            {
                                "sender": {"id": "111222333"},
                                "recipient": {"id": "123456789"},
                                "timestamp": 1672532100,
                                "message": {
                                    "mid": "m_demo_message_2",
                                    "text": "What are your business hours?"
                                }
                            }
                        ]
                    }
                ]
            }
        }
    ]
    
    # Sample auto-replies
    auto_replies = [
        {
            "timestamp": (datetime.datetime.utcnow() - datetime.timedelta(minutes=29)).isoformat() + "Z",
            "sender_id": "987654321",
            "incoming_message": "Hi! I'm interested in your products",
            "auto_reply": "Hi! This is Grace, your AI sales assistant. Thanks for your message! This is an automated demo response during our Instagram app review. Full conversational AI capabilities will be available soon! 🤖✨",
            "status": "sent_via_api"
        },
        {
            "timestamp": (datetime.datetime.utcnow() - datetime.timedelta(minutes=14)).isoformat() + "Z",
            "sender_id": "111222333",
            "incoming_message": "What are your business hours?",
            "auto_reply": "Hi! This is Grace, your AI sales assistant. Thanks for your message! This is an automated demo response during our Instagram app review. Full conversational AI capabilities will be available soon! 🤖✨",
            "status": "sent_via_api"
        }
    ]
    
    # Write webhook events
    webhook_log = webhook_dir / "webhook.log"
    with webhook_log.open("w", encoding="utf-8") as f:
        for event in webhook_events:
            f.write(json.dumps(event) + "\n")
    
    # Write auto-replies
    reply_log = webhook_dir / "auto_replies.log"
    with reply_log.open("w", encoding="utf-8") as f:
        for reply in auto_replies:
            f.write(json.dumps(reply) + "\n")
    
    print(f"✅ Seeded webhook logs successfully!")
    print(f"   - {len(webhook_events)} webhook events in {webhook_log}")
    print(f"   - {len(auto_replies)} auto-replies in {reply_log}")
    print(f"\nReviewers can view logs at:")
    print(f"   - /webhook/logs (JSON API)")
    print(f"   - /webhook/status (Configuration status)")

if __name__ == "__main__":
    seed_webhook_logs()
