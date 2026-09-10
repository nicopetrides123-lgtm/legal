#!/usr/bin/env python3
"""
Static legal-site generator.

Generates a landing page, a shared Terms of Service, and a tailored
Privacy Policy for each app, into ./docs (the GitHub Pages source folder).

To update: edit CONFIG or APPS below, then run:  python3 generate.py
"""

import html
import os

# ---------------------------------------------------------------------------
# CONFIG  --  edit these to match your Apple Developer account details.
# ---------------------------------------------------------------------------
CONFIG = {
    "developer": "Nicolas Petrides",          # <- must match your App Store name
    "email": "nicopetrides123@gmail.com",
    "jurisdiction": "the State of Oregon, United States",
    "site_title": "App Legal Center",
    # Bump this whenever the policy text materially changes -- the policies
    # themselves promise that material changes get a new "last updated" date.
    "updated": "August 5, 2026",
}

# ---------------------------------------------------------------------------
# APPS  --  one entry per app.
#   slug     : filename + URL (lowercase, hyphens, no spaces)
#   name     : display name
#   blurb    : one-line description
#   category : data-practice bucket -> drives the privacy policy content
#              "offline"  = no data leaves the device
#              "ads"      = shows Google AdMob ads (collects device/ad data)
#              "iap"      = in-app purchases, offline content, no ads
#              "cloud"    = accounts + data stored in the cloud (Firebase)
#   icloud   : optional, True if the app syncs via the USER's own iCloud
#              (NSUbiquitousKeyValueStore / CloudKit). Adds a short section.
#
# The category must match what the app ACTUALLY ships, because the policy has
# to line up with the App Store privacy "nutrition label". In particular:
# "iap" states outright that there is no advertising -- so the moment an app
# starts serving AdMob ads, move it to "ads".
#
# An "ads" app that ALSO sells in-app purchases must set "iap": True, which adds
# the purchase wording to its page. Do NOT set it otherwise: until 2026-08-06 the
# "ads" template told every reader the app "may offer optional in-app purchases",
# which was false for 7 of the 9 ads apps and contradicted an App Store listing
# answering IAP = No. Ground the flag in code -- `import StoreKit` plus a
# .storekit file -- not in what the app feels like it should have.
# ---------------------------------------------------------------------------
APPS = [
    {"slug": "color-sort",        "name": "Color Sort",         "category": "ads",     "blurb": "A relaxing water-sort color puzzle game."},
    {"slug": "reactor",           "name": "Reactor",            "category": "ads",     "blurb": "An idle reactor tap-and-build game."},
    {"slug": "blockburst",        "name": "BlockBurst",         "category": "ads",     "blurb": "A block-drop grid puzzle game."},
    {"slug": "matcha-tycoon",     "name": "Matcha Shop Tycoon", "category": "ads",     "blurb": "A matcha-shop tycoon simulation game."},
    # EconQuest and ʻŌleloQuest are the only two "ads" apps that really sell IAPs
    # (verified: `import StoreKit` + a .storekit file in each).
    {"slug": "econquest",         "name": "EconQuest",          "category": "ads",     "iap": True, "blurb": "A game-based app for learning economics."},
    {"slug": "strategylab",       "name": "StrategyLab",        "category": "ads",     "blurb": "A stock-strategy backtesting app."},
    # Derivatives 101 and SignQuest were "offline", whose text claims "no
    # advertising" -- but both ship live AdMob unit ids, a real
    # GADApplicationIdentifier, MobileAds.start() and banners in the UI.
    {"slug": "derivatives-101",   "name": "Derivatives 101",    "category": "ads",     "blurb": "A course app for learning options and derivatives."},
    # Cashflow: moved iap -> ads 2026-09-01. Real AdMob units are being wired in,
    # so "iap" (which claims "no advertising") would understate what it collects.
    # Keeps iap:True for its three non-consumables.
    {"slug": "cashflow",          "name": "Cashflow",           "category": "ads",     "iap": True, "blurb": "An offline personal-finance learning and budgeting app."},
    {"slug": "dailyhealth",       "name": "DailyHealth",        "category": "offline", "blurb": "A private, fully offline health tracker."},
    {"slug": "signquest",         "name": "SignQuest",          "category": "ads",     "blurb": "An app for learning American Sign Language."},
    # ʻŌleloQuest was "iap", but it ships live AdMob banner/interstitial/rewarded
    # units -- the "iap" text claims "no advertising", which would have been false.
    {"slug": "oleloquest",        "name": "ʻŌleloQuest",         "category": "ads",     "iap": True, "blurb": "An offline app for learning the Hawaiian language."},
    {"slug": "pourfolio",         "name": "Pourfolio",          "category": "cloud",   "blurb": "A drink journal with optional social features."},
    {"slug": "chapteros",         "name": "ChapterOS",          "category": "cloud",   "blurb": "An organization/chapter management app."},

    # Added 2026-08-05. Chipwave and Nova Swarm have AdMob code but are NOT
    # registered on AdMob, so their ad units are nil in release and no ads are
    # served -- which is why they are still "iap". Switch them to "ads" as soon
    # as real unit ids go in, or the policy will understate what they collect.
    # SigmaQuest made that move on 2026-09-01; its real units are being wired in.
    {"slug": "sigmaquest",        "name": "SigmaQuest",         "category": "ads",     "iap": True, "blurb": "An offline app for learning statistics.", "icloud": True},
    # Ready Room: registered on AdMob 2026-09-09 (app ca-app-pub-7603265843182353~7622326334)
    # with real banner + interstitial units wired in. No StoreKit anywhere in the
    # target and no NSUbiquitousKeyValueStore, so no "iap" and no "icloud" -- both
    # verified in source rather than assumed.
    {"slug": "ready-room",        "name": "Ready Room",         "category": "ads",     "blurb": "A study app for the ASTB-E aviation selection test battery."},
    {"slug": "chipwave",          "name": "Chipwave",           "category": "iap",     "blurb": "A play-money social casino game. Play chips only, with no cash-out and no prizes of value."},
    {"slug": "novaswarm",         "name": "Nova Swarm",         "category": "iap",     "blurb": "A bullet-heaven arcade roguelite."},
]

