"""Constantes métier de la plateforme Mziya (Agadir uniquement)."""

PILOT_CITY = "Agadir"

AGADIR_NEIGHBORHOODS = [
    "Centre-ville",
    "Talborjt",
    "Haut Founty",
    "Founty",
    "Hay Mohammadi",
    "Dakhla",
    "Al Houda",
    "Tilila",
    "Tikiouine",
    "Bensergao",
    "Anza",
    "Charaf",
    "Hay Salam",
    "Sonaba",
    "Illigh",
    "Cité Suisse",
    "Islane",
]

ALLOWED_ROLES = ("client", "merchant", "admin")

TRANSACTION_TYPES = ("earn", "redeem")

BUSINESS_TYPES = [
    "Supérette",
    "Épicerie",
    "Boulangerie & Pâtisserie",
    "Café & Salon de thé",
    "Pharmacie & Parapharmacie",
    "Librairie & Papeterie",
    "Prêt-à-porter",
    "Boucherie & Volaille",
    "Fruits & Légumes",
    "Coiffure & Beauté",
    "Autre commerce de proximité",
]

REWARD_TYPES = [
    "Réduction immédiate",
    "Bon d'achat simulé",
    "Panier cadeau simulé",
    "Produit offert simulé",
]

MESSAGE_TYPES = [
    "Question",
    "Réclamation",
    "Suggestion",
    "Problème technique",
]

MESSAGE_STATUSES = [
    "Nouveau",
    "En cours",
    "Traité",
]

GIFT_CARD_STATUSES = ("active", "disabled", "expired")

SIMULATION_DISCLAIMER = (
    "Mziya est un prototype de démonstration. Les points, transactions, "
    "récompenses et cartes cadeaux sont simulés et n’ont aucune valeur monétaire réelle."
)
