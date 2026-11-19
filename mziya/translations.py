"""Système de traduction multilingue (Français, English, العربية) pour Mziya."""

from typing import Dict

LANGUAGE_LABELS = {
    "fr": "🇫🇷 Français",
    "en": "🇬🇧 English",
    "ar": "🇲🇦 العربية",
}

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "app_name": {
        "fr": "Mziya",
        "en": "Mziya",
        "ar": "مزية",
    },
    "slogan": {
        "fr": "Une carte, plusieurs commerces, plus d’avantages.",
        "en": "One card, multiple local shops, more benefits.",
        "ar": "بطاقة واحدة، متاجر متعددة، مزايا أكثر.",
    },
    "concept_desc": {
        "fr": "La plateforme marocaine de fidélité qui connecte les habitants d'Agadir à leurs supérettes et commerces de proximité.",
        "en": "The Moroccan loyalty platform connecting Agadir residents with their local mini-markets and neighborhood shops.",
        "ar": "منصة الوفاء المغربية التي تربط سكان أكادير بمتاجرهم المحلية ومحلات القرب.",
    },
    "simulation_banner": {
        "fr": "Mziya est un prototype de démonstration. Les points, transactions, récompenses et cartes cadeaux sont simulés et n’ont aucune valeur monétaire réelle.",
        "en": "Mziya is a demonstration prototype. Points, transactions, rewards, and gift cards are simulated and have no real monetary value.",
        "ar": "مزية هو نموذج تجريبي. النقاط والمعاملات والمكافآت وبطاقات الهدايا محاكاة وليس لها أي قيمة مالية حقيقية.",
    },
    "home": {"fr": "Accueil", "en": "Home", "ar": "الرئيسية"},
    "login": {"fr": "Connexion", "en": "Login", "ar": "تسجيل الدخول"},
    "logout": {"fr": "Déconnexion", "en": "Logout", "ar": "تسجيل الخروج"},
    "register": {"fr": "Créer un compte", "en": "Create an account", "ar": "إنشاء حساب"},
    "register_client": {
        "fr": "Créer un compte client",
        "en": "Create a client account",
        "ar": "إنشاء حساب زبون",
    },
    "register_merchant": {
        "fr": "Créer un compte commerçant",
        "en": "Create a merchant account",
        "ar": "إنشاء حساب تاجر",
    },
    "client": {"fr": "Client", "en": "Client", "ar": "زبون"},
    "merchant": {"fr": "Commerçant", "en": "Merchant", "ar": "تاجر"},
    "admin": {"fr": "Administration", "en": "Administration", "ar": "الإدارة"},
    "dashboard": {"fr": "Tableau de bord", "en": "Dashboard", "ar": "لوحة التحكم"},
    "my_profile": {"fr": "Mon profil", "en": "My profile", "ar": "ملفي الشخصي"},
    "my_points": {"fr": "Mes points", "en": "My points", "ar": "نقاطي"},
    "my_qr": {"fr": "Mon QR code", "en": "My QR code", "ar": "رمز QR الخاص بي"},
    "rewards": {"fr": "Récompenses", "en": "Rewards", "ar": "المكافآت"},
    "my_rewards": {"fr": "Mes récompenses", "en": "My rewards", "ar": "مكافآتي"},
    "promotions": {"fr": "Promotions", "en": "Promotions", "ar": "العروض"},
    "history": {"fr": "Historique", "en": "History", "ar": "السجل"},
    "notifications": {"fr": "Notifications", "en": "Notifications", "ar": "الإشعارات"},
    "messages": {"fr": "Messages", "en": "Messages", "ar": "الرسائل"},
    "complaints": {"fr": "Réclamations", "en": "Complaints", "ar": "الشكايات"},
    "messages_complaints": {
        "fr": "Messages et réclamations",
        "en": "Messages & complaints",
        "ar": "الرسائل والشكايات",
    },
    "contact_complaints": {
        "fr": "Contact et réclamations",
        "en": "Contact & complaints",
        "ar": "التواصل والشكايات",
    },
    "gift_cards": {
        "fr": "Cartes cadeaux simulées",
        "en": "Simulated gift cards",
        "ar": "بطاقات الهدايا المحاكاة",
    },
    "gift_card_disclaimer": {
        "fr": "Carte cadeau simulée, sans valeur monétaire réelle.",
        "en": "Simulated gift card, with no real monetary value.",
        "ar": "بطاقة هدية محاكاة، بدون قيمة مالية حقيقية.",
    },
    "add": {"fr": "Ajouter", "en": "Add", "ar": "إضافة"},
    "edit": {"fr": "Modifier", "en": "Edit", "ar": "تعديل"},
    "disable": {"fr": "Désactiver", "en": "Disable", "ar": "تعطيل"},
    "enable": {"fr": "Réactiver", "en": "Reactivate", "ar": "إعادة تفعيل"},
    "delete": {"fr": "Supprimer", "en": "Delete", "ar": "حذف"},
    "save": {"fr": "Enregistrer", "en": "Save", "ar": "حفظ"},
    "cancel": {"fr": "Annuler", "en": "Cancel", "ar": "إلغاء"},
    "confirm": {"fr": "Confirmer", "en": "Confirm", "ar": "تأكيد"},
    "name": {"fr": "Nom", "en": "Name", "ar": "الاسم"},
    "full_name": {"fr": "Nom complet", "en": "Full name", "ar": "الاسم الكامل"},
    "email": {"fr": "Email", "en": "Email", "ar": "البريد الإلكتروني"},
    "phone": {"fr": "Téléphone", "en": "Phone", "ar": "رقم الهاتف"},
    "password": {"fr": "Mot de passe", "en": "Password", "ar": "كلمة المرور"},
    "neighborhood": {"fr": "Quartier", "en": "Neighborhood", "ar": "الحي"},
    "city_pilot": {"fr": "Ville pilote : Agadir", "en": "Pilot city: Agadir", "ar": "المدينة التجريبية: أكادير"},
    "business": {"fr": "Commerce", "en": "Business", "ar": "المتجر"},
    "business_name": {"fr": "Nom du commerce", "en": "Business name", "ar": "اسم المتجر"},
    "business_type": {"fr": "Type de commerce", "en": "Business type", "ar": "نوع المتجر"},
    "address": {"fr": "Adresse", "en": "Address", "ar": "العنوان"},
    "description": {"fr": "Description", "en": "Description", "ar": "الوصف"},
    "send": {"fr": "Envoyer", "en": "Send", "ar": "إرسال"},
    "statistics": {"fr": "Statistiques", "en": "Statistics", "ar": "الإحصائيات"},
    "no_results": {"fr": "Aucun résultat", "en": "No results", "ar": "لا توجد نتائج"},
    "operation_success": {"fr": "Opération réussie", "en": "Operation successful", "ar": "تمت العملية بنجاح"},
    "error_occurred": {"fr": "Une erreur est survenue", "en": "An error occurred", "ar": "حدث خطأ ما"},
    "language": {"fr": "Langue", "en": "Language", "ar": "اللغة"},
    "navigation": {"fr": "Navigation", "en": "Navigation", "ar": "التنقل"},
    "client_benefits_title": {
        "fr": "Avantages pour les clients",
        "en": "Benefits for clients",
        "ar": "مزايا للزبناء",
    },
    "merchant_benefits_title": {
        "fr": "Avantages pour les commerçants",
        "en": "Benefits for merchants",
        "ar": "مزايا للتجار",
    },
    "how_it_works_title": {
        "fr": "Comment ça fonctionne en 3 étapes",
        "en": "How it works in 3 steps",
        "ar": "كيف تعمل المنصة في 3 خطوات",
    },
    "local_promotions_title": {
        "fr": "Promotions locales à Agadir",
        "en": "Local promotions in Agadir",
        "ar": "عروض محلية في أكادير",
    },
    "rewards_showcase_title": {
        "fr": "Récompenses simulées disponibles",
        "en": "Available simulated rewards",
        "ar": "المكافآت المحاكاة المتاحة",
    },
    "agadir_neighborhoods_title": {
        "fr": "Quartiers couverts à Agadir",
        "en": "Covered neighborhoods in Agadir",
        "ar": "الأحياء المغطاة في أكادير",
    },
    "all_neighborhoods": {
        "fr": "Tous les quartiers d'Agadir",
        "en": "All Agadir neighborhoods",
        "ar": "جميع أحياء أكادير",
    },
    "all_businesses": {
        "fr": "Tous les commerces",
        "en": "All businesses",
        "ar": "جميع المتاجر",
    },
    "download_qr": {
        "fr": "Télécharger mon QR code",
        "en": "Download my QR code",
        "ar": "تحميل رمز QR الخاص بي",
    },
    "points_balance": {
        "fr": "Solde de points",
        "en": "Points balance",
        "ar": "رصيد النقاط",
    },
    "redeem_reward": {
        "fr": "Utiliser cette récompense",
        "en": "Redeem reward",
        "ar": "استبدال المكافأة",
    },
    "record_purchase": {
        "fr": "Enregistrer un achat simulé",
        "en": "Record a simulated purchase",
        "ar": "تسجيل عملية شراء محاكاة",
    },
    "amount_mad": {
        "fr": "Montant (MAD)",
        "en": "Amount (MAD)",
        "ar": "المبلغ (درهم)",
    },
    "subject": {"fr": "Sujet", "en": "Subject", "ar": "الموضوع"},
    "message_type": {"fr": "Type de message", "en": "Message type", "ar": "نوع الرسالة"},
    "message_body": {"fr": "Message", "en": "Message", "ar": "نص الرسالة"},
    "status": {"fr": "Statut", "en": "Status", "ar": "الحالة"},
    "users": {"fr": "Utilisateurs", "en": "Users", "ar": "المستخدمون"},
    "transactions": {"fr": "Transactions", "en": "Transactions", "ar": "المعاملات"},
    "businesses": {"fr": "Commerces", "en": "Businesses", "ar": "المتاجر"},
    "search_client": {
        "fr": "Rechercher un client (nom, email ou ID QR)",
        "en": "Search a client (name, email, or QR ID)",
        "ar": "البحث عن زبون (الاسم، البريد أو رمز QR)",
    },
    "mark_all_read": {
        "fr": "Tout marquer comme lu",
        "en": "Mark all as read",
        "ar": "تحديد الكل كمقروء",
    },
}

# Correspondance inverse pour supporter get_text("Accueil", lang) et get_text("home", lang)
_LABEL_TO_KEY: Dict[str, str] = {}
for _k, _langs in TRANSLATIONS.items():
    _fr_val = _langs.get("fr", "")
    if _fr_val and _fr_val not in _LABEL_TO_KEY:
        _LABEL_TO_KEY[_fr_val.lower()] = _k


def get_text(key: str, language: str = "fr") -> str:
    """Retourne le texte traduit pour une clé et une langue données (fr, en, ar)."""
    lang = language if language in ("fr", "en", "ar") else "fr"
    entry = TRANSLATIONS.get(key)
    if entry is None:
        mapped_key = _LABEL_TO_KEY.get(str(key).strip().lower())
        if mapped_key:
            entry = TRANSLATIONS.get(mapped_key)
    if entry is None:
        return str(key)
    return entry.get(lang) or entry.get("fr") or str(key)


def is_rtl(language: str) -> bool:
    """Indique si la langue sélectionnée s'affiche de droite à gauche (RTL)."""
    return language == "ar"