# ---------------------------------------------------------------------------
# HTML shell
# ---------------------------------------------------------------------------
def page(title, description, body, depth=0):
    """Wrap body content in the site shell. depth = folder depth for relative links."""
    root = "../" * depth
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{html.escape(description)}">
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="{root}style.css">
</head>
<body>
<header class="site-header">
  <a class="brand" href="{root}index.html">{html.escape(CONFIG['site_title'])}</a>
  <nav>
    <a href="{root}index.html">Apps</a>
    <a href="{root}terms.html">Terms</a>
  </nav>
</header>
<main>
{body}
</main>
<footer class="site-footer">
  <p>&copy; 2026 {html.escape(CONFIG['developer'])}. All rights reserved.</p>
  <p>Contact: <a href="mailto:{CONFIG['email']}">{html.escape(CONFIG['email'])}</a></p>
</footer>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Privacy policy bodies by category
# ---------------------------------------------------------------------------
def privacy_body(app):
    name = html.escape(app["name"])
    cat = app["category"]
    intro = f"""<p class="lede">This Privacy Policy explains how <strong>{name}</strong> handles your information.
    We designed this app to respect your privacy.</p>"""

    if cat == "offline":
        sections = f"""
<h2>The short version</h2>
<p><strong>{name} does not collect, transmit, or share any personal information.</strong>
The app runs entirely on your device. There are no accounts, no analytics, no advertising,
and no third-party trackers.</p>

<h2>Information we collect</h2>
<p>None. We operate no servers and receive no data from you. The app does not request access
to your contacts, location, photos, microphone, or other personal information.</p>

<h2>Data stored on your device</h2>
<p>Any content you create in the app &mdash; such as your progress, settings, entries, or
records &mdash; is stored <strong>only on your device</strong>. It is never uploaded to us or
to anyone else. If you delete the app, this data is removed with it. If your device is set up
with iCloud device backups, a copy may be included in your own encrypted Apple backup, which is
controlled entirely by you through your Apple account.</p>

<h2>Children's privacy</h2>
<p>Because the app collects no data at all, it collects nothing from children. It is safe for
users of all ages in that respect.</p>
"""
    elif cat == "ads":
        # Only apps that actually ship StoreKit get purchase wording. See the
        # note on the APPS list -- claiming purchases an app does not have
        # contradicts the App Store listing's own IAP answer.
        if app.get("iap"):
            short_purchases = (", and it may offer optional\nin-app purchases processed by Apple")
            purchases_section = f"""
<h2>In-app purchases</h2>
<p>{name} offers optional purchases. Payment is handled entirely by Apple through the App Store.
We never see or store your payment card details.</p>
"""
        else:
            short_purchases = ""
            purchases_section = f"""
<h2>In-app purchases</h2>
<p>{name} has none. There is nothing to buy inside the app, and we never see or store payment
details of any kind.</p>
"""

        sections = f"""
<h2>The short version</h2>
<p>{name} does not require an account and we do not collect personal information directly.
The app shows advertising provided by <strong>Google AdMob</strong>{short_purchases}. Those
services collect limited technical data as described below.</p>

<h2>Advertising (Google AdMob)</h2>
<p>To keep the app free, {name} displays ads served by Google AdMob. To deliver and measure ads,
Google may collect and process technical information such as your device's advertising identifier,
IP address, general device information, and app-interaction events. This data is handled by Google
under its own policies, not by us.</p>
<ul>
  <li>Google&rsquo;s Privacy Policy: <a href="https://policies.google.com/privacy">policies.google.com/privacy</a></li>
  <li>How Google uses data from apps that use its services:
      <a href="https://policies.google.com/technologies/partner-sites">policies.google.com/technologies/partner-sites</a></li>
</ul>
<p>On iOS, you can limit ad tracking at any time under
<em>Settings &rsaquo; Privacy &amp; Security &rsaquo; Tracking</em> and
<em>Settings &rsaquo; Privacy &amp; Security &rsaquo; Apple Advertising</em>.</p>

{purchases_section}
<h2>Information we collect ourselves</h2>
<p>We do not operate our own servers and do not collect personal information directly. Your
progress and settings are stored locally on your device.</p>

<h2>Children's privacy</h2>
<p>The app is not directed at children under 13, and we do not knowingly collect personal
information from children. Advertising is served in a general-audience context.</p>
"""
    elif cat == "iap":
        sections = f"""
<h2>The short version</h2>
<p>{name} runs on your device and does not collect personal information. It offers optional
in-app purchases that are processed by Apple. There is no advertising and no account.</p>

<h2>Information we collect</h2>
<p>None directly. We operate no servers and do not receive personal data from you. Your progress
and settings are stored locally on your device.</p>

<h2>In-app purchases</h2>
<p>{name} may offer optional purchases (for example, to unlock content). All payments are handled
by Apple through the App Store under Apple&rsquo;s terms. We never see or store your payment card
details. Apple provides us only with anonymized information needed to confirm a purchase and to
prevent fraud.</p>

<h2>Restoring purchases</h2>
<p>Purchase records are tied to your Apple Account so you can restore them on your devices. This is
managed by Apple, not by us.</p>

<h2>Children's privacy</h2>
<p>We do not knowingly collect personal information from children. Purchases require your Apple
Account and any parental controls you have configured.</p>
"""
    elif cat == "cloud":
        sections = f"""
<h2>Overview</h2>
<p>{name} offers features that require an account and store data in the cloud so the app can work
across devices and, where applicable, enable social features. This section explains what we collect
and how it is used.</p>

<h2>Information we collect</h2>
<ul>
  <li><strong>Account information</strong> you provide when you sign up, such as your email address
      and display name.</li>
  <li><strong>Content you create</strong> in the app (for example, entries, posts, comments, lists,
      or organization data), which is stored so you can access it and, where you choose, share it.</li>
  <li><strong>Basic technical data</strong> such as device and diagnostic information used to operate
      and secure the service.</li>
</ul>
<p>Any social or sharing features are <strong>opt-in</strong>: content is private to you unless you
explicitly choose to share it.</p>

<h2>How your data is stored</h2>
<p>Account and app data are stored using <strong>Google Firebase</strong> (Google Cloud) on our
behalf. Google processes this data as our service provider under its own security and privacy terms
(<a href="https://firebase.google.com/support/privacy">firebase.google.com/support/privacy</a>).
We do not sell your personal information.</p>

<h2>How we use your data</h2>
<p>We use it only to provide the app&rsquo;s features &mdash; authenticating you, saving and syncing
your content, enabling features you turn on, and keeping the service secure. We do not use your
content for advertising.</p>

<h2>Deleting your account and data</h2>
<p>You can request deletion of your account and associated data at any time by emailing
<a href="mailto:{CONFIG['email']}">{CONFIG['email']}</a>{account_delete_note(app)}. We will delete
your data within a reasonable period, except where we must retain limited records to comply with
law.</p>

<h2>Children's privacy</h2>
<p>The app is not directed at children under 13, and we do not knowingly collect personal
information from children. If you believe a child has provided us information, contact us and we
will delete it.</p>
"""
    else:
        sections = "<p>No policy defined for this category.</p>"

    # Apps that sync through the user's OWN iCloud account. Worth stating
    # plainly, because the "offline"/"iap" text otherwise says data stays on
    # the device -- which would understate that it reaches their other devices.
    if app.get("icloud"):
        sections += f"""
<h2>iCloud sync</h2>
<p>{name} can sync your progress between your own devices using Apple&rsquo;s iCloud. That data
travels through <strong>your</strong> Apple account, not through us &mdash; we operate no servers
and never receive it. Apple handles it under Apple&rsquo;s privacy policy. You can turn this off
in iOS Settings, and deleting the app removes its local copy.</p>
"""

    shared_tail = f"""
<h2>Your choices &amp; rights</h2>
<p>Depending on where you live, you may have rights to access, correct, or delete personal
information we hold about you. To make a request, email
<a href="mailto:{CONFIG['email']}">{CONFIG['email']}</a>.</p>

<h2>Changes to this policy</h2>
<p>We may update this policy from time to time. Material changes will be reflected here with a new
&ldquo;last updated&rdquo; date.</p>

<h2>Contact</h2>
<p>Questions about this policy? Email
<a href="mailto:{CONFIG['email']}">{CONFIG['email']}</a>.</p>
"""

    return f"""
<article class="doc">
<a class="back" href="../index.html">&larr; All apps</a>
<h1>Privacy Policy &mdash; {name}</h1>
<p class="updated">Last updated: {CONFIG['updated']}</p>
{intro}
{sections}
{shared_tail}
</article>
"""


