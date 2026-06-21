import { NextRequest, NextResponse } from 'next/server';
import { getToken } from '../auth/route';

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const endpoint = searchParams.get('endpoint');

  if (!endpoint) {
    return NextResponse.json({ error: 'endpoint parameter required' }, { status: 400 });
  }

  try {
    const token = await getToken();
    const baseUrl = process.env.SCHOOL21_BASE_URL!;

    const resp = await fetch(`${baseUrl}/${endpoint}`, {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!resp.ok) {
      return NextResponse.json(
        { error: `API returned ${resp.status}` },
        { status: resp.status }
      );
    }

    const data = await resp.json();
    return NextResponse.json(data);
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
