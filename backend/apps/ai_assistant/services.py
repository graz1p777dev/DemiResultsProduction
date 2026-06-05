from django.contrib.auth import get_user_model
from django.db.models import Q

from apps.products.models import Product

from .models import AIConversation, AIMessage


def find_client_for_ai(payload):
    User = get_user_model()
    phone = payload.get("phone") or payload.get("customer_phone")
    telegram = payload.get("telegram") or payload.get("telegram_username")
    google_id = payload.get("google_id")
    name = payload.get("name") or payload.get("customer_name")

    queryset = User.objects.filter(role=User.Role.CLIENT)
    if phone:
        user = queryset.filter(phone=phone).first()
        if user:
            return user
    if telegram:
        normalized = telegram.lstrip("@")
        user = queryset.filter(client_profile__telegram_username__iexact=normalized).first()
        if user:
            return user
    if google_id:
        user = queryset.filter(google_id=google_id).first()
        if user:
            return user
    if name:
        return queryset.filter(Q(username__icontains=name) | Q(first_name__icontains=name) | Q(last_name__icontains=name)).first()
    return None


def save_ai_conversation(payload, client=None):
    external_id = payload.get("conversation_id", "")
    defaults = {
        "client": client,
        "customer_phone": payload.get("phone") or payload.get("customer_phone") or "",
        "telegram_username": (payload.get("telegram") or payload.get("telegram_username") or "").lstrip("@"),
    }
    if external_id:
        conversation, _ = AIConversation.objects.get_or_create(external_id=external_id, defaults=defaults)
    else:
        conversation = AIConversation.objects.create(**defaults)
    if client and conversation.client_id != client.id:
        conversation.client = client
        conversation.save(update_fields=["client", "updated_at"])
    return conversation


def save_ai_message(conversation, *, role, content, payload=None):
    if not content:
        return None
    return AIMessage.objects.create(conversation=conversation, role=role, content=content, payload=payload or {})


def search_products_for_ai(payload):
    query = payload.get("product_query") or payload.get("query") or payload.get("message") or ""
    products = Product.objects.select_related("brand", "category").filter(is_active=True)
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    return [
        {
            "id": product.id,
            "name": product.name,
            "sku": product.sku,
            "brand": product.brand.name,
            "category": product.category.name,
            "price": str(product.price),
            "stock_quantity": product.stock_quantity,
            "is_low_stock": product.is_low_stock,
        }
        for product in products.order_by("name")[:10]
    ]


def build_ai_response_payload(payload, log_id):
    client = find_client_for_ai(payload)
    conversation = save_ai_conversation(payload, client=client)
    message_text = payload.get("message") or payload.get("text") or ""
    save_ai_message(conversation, role=AIMessage.Role.USER, content=message_text, payload=payload)
    return {
        "ok": True,
        "log_id": log_id,
        "conversation_id": conversation.pk,
        "client_id": client.pk if client else None,
        "products": search_products_for_ai(payload),
    }
