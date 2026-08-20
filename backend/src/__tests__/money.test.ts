import { describe, expect, it } from 'vitest';
import { amountToFrench, calcLine, calcTotals } from '../lib/money.js';
describe('financial precision', () => {
  it('calculates 19% VAT', () => { const line = calcLine({ quantity: 1, priceHt: 1000, vatRate: 19 }); expect(line.vatAmount.toString()).toBe('190'); expect(line.totalTtc.toString()).toBe('1190'); });
  it('calculates 9% VAT', () => expect(calcLine({ quantity: 1, priceHt: 1000, vatRate: 9 }).totalTtc.toString()).toBe('1090'));
  it('applies discount', () => { const line = calcLine({ quantity: 2, priceHt: 1000, discountRate: 10, vatRate: 19 }); expect(line.totalHt.toString()).toBe('1800'); expect(line.vatAmount.toString()).toBe('342'); });
  it('supports stamp', () => expect(calcTotals([{ quantity: 1, priceHt: 1000, vatRate: 19 }], 10).totalTtc.toString()).toBe('1200'));
  it('writes amount in French', () => expect(amountToFrench(1190)).toContain('mille cent quatre-vingt-dix'));
});
