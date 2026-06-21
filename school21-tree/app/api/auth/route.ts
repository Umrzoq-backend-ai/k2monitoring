import { NextResponse } from 'next/server';

let cachedToken: string | null = null;
let tokenExpires: number = 0;

export async function getToken(): Promise<string> {
  const now = Date.now();

  if (cachedToken && now < tokenExpires) {
    return cachedToken;
  }

  const resp = await fetch(process.env.SCHOOL21_AUTH_URL!, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      client_id: 's21-open-api',
      username: process.env.SCHOOL21_USERNAME!,
      password: process.env.SCHOOL21_PASSWORD!,
      grant_type: 'password',
    }),
  });

  if (!resp.ok) {
    throw new Error(`Auth failed: ${resp.status}`);
  }

  const data = await resp.json();
  cachedToken = data.access_token;
  tokenExpires = now + (data.expires_in - 30) * 1000;

  return cachedToken!;
}

export async function GET() {
  try {
    const token = await getToken();
    return NextResponse.json({ success: true, hasToken: !!token });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 401 });
  }
}
