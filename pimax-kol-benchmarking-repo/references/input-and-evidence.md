# Inputs and evidence

## Minimum viable input

- partner identity and channel;
- analysis period;
- order export with order date, stable order ID, status, currency, and `Order Subtotal`;
- public channel or site URL;
- known Pimax price, promotion, launch, event, and paid-media timeline.

Proceed with public data when backend data is unavailable, but label exposure conclusions as estimates or unknown. Ask for missing data only when it would change the decision; otherwise state the limitation and continue.

## Recommended fields

### Orders

`Order Date`, `Order Number`, `Order Status`, `Order Subtotal`, `Currency`, `Discount codes`, `New Customer ?`, `Conversion Source`, `SUB ID`, `Affiliate Source`, country, UTM fields, order/referral IDs, refund/cancellation status.

Default rules:

- Use approved unique orders for the primary view.
- Use `Order Subtotal` for sales value unless the user specifies another field.
- Report missing dates, values, IDs, currencies, and duplicate order IDs before analysis.
- Show product-price matches as `high`, `medium`, or `low` confidence with the applicable price period.

### Commercial context

Price book, bundle history, preorder deposits, coupon rules, inventory, launch calendar, expos, seasonal campaigns, EDM, paid ads, product availability by market, and major site changes.

### YouTube evidence

Public: title, URL, publish date, duration, views, likes, comments, description, chapters, links, pinned/creator comments, follow-up videos, Shorts/posts, external landing pages, community or Discord references.

Backend when available: impressions, CTR, traffic sources, unique viewers, average view duration, retention curve, geography, returning viewers, end-screen clicks, link clicks, and revenue/affiliate clicks by video.

### Blog evidence

Public: URL, title/H1, publish and modified dates, topic/intent, product and non-brand terms, headings, structured data, comparison tables, internal/external links, author, CTA, and indexability signals.

Backend when available: GSC query/page impressions, clicks, CTR, position, country/device; GA landing sessions, engagement, outbound/product clicks, assisted conversions; affiliate clicks by page.

Third-party SEO tools can suggest visibility, backlinks, estimated traffic, and keyword candidates. Label them as estimates, record the tool/date, and never substitute them for GSC.

## Evidence ledger

Maintain one row per claim:

| Claim | Observation | Source/link | Time | Alternative explanation | Confidence | Missing evidence |
|---|---|---|---|---|---|---|

Confidence labels:

- **Fact:** directly observed in primary data or page.
- **Strong association:** aligned stage movement plus supporting mechanism, with major confounders checked.
- **Plausible contribution:** timing and mechanism fit, but material confounders or data gaps remain.
- **Hypothesis:** worth testing; current evidence is insufficient.
- **Unknown:** required source is unavailable or conflicting.

Do not upgrade confidence merely because several public observations repeat the same unverified claim.

## Stage construction

1. Calculate full-period and monthly baselines.
2. Identify sustained changes in orders/day, subtotal/day, AOV, new-customer share, and price mix.
3. Propose stage boundaries around business changes, not arbitrary equal dates.
4. Check whether the boundary is also a price, launch, campaign, tracking, or availability change.
5. Inspect the 2–4 weeks before the stage boundary for content and operational actions.
6. For candidate actions, compare 7/14/21/30-day pre/post windows using aligned day counts.
7. Retain both the commercial stage and the content cohort; do not collapse them into one date.

For low-volume partners, prefer wider windows and directional language. A single-day lift is an example to investigate, not a phase by itself.