def account_delete_note(app):
    # In-app deletion note placeholder; keep generic and safe.
    return ", or by using the in-app account-deletion option where available"


# ---------------------------------------------------------------------------
# Per-app support pages
#
# App Store Connect requires a Support URL per app, and Guideline 1.5 expects it
# to actually offer support. A shared "legal center" index technically carries a
# contact address but reads as a legal page, which a reviewer can reject. These
# pages are per-app so the URL a reviewer clicks is unambiguously about the app
# in front of them.
#
# Every FAQ entry below is gated on the same flags that drive the privacy page,
# so the two can never contradict each other -- do not add an entry that isn't
# grounded in what the app actually ships.
# ---------------------------------------------------------------------------
def support_body(app):
    name = html.escape(app["name"])
    email = CONFIG["email"]
    cat = app["category"]
    has_iap = app.get("iap") or cat == "iap"
    is_cloud = cat == "cloud"
    has_ads = cat == "ads"

    faqs = []

    faqs.append((
        "I found a bug, or something isn't working",
        f"Email <a href=\"mailto:{email}\">{email}</a> with your device model and "
        f"iOS version, and what you were doing when it happened. A screenshot helps "
        f"a lot. {name} is maintained by one developer, so replies usually arrive "
        f"within a few days."))

    faqs.append((
        "I have a feature request",
        f"Send it to <a href=\"mailto:{email}\">{email}</a>. Requests genuinely do "
        f"shape what gets built next."))

    if has_iap:
        faqs.append((
            "How do I restore a purchase?",
            "Purchases are tied to your Apple Account. Reinstalling the app or "
            "setting up a new device will not lose them &mdash; use the "
            "<em>Restore Purchases</em> option in the app. If a purchase still "
            f"doesn't appear, email <a href=\"mailto:{email}\">{email}</a>."))
        faqs.append((
            "How do I get a refund?",
            "Refunds are handled by Apple, not by us &mdash; we have no ability to "
            "issue one. Request one at "
            "<a href=\"https://reportaproblem.apple.com\">reportaproblem.apple.com</a>."))

    if is_cloud:
        faqs.append((
            "How do I delete my account and data?",
            f"Use the account-deletion option in the app, or email "
            f"<a href=\"mailto:{email}\">{email}</a> and we will delete it for you."))
    else:
        faqs.append((
            "Where is my data stored, and how do I delete it?",
            f"{name} stores your progress and settings on your device. Deleting "
            f"the app removes that data permanently &mdash; there is no server copy "
            f"we can restore it from, so it cannot be recovered afterwards."))

    if has_ads:
        faqs.append((
            "Can I limit ad personalization?",
            "Yes. iOS controls this system-wide under "
            "<em>Settings &rsaquo; Privacy &amp; Security &rsaquo; Tracking</em> and "
            "<em>Settings &rsaquo; Privacy &amp; Security &rsaquo; Apple Advertising</em>."))

    items = "\n".join(
        f"  <h3>{q}</h3>\n  <p>{a}</p>" for q, a in faqs)

    return f"""
<article class="policy">
<a class="back" href="../index.html">&larr; All apps</a>
<h1>Support &mdash; {name}</h1>
<p class="updated">Last updated: {CONFIG['updated']}</p>

<p>Questions, bugs, or feedback about {name}? Email
<a href="mailto:{email}">{email}</a> &mdash; that address is read by the developer
directly.</p>

<h2>Common questions</h2>
{items}

<h2>Privacy and terms</h2>
<p>See the <a href="../privacy/{app['slug']}.html">Privacy Policy for {name}</a>
and the <a href="../terms.html">Terms of Service</a>.</p>
</article>
"""


