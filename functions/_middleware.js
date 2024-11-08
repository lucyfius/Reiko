export async function onRequest(context) {
  try {
    // Your bot initialization code here
    return await context.next();
  } catch (err) {
    return new Response(`Error: ${err.message}`, { status: 500 });
  }
} 