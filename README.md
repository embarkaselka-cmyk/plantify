# EURL SELKA C.M.E — ERP Facturation Algérie

Application professionnelle de facturation et gestion commerciale pour **EURL SELKA C.M.E — COMMERCE MULTIPLE ET ENTREPRISES**.

## Technologies
React, TypeScript, Vite, Tailwind CSS, Recharts, Lucide React, Node.js, Express, Prisma ORM, SQLite, JWT, bcrypt, PDFKit, XLSX, Vitest.

## Structure
- `frontend/` interface React française et responsive.
- `backend/` API Express sécurisée.
- `prisma/` schéma relationnel, migrations et seed.
- `public/assets/` logo officiel utilisé par l'API/PDF.
- `backups/`, `uploads/`, `docs/`.

## Installation
```bash
npm install
cp .env.example .env
npm run db:migrate -- --name init
npm run db:seed
npm run build
npm test
npm run dev
```

## Lancement
- Frontend : http://localhost:5173
- Backend API : http://localhost:4000
- Production locale : `npm run build && npm start`

## Administrateur initial
Configurer dans `.env` avant `npm run db:seed` :
- `ADMIN_EMAIL=admin@selka.local`
- `ADMIN_PASSWORD=ChangeMe-Strong-2026!`

Changez ce mot de passe dès la première connexion.

## Modules inclus
Entreprise, clients, produits/services, factures, devis, avoirs, bons de commande, bons de livraison, paiements, impayés, dashboard, rapports, exports XLSX, PDF facture A4, recherche globale, archives logiques, rôles/permissions, audit log, backup/restore.

## Fiscalité et configuration
Les taux TVA, le timbre fiscal, le régime fiscal, SMTP, les coordonnées société, les informations bancaires et les mentions PDF sont configurables. Les valeurs vides de l'entreprise doivent être renseignées par l'administrateur : NIF, NIS, RC, article d'imposition, RIB, banque, adresse, téléphone et email.

## Logo officiel
Placez le fichier officiel joint à la conversation dans :
- `frontend/public/logo-selka-cme.jpg`
- `public/assets/logo-selka-cme.jpg`

Si `/mnt/data/1000018559.jpg` existe, le script de création l'a déjà copié. Aucun logo généré ou redessiné n'est utilisé.

## Backup / Restore
- Backup : `POST /api/backup`
- Restore : `POST /api/restore` avec `{ "file": "backup-...sqlite" }`

## Notes légales
Avant un usage commercial réel en Algérie, faites valider par votre comptable/conseiller fiscal les mentions obligatoires, règles de timbre fiscal, régime TVA/IFU, modalités d'avoir, conservation documentaire et numérotation selon les textes DGI applicables. Le logiciel n'est pas présenté comme certifié, homologué ou agréé DGI.