# ---------------------------------------------------------------------------
# Shared Terms of Service
# ---------------------------------------------------------------------------
def terms_body():
    dev = html.escape(CONFIG["developer"])
    email = CONFIG["email"]
    juris = html.escape(CONFIG["jurisdiction"])
    return f"""
<article class="doc">
<h1>Terms of Service</h1>
<p class="updated">Last updated: {CONFIG['updated']}</p>

<p class="lede">These Terms of Service (&ldquo;Terms&rdquo;) govern your use of the mobile
applications published by {dev} (&ldquo;we&rdquo;, &ldquo;us&rdquo;, the &ldquo;Apps&rdquo;).
By downloading or using any of our Apps, you agree to these Terms. If you do not agree, please do
not use the Apps.</p>

<h2>1. License</h2>
<p>We grant you a personal, limited, non-exclusive, non-transferable, revocable license to use our
Apps on Apple-branded devices you own or control, in accordance with the Apple App Store Terms of
Service and these Terms. We reserve all rights not expressly granted to you.</p>

<h2>2. Acceptable use</h2>
<p>You agree not to: (a) copy, modify, reverse-engineer, decompile, or attempt to extract the source
code of the Apps except as permitted by law; (b) use the Apps for any unlawful purpose; (c) interfere
with or disrupt the Apps or any servers or networks connected to them; or (d) resell or commercially
exploit the Apps without our permission.</p>

<h2>3. In-app purchases &amp; subscriptions</h2>
<p>Some Apps offer optional in-app purchases or subscriptions. All payments are processed by Apple
through the App Store and are subject to Apple&rsquo;s terms. Prices and availability may change.
Purchases are generally non-refundable except as required by law or Apple&rsquo;s policies; refund
requests are handled by Apple. Subscriptions, where offered, renew automatically unless canceled at
least 24 hours before the end of the current period, and can be managed in your Apple Account
settings.</p>

<h2>4. Advertising</h2>
<p>Some Apps are supported by third-party advertising. We are not responsible for the content of
third-party ads or the websites or offers they link to.</p>

<h2>5. User content</h2>
<p>Some Apps let you create or store content. You retain ownership of content you create. For any
App with sharing or social features, you grant us a limited license to store and display that
content solely to operate the feature you have enabled. You are responsible for the content you
create and share, and you agree not to post anything unlawful, infringing, or abusive.</p>

<h2>6. Not professional advice</h2>
<p>Several of our Apps cover educational topics including finance, economics, options and
derivatives, budgeting, health, and languages. All such content is provided for
<strong>general educational and entertainment purposes only</strong>. It is <strong>not</strong>
financial, investment, legal, medical, or other professional advice, and must not be relied on as
such. Always consult a qualified professional before making financial, health, or other important
decisions. You are solely responsible for decisions you make.</p>

<h2>7. Intellectual property</h2>
<p>The Apps, including their design, code, graphics, and content (excluding your own user content),
are owned by us and protected by intellectual-property laws. The App names and logos are our marks.</p>

<h2>8. Disclaimer of warranties</h2>
<p>The Apps are provided <strong>&ldquo;as is&rdquo; and &ldquo;as available&rdquo;</strong> without
warranties of any kind, whether express or implied, including fitness for a particular purpose,
merchantability, and non-infringement. We do not warrant that the Apps will be uninterrupted,
error-free, or secure.</p>

<h2>9. Limitation of liability</h2>
<p>To the maximum extent permitted by law, we will not be liable for any indirect, incidental,
special, consequential, or punitive damages, or any loss of data, profits, or goodwill, arising from
your use of the Apps. Our total liability for any claim relating to the Apps will not exceed the
amount you paid us for the App in question in the twelve months before the claim, or USD $50,
whichever is greater.</p>

<h2>10. Termination</h2>
<p>We may suspend or terminate your access to the Apps if you violate these Terms. You may stop using
the Apps at any time by deleting them.</p>

<h2>11. Apple App Store</h2>
<p>These Terms are between you and us only, not with Apple. Apple is not responsible for the Apps or
their content. Apple has no obligation to provide maintenance or support for the Apps. In the event
of any failure of an App to conform to any applicable warranty, you may notify Apple and Apple will
refund the purchase price (if any); to the maximum extent permitted by law, Apple has no other
warranty obligation. Apple is not responsible for addressing any claims relating to the Apps,
including product-liability, legal-compliance, or intellectual-property claims. Apple and its
subsidiaries are third-party beneficiaries of these Terms and may enforce them against you. You
represent that you are not located in a country subject to a U.S. Government embargo and are not on
any U.S. Government restricted-parties list.</p>

<h2>12. Changes to these Terms</h2>
<p>We may update these Terms from time to time. Continued use of the Apps after changes take effect
means you accept the updated Terms.</p>

<h2>13. Governing law</h2>
<p>These Terms are governed by the laws of {juris}, without regard to conflict-of-laws principles.</p>

<h2>14. Contact</h2>
<p>Questions about these Terms? Email <a href="mailto:{email}">{html.escape(email)}</a>.</p>
</article>
"""


