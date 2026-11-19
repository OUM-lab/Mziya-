# Mziya — Plateforme de fidélité multi-commerces à Agadir

> **Slogan :** *« Une carte, plusieurs commerces, plus d’avantages. »*

## Présentation

**Mziya** est un prototype de démonstration destiné aux habitants, petits commerçants et supérettes de la ville pilote d’**Agadir (Maroc)**.  
L’application permet aux clients de cumuler et d’utiliser des points de fidélité **simulés** dans plusieurs commerces partenaires à l’aide d’un QR code personnel unique.

> ⚠️ **Avertissement :** Mziya est un prototype de démonstration. Les points, transactions, récompenses et cartes cadeaux sont simulés et n’ont aucune valeur monétaire réelle. Aucun paiement réel ni donnée bancaire n’est utilisé.

---

## Fonctionnalités principales

- **Multilingue (FR / EN / AR)** avec sélecteur dans la barre latérale et support RTL pour l’arabe.
- **Espace Client :**
  - QR code personnel non sensible (`MZIYA-CLIENT-XXXX`) téléchargeable en PNG.
  - Solde de points simulés (1 point par tranche de 10 MAD dépensés).
  - Découverte des promotions locales filtrées par quartier d’Agadir.
  - Utilisation de récompenses simulées (contrôle du solde et du stock, blocage de solde négatif).
  - Cartes cadeaux simulées sans valeur monétaire réelle.
  - Historique des transactions, notifications et messagerie/réclamations.
- **Espace Commerçant :**
  - Fiche commerce limitée à son propre établissement à Agadir.
  - Recherche de clients et enregistrement d’achats simulés.
  - Création, modification et désactivation de récompenses, promotions et cartes cadeaux simulées.
  - Statistiques interactives (Pandas & Plotly) et messages liés au commerce.
- **Espace Administration :**
  - Vue d’ensemble avec KPIs et graphiques Plotly alimentés par SQLite.
  - Gestion des clients et commerçants (ajout, désactivation avec confirmation via `is_active`, réactivation).
  - Suivi des commerces, transactions, récompenses, promotions et traitement des réclamations.

---

## Technologies utilisées

- **Python 3.11+**
- **Streamlit** (interface web)
- **SQLite** (base de données locale `mziya.db` avec requêtes paramétrées et clés étrangères)
- **Pandas & Plotly** (analyses et graphiques)
- **qrcode & Pillow** (génération de QR codes PNG)
- **bcrypt** (hachage sécurisé des mots de passe)
- **pytest** (tests automatisés)

---

## Structure du projet

```text
mziya/
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── .gitignore
├── translations.py
├── style.css
├── database/
│   ├── __init__.py
│   ├── database.py
│   ├── schema.sql
│   └── seed.py
├── services/
│   ├── __init__.py
│   ├── auth_service.py
│   ├── points_service.py
│   ├── qr_service.py
│   ├── reward_service.py
│   ├── promotion_service.py
│   └── message_service.py
├── pages/
│   ├── __init__.py
│   ├── home_page.py
│   ├── auth_page.py
│   ├── client_page.py
│   ├── merchant_page.py
│   └── admin_page.py
├── components/
│   ├── __init__.py
│   ├── sidebar.py
│   ├── cards.py
│   ├── charts.py
│   └── tables.py
├── utils/
│   ├── __init__.py
│   ├── validators.py
│   ├── security.py
│   ├── constants.py
│   └── formatting.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_points.py
│   ├── test_rewards.py
│   └── test_database.py
└── assets/
```

---

## Installation et lancement

### Windows

```bash
cd mziya
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python database/seed.py
streamlit run app.py
```

### Linux et macOS

```bash
cd mziya
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python database/seed.py
streamlit run app.py
```

---

## Comptes de démonstration

| Rôle | Email | Mot de passe | Détails |
| :--- | :--- | :--- | :--- |
| **Administration** | `admin@mziya.ma` | `Admin123!` | Équipe Mziya |
| **Client** | `client@mziya.ma` | `Client123!` | Youssef Amrani (Talborjt) |
| **Commerçant** | `merchant@mziya.ma` | `Merchant123!` | Supérette Al Baraka (Centre-ville) |

---

## Lancer les tests

```bash
pytest
```

---

## Limites du prototype et évolutions futures

- **Limites :** Prototype local mono-instance SQLite ; toutes les opérations (points, achats, récompenses, cartes cadeaux) sont simulées ; couverture limitée aux 17 quartiers d’Agadir.
- **Évolutions futures :** Scan caméra QR en boutique, application mobile native iOS/Android, notifications push temps réel, extension progressive à d’autres villes du Souss-Massa puis du Maroc, tableau de bord analytique avancé pour les commerçants.
