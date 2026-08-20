import { prisma } from '../lib/prisma.js';
export async function nextNumber(code: string) {
  const year = new Date().getFullYear();
  const series = await prisma.numberSeries.upsert({ where: { code }, create: { code, prefix: code, year, counter: 1, length: 5 }, update: { counter: { increment: 1 } } });
  return `${series.prefix}-${year}-${String(series.counter).padStart(series.length, '0')}`;
}
