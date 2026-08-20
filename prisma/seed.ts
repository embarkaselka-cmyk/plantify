import 'dotenv/config';
import bcrypt from 'bcryptjs';
import { PrismaClient } from '@prisma/client';
const prisma = new PrismaClient();
const permissions = ['View','Create','Edit','Delete','Validate','Cancel','Export','Settings','Users','Backup','Restore'];
async function main() {
  for (const name of ['Administrateur','Comptable','Commercial','Consultation']) {
    const role = await prisma.role.upsert({ where: { name }, create: { name }, update: {} });
    for (const action of permissions) await prisma.permission.upsert({ where: { action_entity_roleId: { action, entity: '*', roleId: role.id } }, create: { action, entity: '*', roleId: role.id }, update: {} });
  }
  const role = await prisma.role.findUniqueOrThrow({ where: { name: 'Administrateur' } });
  const email = process.env.ADMIN_EMAIL || 'admin@selka.local';
  const password = process.env.ADMIN_PASSWORD || 'ChangeMe-Strong-2026!';
  await prisma.user.upsert({ where: { email }, create: { email, username: 'admin', fullName: 'Administrateur', passwordHash: await bcrypt.hash(password, 12), roleId: role.id }, update: { roleId: role.id } });
  await prisma.company.upsert({ where: { id: 1 }, create: { id: 1, logoPath: '/assets/logo-selka-cme.jpg', raisonSociale: 'EURL SELKA C.M.E', activite: 'COMMERCE MULTIPLE ET ENTREPRISES' }, update: {} });
  for (const [key,value,group] of [['vat.rates','19,9,0,Exonéré','Fiscalité'],['stamp.enabled','false','Timbre fiscal'],['stamp.amount','0','Timbre fiscal'],['fiscal.regime','Régime réel','Fiscalité'],['smtp.host','','Email']] as const) await prisma.setting.upsert({ where: { key }, create: { key, value, group }, update: {} });
  for (const code of ['FAC','DEV','AV','BC','BL']) await prisma.numberSeries.upsert({ where: { code }, create: { code, prefix: code, year: new Date().getFullYear(), counter: 0, length: 5 }, update: {} });
}
main().finally(() => prisma.$disconnect());
