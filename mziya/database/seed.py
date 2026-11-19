"""Script d'initialisation et de peuplement des données fictives de démonstration (Agadir uniquement)."""

import sys
from pathlib import Path
from typing import Optional, Union

# Permet l'exécution directe via `python database/seed.py`
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database.database import db_session, init_db
from services.auth_service import register_user
from services.points_service import award_points
from services.promotion_service import create_promotion
from services.reward_service import create_reward, create_simulated_gift_card


def _get_user_id_by_email(email: str, db_path: Optional[Union[str, Path]] = None) -> Optional[int]:
    with db_session(db_path) as conn:
        row = conn.execute(
            "SELECT id FROM users WHERE lower(email) = ?",
            (email.strip().lower(),),
        ).fetchone()
        return int(row["id"]) if row else None


def _get_merchant_id_by_name(
    business_name: str, db_path: Optional[Union[str, Path]] = None
) -> Optional[int]:
    with db_session(db_path) as conn:
        row = conn.execute(
            "SELECT id FROM merchants WHERE business_name = ?",
            (business_name,),
        ).fetchone()
        return int(row["id"]) if row else None


def seed_database(db_path: Optional[Union[str, Path]] = None) -> None:
    """Initialise la base et insère les données de démonstration sans créer de doublons."""
    init_db(db_path)

    # 1. Compte Administrateur
    if _get_user_id_by_email("admin@mziya.ma", db_path) is None:
        register_user(
            full_name="Équipe Mziya",
            email="admin@mziya.ma",
            phone="0600000001",
            password="Admin123!",
            role="admin",
            neighborhood="Centre-ville",
            language="fr",
            db_path=db_path,
        )

    # 2. Comptes Clients (Agadir uniquement)
    demo_clients = [
        {
            "full_name": "Youssef Amrani",
            "email": "client@mziya.ma",
            "phone": "0611223344",
            "password": "Client123!",
            "neighborhood": "Talborjt",
        },
        {
            "full_name": "Salma Benali",
            "email": "salma.benali@mziya.ma",
            "phone": "0622334455",
            "password": "Client123!",
            "neighborhood": "Founty",
        },
        {
            "full_name": "Karim Tazi",
            "email": "karim.tazi@mziya.ma",
            "phone": "0633445566",
            "password": "Client123!",
            "neighborhood": "Hay Salam",
        },
    ]
    for c in demo_clients:
        if _get_user_id_by_email(c["email"], db_path) is None:
            register_user(
                full_name=c["full_name"],
                email=c["email"],
                phone=c["phone"],
                password=c["password"],
                role="client",
                neighborhood=c["neighborhood"],
                language="fr",
                db_path=db_path,
            )

    # 3. Comptes Commerçants (Agadir uniquement)
    demo_merchants = [
        {
            "full_name": "Hassan El Idrissi",
            "email": "merchant@mziya.ma",
            "phone": "0644556677",
            "password": "Merchant123!",
            "neighborhood": "Centre-ville",
            "business_name": "Supérette Al Baraka",
            "business_type": "Supérette",
            "address": "Avenue Hassan II, Résidence Souss, Agadir",
            "description": "Supérette de quartier proposant produits alimentaires, frais et essentiels du quotidien.",
        },
        {
            "full_name": "Nadia Chraibi",
            "email": "boulangerie@mziya.ma",
            "phone": "0655667788",
            "password": "Merchant123!",
            "neighborhood": "Talborjt",
            "business_name": "Boulangerie Souss",
            "business_type": "Boulangerie & Pâtisserie",
            "address": "Rue du 29 Février, Talborjt, Agadir",
            "description": "Pains traditionnels, viennoiseries chaudes et pâtisseries marocaines.",
        },
        {
            "full_name": "Omar Mansouri",
            "email": "cafe.founty@mziya.ma",
            "phone": "0666778899",
            "password": "Merchant123!",
            "neighborhood": "Founty",
            "business_name": "Café Océan Founty",
            "business_type": "Café & Salon de thé",
            "address": "Boulevard de la Plage, Founty, Agadir",
            "description": "Espace convivial près de la corniche pour petits-déjeuners et pauses café.",
        },
        {
            "full_name": "Khadija Ouali",
            "email": "para.dakhla@mziya.ma",
            "phone": "0677889900",
            "password": "Merchant123!",
            "neighborhood": "Dakhla",
            "business_name": "Parapharmacie Atlas",
            "business_type": "Pharmacie & Parapharmacie",
            "address": "Avenue des FAR, Dakhla, Agadir",
            "description": "Soins dermocosmétiques, huiles d'argan locales et produits de bien-être.",
        },
    ]
    for m in demo_merchants:
        if _get_user_id_by_email(m["email"], db_path) is None:
            register_user(
                full_name=m["full_name"],
                email=m["email"],
                phone=m["phone"],
                password=m["password"],
                role="merchant",
                neighborhood=m["neighborhood"],
                language="fr",
                business_name=m["business_name"],
                business_type=m["business_type"],
                address=m["address"],
                description=m["description"],
                db_path=db_path,
            )

    baraka_id = _get_merchant_id_by_name("Supérette Al Baraka", db_path)
    boulangerie_id = _get_merchant_id_by_name("Boulangerie Souss", db_path)
    cafe_id = _get_merchant_id_by_name("Café Océan Founty", db_path)
    para_id = _get_merchant_id_by_name("Parapharmacie Atlas", db_path)

    # 4. Récompenses simulées (sans doublons)
    seed_rewards = [
        (
            baraka_id,
            "Réduction simulée de 10 MAD",
            "Utilisez 100 points pour obtenir 10 MAD de remise simulée sur vos courses.",
            100,
            10.0,
            "Réduction immédiate",
            40,
            "2027-12-31",
        ),
        (
            baraka_id,
            "Réduction simulée de 25 MAD",
            "Remise simulée de 25 MAD valable sur tout le rayon épicerie.",
            250,
            25.0,
            "Réduction immédiate",
            25,
            "2027-12-31",
        ),
        (
            boulangerie_id,
            "Panier cadeau simulé petit-déjeuner",
            "Assortiment simulé de msemen, baghrir et viennoiseries maison.",
            500,
            60.0,
            "Panier cadeau simulé",
            15,
            "2027-12-31",
        ),
        (
            para_id,
            "Bon d'achat simulé de 100 MAD",
            "Bon d'achat fictif de 100 MAD sur les coffrets bien-être d'Agadir.",
            750,
            100.0,
            "Bon d'achat simulé",
            10,
            "2027-12-31",
        ),
        (
            cafe_id,
            "Boisson chaude offerte simulée",
            "Un café ou thé à la menthe offert en démonstration.",
            80,
            15.0,
            "Produit offert simulé",
            50,
            "2027-12-31",
        ),
    ]
    with db_session(db_path) as conn:
        for m_id, title, desc, pts, disc, rtype, stock, exp in seed_rewards:
            if m_id is None:
                continue
            exists = conn.execute(
                "SELECT id FROM rewards WHERE merchant_id = ? AND title = ?",
                (m_id, title),
            ).fetchone()
            if exists is None:
                create_reward(
                    merchant_id=m_id,
                    title=title,
                    description=desc,
                    points_required=pts,
                    discount_value=disc,
                    reward_type=rtype,
                    stock=stock,
                    expiration_date=exp,
                    db_path=db_path,
                )

    # 5. Promotions locales à Agadir (sans doublons)
    seed_promos = [
        (
            baraka_id,
            "Semaine Fraîcheur Centre-ville",
            "15% de remise simulée sur les fruits, légumes et produits laitiers.",
            15.0,
            "Centre-ville",
            "2026-01-01",
            "2027-12-31",
        ),
        (
            boulangerie_id,
            "Matinées Gourmandes Talborjt",
            "20% de réduction sur les packs petit-déjeuner avant 10h.",
            20.0,
            "Talborjt",
            "2026-01-01",
            "2027-12-31",
        ),
        (
            cafe_id,
            "Pause Corniche Founty",
            "10% de remise fidélité sur les menus goûter face à la mer.",
            10.0,
            "Founty",
            "2026-01-01",
            "2027-12-31",
        ),
        (
            para_id,
            "Offre Argan & Bien-être Dakhla",
            "25% de réduction sur la gamme cosmétique naturelle du Souss.",
            25.0,
            "Dakhla",
            "2026-01-01",
            "2027-12-31",
        ),
    ]
    with db_session(db_path) as conn:
        for m_id, title, desc, pct, nb, start_d, end_d in seed_promos:
            if m_id is None:
                continue
            exists = conn.execute(
                "SELECT id FROM promotions WHERE merchant_id = ? AND title = ?",
                (m_id, title),
            ).fetchone()
            if exists is None:
                create_promotion(
                    merchant_id=m_id,
                    title=title,
                    description=desc,
                    discount_percentage=pct,
                    neighborhood=nb,
                    start_date=start_d,
                    end_date=end_d,
                    db_path=db_path,
                )

    # 6. Transactions simulées initiales (uniquement si aucune transaction n'existe encore)
    youssef_id = _get_user_id_by_email("client@mziya.ma", db_path)
    salma_id = _get_user_id_by_email("salma.benali@mziya.ma", db_path)
    karim_id = _get_user_id_by_email("karim.tazi@mziya.ma", db_path)

    with db_session(db_path) as conn:
        tx_count = conn.execute("SELECT COUNT(*) AS cnt FROM transactions").fetchone()["cnt"]
    if tx_count == 0 and youssef_id and baraka_id:
        award_points(youssef_id, baraka_id, 650.0, "Courses hebdomadaires (simulation)", db_path=db_path)
        if boulangerie_id:
            award_points(youssef_id, boulangerie_id, 300.0, "Pains & pâtisseries (simulation)", db_path=db_path)
        if cafe_id:
            award_points(youssef_id, cafe_id, 250.0, "Petit-déjeuner Founty (simulation)", db_path=db_path)
        if salma_id and cafe_id:
            award_points(salma_id, cafe_id, 420.0, "Salon de thé entre amies (simulation)", db_path=db_path)
        if salma_id and para_id:
            award_points(salma_id, para_id, 800.0, "Coffret soins argan (simulation)", db_path=db_path)
        if karim_id and baraka_id:
            award_points(karim_id, baraka_id, 500.0, "Panier familial (simulation)", db_path=db_path)

    # 7. Carte cadeau simulée initiale (si aucune n'existe)
    with db_session(db_path) as conn:
        gc_count = conn.execute("SELECT COUNT(*) AS cnt FROM gift_cards").fetchone()["cnt"]
    if gc_count == 0 and youssef_id and baraka_id:
        create_simulated_gift_card(
            merchant_id=baraka_id,
            amount=150.0,
            expiration_date="2027-12-31",
            client_id=youssef_id,
            db_path=db_path,
        )

    # 8. Messages initiaux de démonstration (si aucun message n'existe)
    with db_session(db_path) as conn:
        msg_count = conn.execute("SELECT COUNT(*) AS cnt FROM messages").fetchone()["cnt"]
        if msg_count == 0:
            conn.execute(
                """
                INSERT INTO messages (user_id, name, email, subject, message, message_type, status, admin_response)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    youssef_id,
                    "Youssef Amrani",
                    "client@mziya.ma",
                    "Question sur Supérette Al Baraka",
                    "Puis-je utiliser mes points cumulés à Talborjt dans la supérette du Centre-ville ?",
                    "Question",
                    "Traité",
                    "Oui, votre carte QR Mziya est valable dans tous les commerces partenaires d'Agadir.",
                ),
            )
            conn.execute(
                """
                INSERT INTO messages (user_id, name, email, subject, message, message_type, status, admin_response)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    salma_id,
                    "Salma Benali",
                    "salma.benali@mziya.ma",
                    "Suggestion pour les commerces de Founty",
                    "Ce serait super d'ajouter plus de boulangeries partenaires dans le quartier Founty.",
                    "Suggestion",
                    "En cours",
                    "Merci ! Notre équipe d'Agadir contacte de nouveaux commerçants à Founty.",
                ),
            )


if __name__ == "__main__":
    seed_database()
    print("Base de données Mziya initialisée et peuplée avec succès (Agadir).")
