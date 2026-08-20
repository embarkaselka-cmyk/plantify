import Decimal from 'decimal.js';
Decimal.set({ precision: 28, rounding: Decimal.ROUND_HALF_UP });
export type LineInput = { quantity: string|number|Decimal; priceHt: string|number|Decimal; discountRate?: string|number|Decimal; vatRate?: string|number|Decimal };
export const d = (value: string|number|Decimal|undefined|null) => new Decimal(value ?? 0);
export const round = (value: Decimal) => value.toDecimalPlaces(2);
export function calcLine(input: LineInput) {
  const gross = d(input.quantity).mul(d(input.priceHt));
  const discount = gross.mul(d(input.discountRate)).div(100);
  const totalHt = round(gross.minus(discount));
  const vatAmount = round(totalHt.mul(d(input.vatRate)).div(100));
  return { gross: round(gross), discount: round(discount), totalHt, vatAmount, totalTtc: round(totalHt.plus(vatAmount)) };
}
export function calcTotals(lines: LineInput[], stamp: string|number|Decimal = 0) {
  return lines.reduce((acc, line) => {
    const item = calcLine(line);
    const totalHt = round(acc.totalHt.plus(item.totalHt));
    const discountTotal = round(acc.discountTotal.plus(item.discount));
    const vatTotal = round(acc.vatTotal.plus(item.vatAmount));
    return { totalHt, discountTotal, vatTotal, stamp: round(d(stamp)), totalTtc: round(totalHt.plus(vatTotal).plus(d(stamp))) };
  }, { totalHt: d(0), discountTotal: d(0), vatTotal: d(0), stamp: round(d(stamp)), totalTtc: d(0) });
}
const units = ['','un','deux','trois','quatre','cinq','six','sept','huit','neuf','dix','onze','douze','treize','quatorze','quinze','seize'];
function under100(n: number): string { if (n < 17) return units[n]; if (n < 20) return `dix-${units[n - 10]}`; if (n < 70) { const tens = ['','','vingt','trente','quarante','cinquante','soixante'][Math.floor(n / 10)]; const rest = n % 10; return rest ? `${tens}-${rest === 1 ? 'et-un' : units[rest]}` : tens; } if (n < 80) return `soixante-${under100(n - 60)}`; const rest = n - 80; return rest ? `quatre-vingt-${under100(rest)}` : 'quatre-vingts'; }
function words(n: number): string { if (n === 0) return 'zéro'; if (n < 100) return under100(n); if (n < 1000) { const h = Math.floor(n / 100), rest = n % 100; return `${h > 1 ? `${units[h]} ` : ''}cent${rest ? ` ${words(rest)}` : h > 1 ? 's' : ''}`; } if (n < 1000000) { const k = Math.floor(n / 1000), rest = n % 1000; return `${k > 1 ? `${words(k)} ` : ''}mille${rest ? ` ${words(rest)}` : ''}`; } const m = Math.floor(n / 1000000), rest = n % 1000000; return `${words(m)} million${m > 1 ? 's' : ''}${rest ? ` ${words(rest)}` : ''}`; }
export function amountToFrench(value: string|number|Decimal) { const val = d(value); const dinars = val.floor().toNumber(); const cents = val.minus(dinars).mul(100).round().toNumber(); return `${words(dinars)} dinars algériens${cents ? ` et ${words(cents)} centimes` : ''}`; }
