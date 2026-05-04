# DNS Configuration Reference

After completing `_docs/DEPLOY.md` Step 3 successfully, your DNS for
`gurbanipath.org` should look like this (assuming you moved DNS to
Cloudflare, which is recommended):

| Type   | Name | Content                  | Proxy   | TTL  |
|--------|------|--------------------------|---------|------|
| CNAME  | @    | `gurbanipath.pages.dev`  | Proxied | Auto |
| CNAME  | www  | `gurbanipath.pages.dev`  | Proxied | Auto |

The `Proxied` setting (orange cloud icon in Cloudflare) means traffic
flows through Cloudflare for caching, DDoS protection, and SSL.
This is what you want.

## Email DNS (for feedback@gurbanipath.org)

Cloudflare Email Routing is the simplest way to set up an email alias:

1. In Cloudflare dashboard → select your domain → **Email** →
   **Email Routing**
2. Click **Get started**
3. Cloudflare will add the necessary MX and TXT records automatically
4. Create an alias: `feedback@gurbanipath.org` → forward to your
   personal email
5. Verify your destination email when Cloudflare emails you

Other aliases to consider once the project grows:
- `corrections@gurbanipath.org` — for verse corrections specifically
- `seva@gurbanipath.org` — for volunteer inquiries
- `legal@gurbanipath.org` — for IP / takedown / formal correspondence

## Verifying DNS propagation

To check whether your DNS has propagated:

```bash
dig gurbanipath.org +short
dig www.gurbanipath.org +short
```

Both should resolve to Cloudflare IPs. Or use a web tool like
https://www.whatsmydns.net to check from multiple regions.

## Common issues

**HTTPS not working after 30 minutes** — In Cloudflare, go to your
domain → **SSL/TLS** → set encryption mode to **Full** (not Flexible
and not Strict). Pages handles its own certificates.

**`www.` works but root doesn't** — Some registrars don't support
CNAME at root. Use Cloudflare's nameservers (Path A in DEPLOY.md).

**Email forwarding stops working** — Check Cloudflare Email Routing
status; Cloudflare requires periodic verification of destination
addresses.
