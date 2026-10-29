import { NextResponse } from "next/server";

/**
 * Runtime configuration read from the server environment on each request, so one
 * built image works in every deployment (NEXT_PUBLIC_* values would be frozen at
 * build time).
 */
export const dynamic = "force-dynamic";

export function GET() {
  return NextResponse.json(
    // "app" identifies this as the Argus dashboard to health probes (argus doctor).
    { app: "argus-dashboard", wsUrl: process.env.ARGUS_PUBLIC_WS_URL ?? null },
    { headers: { "Cache-Control": "no-store" } },
  );
}
