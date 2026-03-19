import NextAuth from 'next-auth';
import Credentials from 'next-auth/providers/credentials';
import { apiClient } from '@/lib/api';

declare module 'next-auth' {
  interface Session {
    accessToken?: string;
    user: {
      id: string;
      email: string;
      name: string;
      role: string;
    };
  }

  interface User {
    accessToken: string;
    id: string;
    email: string;
    name: string;
    role: string;
  }

  interface JWT {
    accessToken?: string;
    id?: string;
    email?: string;
    name?: string;
    role?: string;
  }
}


function parseJwt(token: string) {
  const base64Url = token.split('.')[1];
  const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
  const jsonPayload = Buffer.from(base64, 'base64').toString('utf-8');
  return JSON.parse(jsonPayload);
}

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [
    Credentials({
      name: 'Credentials',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        try {
          const res = await apiClient<{ access_token: string }>(
            '/api/v1/auth/login',
            {
              method: 'POST',
              body: JSON.stringify({
                email: credentials?.email,
                password: credentials?.password,
              }),
            },
          );

          if (res.access_token) {
            const payload = parseJwt(res.access_token);
            return {
              accessToken: res.access_token,
              id: payload.sub,
              email: payload.email,
              name: payload.email, // Will be overridden if we fetch profile
              role: payload.role,
            };
          }

          return null;
        } catch {
          return null;
        }
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.accessToken = (user as any).accessToken;
        token.id = user.id;
        token.email = user.email ?? undefined;
        token.name = user.name ?? undefined;
        token.role = (user as any).role;
      }
      return token;
    },
    async session({ session, token }): Promise<any> {
      (session as any).accessToken = token.accessToken;
      session.user = {
        id: token.id as string,
        email: token.email as string,
        name: token.name as string,
        role: token.role as string,
      } as any;
      return session;
    },
  },

  pages: {
    signIn: '/login',
  },
  session: {
    strategy: 'jwt',
  },
});
