import { NextFunction, Request, Response } from 'express';
import jwt from 'jsonwebtoken';
export type AuthRequest = Request & { user?: { id: number; role: string } };
export const sign = (user: { id: number; role: string }) => jwt.sign(user, process.env.JWT_SECRET || 'dev-change-me', { expiresIn: '8h' });
export function auth(req: AuthRequest, res: Response, next: NextFunction) { const header = req.headers.authorization; if (!header?.startsWith('Bearer ')) return res.status(401).json({ message: 'Non authentifié' }); try { req.user = jwt.verify(header.slice(7), process.env.JWT_SECRET || 'dev-change-me') as any; next(); } catch { return res.status(401).json({ message: 'Session invalide' }); } }
export const permit = (...roles: string[]) => (req: AuthRequest, res: Response, next: NextFunction) => roles.length && !roles.includes(req.user?.role || '') ? res.status(403).json({ message: 'Permission refusée' }) : next();
