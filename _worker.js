export default {
  async fetch(request, env) {
    // Your worker code here
    return new Response("Bot is running!");
  }
};