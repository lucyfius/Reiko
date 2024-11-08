export async function onRequest(context) {
  // Basic health check endpoint
  return new Response("Discord bot is running!");
} 