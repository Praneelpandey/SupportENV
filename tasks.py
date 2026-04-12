"""
tasks.py — Task configurations and sample ticket dataset for SupportEnv.

Three tasks of increasing difficulty:
  1. classify  — agent only sets category
  2. prioritize — agent sets category + priority
  3. resolve   — agent sets category + priority + reply
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


# ---------------------------------------------------------------------------
# Task configuration
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TaskConfig:
    """Describes what the agent is expected to do."""
    name: str
    difficulty: str
    requires_category: bool = True
    requires_priority: bool = False
    requires_reply: bool = False


TASKS: dict[str, TaskConfig] = {
    "classify": TaskConfig(
        name="classify",
        difficulty="easy",
        requires_category=True,
        requires_priority=False,
        requires_reply=False,
    ),
    "prioritize": TaskConfig(
        name="prioritize",
        difficulty="medium",
        requires_category=True,
        requires_priority=True,
        requires_reply=False,
    ),
    "resolve": TaskConfig(
        name="resolve",
        difficulty="hard",
        requires_category=True,
        requires_priority=True,
        requires_reply=True,
    ),
}


# ---------------------------------------------------------------------------
# Ticket dataclass
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Ticket:
    ticket_id: str
    ticket_text: str
    true_category: str          # billing | technical | general
    true_priority: str          # low | medium | high | urgent
    ideal_reply_keywords: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# 30 realistic sample tickets (10 per task)
# ---------------------------------------------------------------------------

TICKETS: dict[str, list[Ticket]] = {
    # ------------------------------------------------------------------
    # Task 1 — classify (10 tickets)
    # ------------------------------------------------------------------
    "classify": [
        Ticket(
            ticket_id="CLF-001",
            ticket_text=(
                "I was charged twice for my monthly subscription last week. "
                "My bank statement shows two identical transactions of $14.99. "
                "Please refund the duplicate charge immediately."
            ),
            true_category="billing",
            true_priority="high",
            ideal_reply_keywords=["refund", "duplicate", "charge", "investigate", "apologize"],
        ),
        Ticket(
            ticket_id="CLF-002",
            ticket_text=(
                "The app keeps crashing every time I try to open the settings page. "
                "I'm running Android 14 on a Pixel 8. Already tried clearing cache."
            ),
            true_category="technical",
            true_priority="high",
            ideal_reply_keywords=["crash", "settings", "update", "reinstall", "logs"],
        ),
        Ticket(
            ticket_id="CLF-003",
            ticket_text=(
                "How do I change my display name? I looked in account settings "
                "but I couldn't find the option anywhere."
            ),
            true_category="general",
            true_priority="low",
            ideal_reply_keywords=["profile", "settings", "display", "name", "navigate"],
        ),
        Ticket(
            ticket_id="CLF-004",
            ticket_text=(
                "My invoice from March is showing the wrong tax rate. I'm located "
                "in Oregon which has no state sales tax but I was charged 8%."
            ),
            true_category="billing",
            true_priority="medium",
            ideal_reply_keywords=["tax", "invoice", "correction", "refund", "updated"],
        ),
        Ticket(
            ticket_id="CLF-005",
            ticket_text=(
                "Getting a 502 Bad Gateway error on the dashboard since this morning. "
                "None of my team members can access it either. Is there an outage?"
            ),
            true_category="technical",
            true_priority="urgent",
            ideal_reply_keywords=["outage", "status", "investigating", "restore", "update"],
        ),
        Ticket(
            ticket_id="CLF-006",
            ticket_text=(
                "Can you tell me the difference between the Pro and Enterprise plans? "
                "I need to know before our annual renewal next month."
            ),
            true_category="general",
            true_priority="low",
            ideal_reply_keywords=["plan", "features", "comparison", "upgrade", "pricing"],
        ),
        Ticket(
            ticket_id="CLF-007",
            ticket_text=(
                "I cancelled my subscription two weeks ago but I was still charged today! "
                "This is unacceptable. I want a full refund and confirmation of cancellation."
            ),
            true_category="billing",
            true_priority="urgent",
            ideal_reply_keywords=["cancellation", "refund", "confirm", "apologize", "processed"],
        ),
        Ticket(
            ticket_id="CLF-008",
            ticket_text=(
                "The file upload feature is broken. Whenever I try to upload a PDF larger "
                "than 5 MB it just hangs and eventually times out with no error message."
            ),
            true_category="technical",
            true_priority="medium",
            ideal_reply_keywords=["upload", "file", "size", "limit", "fix"],
        ),
        Ticket(
            ticket_id="CLF-009",
            ticket_text=(
                "Hi, I just wanted to say thank you! Your product has been amazing. "
                "One question — do you have a referral program?"
            ),
            true_category="general",
            true_priority="low",
            ideal_reply_keywords=["thank", "referral", "program", "reward", "share"],
        ),
        Ticket(
            ticket_id="CLF-010",
            ticket_text=(
                "My API calls are returning 401 Unauthorized errors even though I regenerated "
                "my API key yesterday. I've double-checked the key in my config."
            ),
            true_category="technical",
            true_priority="high",
            ideal_reply_keywords=["API", "key", "authorization", "verify", "token"],
        ),
    ],

    # ------------------------------------------------------------------
    # Task 2 — prioritize (10 tickets)
    # ------------------------------------------------------------------
    "prioritize": [
        Ticket(
            ticket_id="PRI-001",
            ticket_text=(
                "URGENT: Our entire organization (200+ users) is locked out of the platform. "
                "We're in the middle of a product launch and cannot access any data."
            ),
            true_category="technical",
            true_priority="urgent",
            ideal_reply_keywords=["escalate", "access", "restore", "priority", "team"],
        ),
        Ticket(
            ticket_id="PRI-002",
            ticket_text=(
                "I see a small discrepancy of $0.03 on last month's invoice. Not a big deal "
                "but wanted to flag it for your records."
            ),
            true_category="billing",
            true_priority="low",
            ideal_reply_keywords=["discrepancy", "invoice", "corrected", "noted", "thank"],
        ),
        Ticket(
            ticket_id="PRI-003",
            ticket_text=(
                "We've been experiencing intermittent latency spikes (3-5s response times) "
                "on the reporting module for the past 3 days. It's affecting our SLA."
            ),
            true_category="technical",
            true_priority="high",
            ideal_reply_keywords=["latency", "performance", "investigating", "SLA", "monitoring"],
        ),
        Ticket(
            ticket_id="PRI-004",
            ticket_text=(
                "I accidentally purchased the annual plan instead of monthly. Can you switch "
                "it and adjust the billing? I literally just bought it 5 minutes ago."
            ),
            true_category="billing",
            true_priority="medium",
            ideal_reply_keywords=["switch", "plan", "adjustment", "refund", "confirm"],
        ),
        Ticket(
            ticket_id="PRI-005",
            ticket_text=(
                "Where can I find documentation for the new webhook feature you announced "
                "in last week's newsletter?"
            ),
            true_category="general",
            true_priority="low",
            ideal_reply_keywords=["documentation", "webhook", "link", "guide", "help"],
        ),
        Ticket(
            ticket_id="PRI-006",
            ticket_text=(
                "Security alert — I received a login notification from an IP address I don't "
                "recognize. I've changed my password but I'm worried about a data breach."
            ),
            true_category="technical",
            true_priority="urgent",
            ideal_reply_keywords=["security", "breach", "investigate", "password", "2FA"],
        ),
        Ticket(
            ticket_id="PRI-007",
            ticket_text=(
                "Your system charged my expired credit card and now I have an overdraft fee "
                "from my bank. I need you to reimburse the overdraft fee as well."
            ),
            true_category="billing",
            true_priority="high",
            ideal_reply_keywords=["overdraft", "reimburse", "expired", "card", "apologize"],
        ),
        Ticket(
            ticket_id="PRI-008",
            ticket_text=(
                "Just curious — do you have any plans to add dark mode to the web app? "
                "Would be a great quality-of-life improvement."
            ),
            true_category="general",
            true_priority="low",
            ideal_reply_keywords=["feature", "request", "roadmap", "dark", "feedback"],
        ),
        Ticket(
            ticket_id="PRI-009",
            ticket_text=(
                "I'm unable to export reports to CSV. The button does nothing when clicked. "
                "I need these reports for a board meeting tomorrow morning."
            ),
            true_category="technical",
            true_priority="high",
            ideal_reply_keywords=["export", "CSV", "fix", "workaround", "urgent"],
        ),
        Ticket(
            ticket_id="PRI-010",
            ticket_text=(
                "I want to downgrade from the Enterprise plan to Pro. Can you walk me through "
                "the process and any changes to my billing?"
            ),
            true_category="billing",
            true_priority="medium",
            ideal_reply_keywords=["downgrade", "plan", "billing", "changes", "process"],
        ),
    ],

    # ------------------------------------------------------------------
    # Task 3 — resolve (10 tickets)
    # ------------------------------------------------------------------
    "resolve": [
        Ticket(
            ticket_id="RES-001",
            ticket_text=(
                "I'm absolutely furious! I've been charged $299 for an enterprise plan I NEVER "
                "signed up for. This is the third time I've contacted you about billing errors. "
                "If this isn't resolved today I'm disputing the charge with my bank."
            ),
            true_category="billing",
            true_priority="urgent",
            ideal_reply_keywords=["refund", "apologize", "escalate", "immediately", "resolved"],
        ),
        Ticket(
            ticket_id="RES-002",
            ticket_text=(
                "The mobile app crashes instantly after the latest update (v4.2.1). I've tried "
                "reinstalling, clearing data, and restarting my phone. Nothing works. "
                "I'm on iOS 17.3, iPhone 15 Pro."
            ),
            true_category="technical",
            true_priority="high",
            ideal_reply_keywords=["update", "crash", "fix", "version", "investigating"],
        ),
        Ticket(
            ticket_id="RES-003",
            ticket_text=(
                "Hi there! I'm a new user and I'm confused about how to set up team workspaces. "
                "The onboarding guide mentions it but doesn't show where the button is."
            ),
            true_category="general",
            true_priority="low",
            ideal_reply_keywords=["workspace", "setup", "navigate", "guide", "welcome"],
        ),
        Ticket(
            ticket_id="RES-004",
            ticket_text=(
                "Our payment method was updated last week but the system is still trying to "
                "charge the old card. We've received 3 failed payment notifications."
            ),
            true_category="billing",
            true_priority="high",
            ideal_reply_keywords=["payment", "update", "card", "retry", "resolved"],
        ),
        Ticket(
            ticket_id="RES-005",
            ticket_text=(
                "CRITICAL: Data loss detected. Several of our project files from the shared "
                "drive appear to be missing after your maintenance window last night. "
                "We need immediate recovery."
            ),
            true_category="technical",
            true_priority="urgent",
            ideal_reply_keywords=["recovery", "data", "backup", "restore", "priority"],
        ),
        Ticket(
            ticket_id="RES-006",
            ticket_text=(
                "I'd like to request an invoice with our company's tax ID (VAT number) for "
                "compliance purposes. Our finance team needs it by end of week."
            ),
            true_category="billing",
            true_priority="medium",
            ideal_reply_keywords=["invoice", "VAT", "generate", "compliance", "send"],
        ),
        Ticket(
            ticket_id="RES-007",
            ticket_text=(
                "The SSO integration with our Okta setup stopped working after your last "
                "platform update. 50 team members can't log in. We are dead in the water."
            ),
            true_category="technical",
            true_priority="urgent",
            ideal_reply_keywords=["SSO", "Okta", "integration", "fix", "restore"],
        ),
        Ticket(
            ticket_id="RES-008",
            ticket_text=(
                "Can I get a copy of your data processing agreement (DPA)? Our legal team "
                "needs it for a GDPR audit we're preparing for next quarter."
            ),
            true_category="general",
            true_priority="medium",
            ideal_reply_keywords=["DPA", "GDPR", "legal", "document", "send"],
        ),
        Ticket(
            ticket_id="RES-009",
            ticket_text=(
                "The notification system is completely broken for me. I'm not receiving any "
                "email or in-app notifications. I missed an important deadline because of this. "
                "I've checked spam folders and notification settings — everything looks correct."
            ),
            true_category="technical",
            true_priority="high",
            ideal_reply_keywords=["notification", "email", "settings", "investigate", "fix"],
        ),
        Ticket(
            ticket_id="RES-010",
            ticket_text=(
                "I'm being charged in USD but I'm based in the EU. Can you switch my billing "
                "currency to EUR? Also wondering if prices differ between currencies."
            ),
            true_category="billing",
            true_priority="medium",
            ideal_reply_keywords=["currency", "EUR", "billing", "switch", "pricing"],
        ),
    ],
}
