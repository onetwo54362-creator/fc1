# Facebook Comments Scraper

A robust, high-performance Apify Actor for scraping comments and replies from Facebook posts. This scraper uses Facebook's internal GraphQL API to fetch comments quickly and reliably, bypassing UI changes and avoiding heavy browser automation overhead.

## Features

- **Blazing Fast**: Uses raw GraphQL requests instead of browser automation (Puppeteer/Playwright).
- **Deep Threading**: Extracts top-level comments and all nested replies (threading).
- **Reaction Breakdown**: Extracts detailed reaction counts (👍 Like, ❤️ Love, 😂 Haha, 😮 Wow, 😢 Sad, 😠 Angry, 🤗 Care) for every comment and reply.
- **Media Extraction**: Automatically extracts attachments like photos, videos, GIFs, and stickers from comments, providing the media type and a direct URL to the media.
- **Excel Export**: Generates a clean, nicely formatted Excel (`.xlsx`) file with clickable URLs and visually grouped threaded replies.
- **Dataset Export**: Outputs flat JSON to the Apify Dataset for easy API integration.

## Input Configuration

The scraper requires the following inputs:

| Field | Type | Description |
|---|---|---|
| `postUrls` | Array of Strings | (Required) A list of Facebook post URLs to scrape. |
| `cookies` | String | (Required) Your Facebook session cookies to authenticate the requests. |
| `fbDtsg` | String | (Optional) The `fb_dtsg` token. If left blank, the scraper will attempt to auto-fetch it. |
| `maxComments` | Integer | Maximum number of top-level comments to scrape per post. Leave as `0` for no limit. |
| `includeReplies` | Boolean | Whether to fetch replies to comments. Default is `true`. |
| `excelExport` | Boolean | Whether to generate and save an Excel (`.xlsx`) file to the Key-Value Store. Default is `true`. |
| `minBatchSize` / `maxBatchSize` | Integer | Pagination controls to determine how many items to fetch per request. |
| `minCooldownSeconds` / `maxCooldownSeconds` | Integer | Random delay ranges between GraphQL requests to avoid rate limits. |

### How to get your Cookies

1. Log into your Facebook account in your desktop browser.
2. Use a browser extension like [EditThisCookie](https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg) or [Cookie-Editor](https://cookie-editor.com/).
3. Export your cookies in **JSON format** or **Netscape format**.
4. Paste the entire string into the `cookies` input field.
*Note: Make sure your cookie string contains the `c_user` and `xs` cookies.*

## Output Data Structure

The scraper outputs flat JSON objects to the Apify Dataset. The structure of each item is:

```json
{
  "post_url": "https://www.facebook.com/...",
  "post_author_name": "Author Name",
  "post_text": "Post caption...",
  "comment_number": "#1.1",
  "type": "↳ Reply",
  "comment_id": "123456789",
  "post_id": "987654321",
  "author_name": "Commenter Name",
  "author_url": "https://www.facebook.com/commenter",
  "text": "This is a comment!",
  "media_type": "photo",
  "media_url": "https://scontent.fmnl...fbcdn.net/v/...",
  "reaction_count": 5,
  "reactions_like": 4,
  "reactions_love": 1,
  "reactions_haha": 0,
  "reactions_wow": 0,
  "reactions_sad": 0,
  "reactions_angry": 0,
  "reactions_care": 0,
  "reply_count": 0,
  "is_reply": true,
  "parent_comment_id": "123456780",
  "scraped_at": "2026-06-03T12:00:00.000+00:00"
}
```

*Note: If a field doesn't have data (e.g., a text-only comment), fields like `media_type` and `media_url` will default to `"No media type"` and `"No media URL"`.*

## Limitations
- **Private Groups/Profiles**: The scraper can only access posts that your provided account (via cookies) has permission to see.
- **Rate Limits**: Scraping too fast can result in Facebook temporarily blocking your account. Use sensible cooldown values and a proxy if scraping in bulk.
