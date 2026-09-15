from sqlalchemy.orm import Session

from .repositories.knowledge import create_article, get_article_by_title
from .schemas import KnowledgeArticleCreate


SEED_ARTICLES = [
    {
        "title": "Invoice and payment help",
        "intent": "billing",
        "keywords": ["bill", "invoice", "payment", "charge", "rechnung", "zahlung"],
        "content_en": (
            "You can view invoices and payment status in My Account under Billing. "
            "If a charge looks incorrect, open the invoice details and select "
            "Dispute a charge."
        ),
        "content_de": (
            "Rechnungen und den Zahlungsstatus finden Sie in Mein Konto unter "
            "Abrechnung. Bei einer falschen Gebühr öffnen Sie die Rechnungsdetails "
            "und wählen Gebühr reklamieren."
        ),
    },
    {
        "title": "Internet troubleshooting",
        "intent": "technical_support",
        "keywords": [
            "internet",
            "wifi",
            "router",
            "connection",
            "offline",
            "verbindung",
            "störung",
        ],
        "content_en": (
            "Restart the router after disconnecting power for 30 seconds, then check "
            "the service-status page. If the connection is still offline, run the "
            "line test in My Account."
        ),
        "content_de": (
            "Trennen Sie den Router 30 Sekunden vom Strom und starten Sie ihn neu. "
            "Prüfen Sie danach die Statusseite. Bleibt die Verbindung offline, "
            "führen Sie den Leitungstest in Mein Konto aus."
        ),
    },
    {
        "title": "Device setup",
        "intent": "device_setup",
        "keywords": [
            "device",
            "setup",
            "install",
            "box",
            "gerät",
            "einrichten",
            "installation",
        ],
        "content_en": (
            "Connect the device to power and the router, wait for the status light to "
            "turn green, then follow the activation steps shown on screen."
        ),
        "content_de": (
            "Verbinden Sie das Gerät mit Strom und Router. Warten Sie auf die grüne "
            "Statusleuchte und folgen Sie den Aktivierungsschritten auf dem Bildschirm."
        ),
    },
    {
        "title": "Cancellation policy",
        "intent": "cancellation",
        "keywords": [
            "cancel",
            "terminate",
            "contract",
            "kündigen",
            "kündigung",
            "vertrag",
        ],
        "content_en": (
            "Cancellation depends on the minimum contract term. Because identity and "
            "account verification are required, a specialist must review the request."
        ),
        "content_de": (
            "Die Kündigung hängt von der Mindestvertragslaufzeit ab. Da eine Identitäts- "
            "und Kontoprüfung erforderlich ist, muss ein Mitarbeiter die Anfrage prüfen."
        ),
    },
]


def seed_knowledge_base(database: Session) -> None:
    for item in SEED_ARTICLES:
        if not get_article_by_title(database, item["title"]):
            create_article(database, KnowledgeArticleCreate(**item))
