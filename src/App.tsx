/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useState } from 'react';
import {
  CreditCard,
  Gift,
  MapPin,
  QrCode,
  ShieldCheck,
  Store,
  Tag,
  Terminal,
  Users,
} from 'lucide-react';

const AGADIR_NEIGHBORHOODS = [
  'Centre-ville',
  'Talborjt',
  'Haut Founty',
  'Founty',
  'Hay Mohammadi',
  'Dakhla',
  'Al Houda',
  'Tilila',
  'Tikiouine',
  'Bensergao',
  'Anza',
  'Charaf',
  'Hay Salam',
  'Sonaba',
  'Illigh',
  'Cité Suisse',
  'Islane',
];

const DEMO_ACCOUNTS = [
  {
    role: 'Client',
    email: 'client@mziya.ma',
    password: 'Client123!',
    detail: 'Youssef Amrani • Talborjt',
  },
  {
    role: 'Commerçant',
    email: 'merchant@mziya.ma',
    password: 'Merchant123!',
    detail: 'Supérette Al Baraka • Centre-ville',
  },
  {
    role: 'Administration',
    email: 'admin@mziya.ma',
    password: 'Admin123!',
    detail: 'Équipe Mziya • Agadir',
  },
];

export default function App() {
  const [osTab, setOsTab] = useState<'linux' | 'windows'>('linux');

  return (
    <div className="min-h-screen bg-[#f4f7fb] text-slate-800">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-[#0f2942] to-[#0ea5a4] text-lg font-extrabold text-white shadow">
              M
            </div>
            <div>
              <span className="text-xl font-extrabold tracking-tight text-[#0f2942]">
                Mziya
              </span>
              <span className="ml-2 rounded-full bg-[#e6f7f7] px-2.5 py-0.5 text-xs font-semibold text-[#0f766e]">
                Agadir • Maroc
              </span>
            </div>
          </div>
          <span className="text-sm font-medium text-slate-500">
            Python • Streamlit • SQLite • Pandas • Plotly • pytest
          </span>
        </div>
      </header>

      <main className="mx-auto max-w-6xl space-y-6 px-6 py-8">
        <div className="rounded-xl border-l-4 border-[#f97316] bg-orange-50 px-4 py-3 text-sm font-medium text-orange-900">
          Mziya est un prototype de démonstration. Les points, transactions,
          récompenses et cartes cadeaux sont simulés et n’ont aucune valeur
          monétaire réelle.
        </div>

        <section className="grid gap-6 rounded-2xl bg-gradient-to-br from-[#0f2942] via-[#143d63] to-[#0ea5a4] p-8 text-white shadow-lg md:grid-cols-5">
          <div className="space-y-3 md:col-span-3">
            <span className="inline-block rounded-full border border-white/25 bg-white/15 px-3 py-1 text-xs font-semibold">
              Ville pilote : Agadir • Projet complet dans /mziya
            </span>
            <h1 className="text-3xl font-extrabold tracking-tight md:text-4xl">
              Mziya
            </h1>
            <p className="text-lg font-semibold text-teal-200">
              « Une carte, plusieurs commerces, plus d’avantages. »
            </p>
            <p className="text-sm leading-relaxed text-slate-200">
              Plateforme marocaine de fidélité multi-commerces destinée aux
              clients, petits commerçants et supérettes d’Agadir. L’ensemble du
              code Python, Streamlit, SQLite et des tests pytest est généré dans
              le dossier <code>mziya/</code>.
            </p>
          </div>

          <div className="rounded-2xl border border-white/20 bg-[#091b2c]/80 p-5 md:col-span-2">
            <div className="mb-3 flex items-center justify-between">
              <span className="text-sm font-bold tracking-wider">
                MZIYA PASS
              </span>
              <QrCode className="h-5 w-5 text-teal-300" />
            </div>
            <div className="mb-4 h-6 w-9 rounded bg-gradient-to-br from-amber-200 to-amber-500" />
            <div className="text-xs text-slate-400">Identifiant QR</div>
            <div className="font-mono text-base font-bold tracking-wider text-white">
              MZIYA-CLIENT-0001
            </div>
            <div className="mt-4 flex items-end justify-between text-xs text-slate-300">
              <span>1 point = 10 MAD dépensés</span>
              <span className="font-bold text-teal-300">FR / EN / AR</span>
            </div>
          </div>
        </section>

        <section className="grid gap-4 md:grid-cols-3">
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="mb-2 flex items-center gap-2 font-bold text-[#0f2942]">
              <Users className="h-5 w-5 text-[#0ea5a4]" />
              Espace Client
            </div>
            <p className="text-sm text-slate-600">
              QR code personnel téléchargeable, solde de points simulés,
              récompenses, cartes cadeaux simulées, promotions par quartier et
              notifications.
            </p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="mb-2 flex items-center gap-2 font-bold text-[#0f2942]">
              <Store className="h-5 w-5 text-[#f97316]" />
              Espace Commerçant
            </div>
            <p className="text-sm text-slate-600">
              Achats simulés, attribution automatique de points, gestion des
              récompenses et promotions, cartes cadeaux et graphiques Plotly.
            </p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="mb-2 flex items-center gap-2 font-bold text-[#0f2942]">
              <ShieldCheck className="h-5 w-5 text-[#16a34a]" />
              Administration
            </div>
            <p className="text-sm text-slate-600">
              Gestion des rôles et comptes avec <code>is_active</code>, suivi
              des transactions, traitement des réclamations et KPIs SQLite.
            </p>
          </div>
        </section>

        <section className="grid gap-6 md:grid-cols-2">
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="mb-3 flex items-center justify-between">
              <div className="flex items-center gap-2 font-bold text-[#0f2942]">
                <Terminal className="h-5 w-5 text-[#0ea5a4]" />
                Lancement local (Streamlit)
              </div>
              <div className="flex gap-2 text-xs">
                <button
                  type="button"
                  onClick={() => setOsTab('linux')}
                  className={`rounded-lg px-2.5 py-1 font-semibold ${
                    osTab === 'linux'
                      ? 'bg-[#0f2942] text-white'
                      : 'bg-slate-100 text-slate-600'
                  }`}
                >
                  Linux / macOS
                </button>
                <button
                  type="button"
                  onClick={() => setOsTab('windows')}
                  className={`rounded-lg px-2.5 py-1 font-semibold ${
                    osTab === 'windows'
                      ? 'bg-[#0f2942] text-white'
                      : 'bg-slate-100 text-slate-600'
                  }`}
                >
                  Windows
                </button>
              </div>
            </div>
            <pre className="overflow-x-auto rounded-lg bg-slate-900 p-4 text-xs leading-relaxed text-teal-200">
              {osTab === 'linux'
                ? `cd mziya
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python database/seed.py
streamlit run app.py
pytest`
                : `cd mziya
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
python database/seed.py
streamlit run app.py
pytest`}
            </pre>
          </div>

          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="mb-3 flex items-center gap-2 font-bold text-[#0f2942]">
              <CreditCard className="h-5 w-5 text-[#0ea5a4]" />
              Comptes de démonstration (mziya.db)
            </div>
            <div className="space-y-2.5">
              {DEMO_ACCOUNTS.map((acc) => (
                <div
                  key={acc.email}
                  className="flex items-center justify-between rounded-lg border border-slate-100 bg-slate-50 px-3 py-2 text-sm"
                >
                  <div>
                    <div className="font-bold text-[#0f2942]">{acc.role}</div>
                    <div className="text-xs text-slate-500">{acc.detail}</div>
                  </div>
                  <div className="text-right font-mono text-xs">
                    <div>{acc.email}</div>
                    <div className="text-[#0ea5a4]">{acc.password}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="mb-3 flex items-center gap-2 font-bold text-[#0f2942]">
            <MapPin className="h-5 w-5 text-[#0ea5a4]" />
            Quartiers autorisés à Agadir ({AGADIR_NEIGHBORHOODS.length})
          </div>
          <div className="flex flex-wrap gap-2">
            {AGADIR_NEIGHBORHOODS.map((nb) => (
              <span
                key={nb}
                className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-semibold text-[#0f2942]"
              >
                {nb}
              </span>
            ))}
          </div>
          <div className="mt-4 flex flex-wrap gap-4 text-xs text-slate-500">
            <span className="flex items-center gap-1">
              <Gift className="h-4 w-4 text-[#16a34a]" /> Récompenses & cartes
              cadeaux simulées
            </span>
            <span className="flex items-center gap-1">
              <Tag className="h-4 w-4 text-[#f97316]" /> Promotions locales
              Agadir uniquement
            </span>
          </div>
        </section>
      </main>
    </div>
  );
}
