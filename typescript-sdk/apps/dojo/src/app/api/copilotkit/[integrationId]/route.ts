import {
  CopilotRuntime,
  ExperimentalEmptyAdapter,
  copilotRuntimeNextJSAppRouterEndpoint,
} from "@copilotkit/runtime";
import { agentsIntegrations } from "@/agents";

import { NextRequest, NextResponse } from "next/server";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization, x-copilotkit-runtime-client-gql-version",
  "Access-Control-Allow-Credentials": 'true',
};

export async function OPTIONS(request: NextRequest) {
  return new NextResponse(null, { status: 200, headers: corsHeaders });
}

export async function POST(request: NextRequest) {
  const integrationId = request.url.split("/").pop();
  const integration = agentsIntegrations.find((i) => i.id === integrationId);
  if (!integration) {
    return new NextResponse("Integration not found", { 
      status: 404, 
      headers: corsHeaders 
    });
  }
  const agents = await integration.agents();
  const runtime = new CopilotRuntime({
    // @ts-ignore for now
    agents,
  });
  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter: new ExperimentalEmptyAdapter(),
    endpoint: `/api/copilotkit/${integrationId}`,
  });

  const response = await handleRequest(request);
  
  // Add CORS headers to the response
  Object.entries(corsHeaders).forEach(([key, value]) => {
    response.headers.set(key, value);
  });

  return response;
}