# ---------------------------------------------------------------------------
# Landing page
# ---------------------------------------------------------------------------
def index_body():
    cards = []
    for app in sorted(APPS, key=lambda a: a["name"].lower()):
        cards.append(f"""
    <li class="app-card">
      <div class="app-info">
        <h3>{html.escape(app['name'])}</h3>
        <p>{html.escape(app['blurb'])}</p>
      </div>
      <div class="app-links">
        <a href="support/{app['slug']}.html">Support</a>
        <a href="privacy/{app['slug']}.html">Privacy Policy</a>
        <a href="terms.html">Terms</a>
      </div>
    </li>""")
    return f"""
<section class="intro">
  <h1>{html.escape(CONFIG['site_title'])}</h1>
  <p class="lede">Terms of Service and Privacy Policies for apps by
     {html.escape(CONFIG['developer'])}.</p>
</section>
<ul class="app-list">
{''.join(cards)}
</ul>
"""


# ---------------------------------------------------------------------------
# Stylesheet
# ---------------------------------------------------------------------------
CSS = """:root {
  --bg: #ffffff;
  --fg: #1c1c1e;
  --muted: #6b6b70;
  --accent: #0a6cff;
  --card: #f6f7f9;
  --border: #e4e6ea;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #131316;
    --fg: #ececef;
    --muted: #9a9aa2;
    --accent: #4d9bff;
    --card: #1d1d21;
    --border: #2c2c31;
  }
}
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  background: var(--bg);
  color: var(--fg);
  line-height: 1.6;
}
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }

.site-header {
  display: flex; align-items: center; justify-content: space-between;
  flex-wrap: wrap; gap: .5rem;
  max-width: 780px; margin: 0 auto; padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--border);
}
.brand { font-weight: 700; font-size: 1.05rem; color: var(--fg); }
.site-header nav a { margin-left: 1rem; color: var(--muted); font-size: .95rem; }

main { max-width: 780px; margin: 0 auto; padding: 1.5rem 1.25rem 3rem; }

h1 { font-size: 1.9rem; line-height: 1.2; margin: .2rem 0 .4rem; }
h2 { font-size: 1.2rem; margin: 2rem 0 .5rem; }
h3 { margin: 0 0 .25rem; }
.lede { font-size: 1.08rem; color: var(--muted); }
.updated { color: var(--muted); font-size: .9rem; margin-top: 0; }
.doc p, .doc li { font-size: 1rem; }
.doc ul { padding-left: 1.2rem; }
.back { display: inline-block; margin-bottom: 1rem; font-size: .95rem; }

.intro { margin-bottom: 1.5rem; }
.app-list { list-style: none; margin: 0; padding: 0; display: grid; gap: .75rem; }
.app-card {
  display: flex; align-items: center; justify-content: space-between;
  flex-wrap: wrap; gap: .75rem;
  background: var(--card); border: 1px solid var(--border);
  border-radius: 14px; padding: 1rem 1.15rem;
}
.app-info h3 { font-size: 1.1rem; }
.app-info p { margin: 0; color: var(--muted); font-size: .95rem; }
.app-links { display: flex; gap: 1rem; flex-shrink: 0; }
.app-links a { font-size: .92rem; font-weight: 600; }

.site-footer {
  max-width: 780px; margin: 0 auto; padding: 1.5rem 1.25rem 2.5rem;
  border-top: 1px solid var(--border); color: var(--muted); font-size: .88rem;
}
.site-footer p { margin: .25rem 0; }
"""


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def main():
    here = os.path.dirname(os.path.abspath(__file__))
    docs = os.path.join(here, "docs")
    priv = os.path.join(docs, "privacy")
    supp = os.path.join(docs, "support")
    os.makedirs(priv, exist_ok=True)
    os.makedirs(supp, exist_ok=True)

    # style
    with open(os.path.join(docs, "style.css"), "w", encoding="utf-8") as f:
        f.write(CSS)

    # index
    with open(os.path.join(docs, "index.html"), "w", encoding="utf-8") as f:
        f.write(page(CONFIG["site_title"],
                     f"Terms of Service and Privacy Policies for apps by {CONFIG['developer']}.",
                     index_body(), depth=0))

    # terms
    with open(os.path.join(docs, "terms.html"), "w", encoding="utf-8") as f:
        f.write(page(f"Terms of Service — {CONFIG['site_title']}",
                     "Terms of Service governing use of the apps.",
                     terms_body(), depth=0))

    # privacy per app
    for app in APPS:
        with open(os.path.join(priv, f"{app['slug']}.html"), "w", encoding="utf-8") as f:
            f.write(page(f"Privacy Policy — {app['name']}",
                         f"Privacy Policy for {app['name']}.",
                         privacy_body(app), depth=1))

    # support per app
    for app in APPS:
        with open(os.path.join(supp, f"{app['slug']}.html"), "w", encoding="utf-8") as f:
            f.write(page(f"Support — {app['name']}",
                         f"Support and contact information for {app['name']}.",
                         support_body(app), depth=1))

    print(f"Generated {len(APPS)} privacy + {len(APPS)} support pages "
          f"+ index + terms into {docs}")


if __name__ == "__main__":
    main()
