import scrapy
from urllib.parse import urlencode
from datetime import datetime, timezone


class RedditSearchSpider(scrapy.Spider):
    """
    Scrape Reddit search results from the public JSON endpoint without API keys.
    RAG-ready: includes selftext + optional top comments, and a combined doc_text field.
    """

    name = "reddit_search"

    custom_settings = {
        "ROBOTSTXT_OBEY": False,
        "DOWNLOAD_DELAY": 1.25,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        "RETRY_TIMES": 6,
        "COOKIES_ENABLED": False,
        "LOG_LEVEL": "INFO",

        # Helpful when Reddit gets picky
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 1.0,
        "AUTOTHROTTLE_MAX_DELAY": 10.0,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 1.0,

        "USER_AGENT": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),

        "FEED_EXPORT_FIELDS": [
            # identity / query
            "query",
            "subreddit",
            "rank",
            "post_id",
            "permalink",
            "post_url",

            # content
            "title",
            "selftext",
            "top_comments",

            # RAG helper: one text blob to embed
            "doc_text",

            # ranking / metadata
            "score",
            "upvote_ratio",
            "num_comments",
            "created_utc",
            "created_iso",
            "author",
            "is_self",
            "over_18",
            "link_flair_text",
        ],
    }

    def __init__(
        self,
        query=None,
        subreddits=None,
        limit=100,
        sort="new",
        t="all",
        include_comments="1",
        max_comments=10,
        min_score=0,
        min_comments=0,
        **kwargs,
    ):
        super().__init__(**kwargs)

        if not query:
            raise ValueError("Missing required -a query='...'")

        if not subreddits:
            self.subreddits = ["UCSantaBarbara", "SantaBarbara"]
        else:
            self.subreddits = [s.strip() for s in subreddits.split(",") if s.strip()]

        self.query = query
        self.sort = sort
        self.t = t

        try:
            self.limit = max(1, int(limit))
        except Exception:
            self.limit = 100

        self.page_size = 100
        self.count_by_sub = {sub: 0 for sub in self.subreddits}
        self.seen_ids_by_sub = {sub: set() for sub in self.subreddits}

        # RAG-focused controls
        self.include_comments = str(include_comments).strip() not in ("0", "false", "False", "")
        try:
            self.max_comments = max(0, int(max_comments))
        except Exception:
            self.max_comments = 10

        try:
            self.min_score = int(min_score)
        except Exception:
            self.min_score = 0

        try:
            self.min_comments = int(min_comments)
        except Exception:
            self.min_comments = 0

    def start_requests(self):
        for sub in self.subreddits:
            req = self._make_request(subreddit=sub, after=None)
            if req:
                yield req

    def _make_request(self, subreddit: str, after: str | None):
        remaining = self.limit - self.count_by_sub[subreddit]
        if remaining <= 0:
            return None

        size = min(self.page_size, remaining)

        params = {
            "q": self.query,
            "restrict_sr": 1,
            "sort": self.sort,   # relevance, new, top, comments
            "t": self.t,         # hour, day, week, month, year, all (matters for top)
            "limit": size,
            "raw_json": 1,
        }
        if after:
            params["after"] = after

        url = f"https://www.reddit.com/r/{subreddit}/search.json?{urlencode(params)}"

        return scrapy.Request(
            url,
            callback=self.parse_search,
            headers={"Accept": "application/json,text/plain,*/*"},
            meta={"subreddit": subreddit},
        )

    def parse_search(self, response):
        # self.logger.info(f"URL: {response.url}")
        # self.logger.info(f"Status: {response.status}")
        # self.logger.info(f"CT: {response.headers.get('Content-Type')}")
        # self.logger.info(response.text[:300])
        subreddit = response.meta["subreddit"]

        # quick block/rate-limit detection
        ct = (response.headers.get("Content-Type") or b"").decode("utf-8", errors="ignore").lower()
        if response.status in (401, 403, 429) or "application/json" not in ct:
            self.logger.warning(
                f"Possible block/ratelimit: status={response.status}, content-type={ct}. "
                "Try increasing DOWNLOAD_DELAY / AUTOTHROTTLE_MAX_DELAY."
            )
            return

        try:
            data = response.json()
        except Exception:
            self.logger.warning("Non-JSON response (possible block/rate-limit).")
            return

        payload = data.get("data") or {}
        children = payload.get("children") or []
        after = payload.get("after")

        for child in children:
            post = child.get("data") or {}

            post_id = post.get("id") or ""
            if not post_id:
                continue

            # dedupe
            if post_id in self.seen_ids_by_sub[subreddit]:
                continue
            self.seen_ids_by_sub[subreddit].add(post_id)

            # basic safety + low-signal filters (tweak as needed)
            over_18 = bool(post.get("over_18"))
            if over_18:
                continue

            score = post.get("score") or 0
            num_comments = post.get("num_comments") or 0

            if score < self.min_score and num_comments < self.min_comments:
                # keep only if it has at least some engagement (unless you set mins to 0)
                continue

            if self.count_by_sub[subreddit] >= self.limit:
                break

            self.count_by_sub[subreddit] += 1
            rank = self.count_by_sub[subreddit]

            created_utc = post.get("created_utc")
            created_iso = ""
            if created_utc:
                try:
                    created_iso = datetime.fromtimestamp(float(created_utc), tz=timezone.utc).isoformat()
                except Exception:
                    created_iso = ""

            permalink = post.get("permalink") or ""
            full_permalink = f"https://www.reddit.com{permalink}" if permalink else ""

            title = post.get("title") or ""
            selftext = post.get("selftext") or ""
            author = post.get("author") or ""
            link_flair_text = post.get("link_flair_text") or ""

            base_item = {
                "query": self.query,
                "subreddit": subreddit,
                "rank": rank,
                "post_id": post_id,
                "permalink": full_permalink,
                "post_url": post.get("url") or "",
                "title": title,
                "selftext": selftext,
                "top_comments": "",

                # ranking/meta
                "score": score,
                "upvote_ratio": post.get("upvote_ratio"),
                "num_comments": num_comments,
                "created_utc": created_utc,
                "created_iso": created_iso,
                "author": author,
                "is_self": post.get("is_self"),
                "over_18": over_18,
                "link_flair_text": link_flair_text,
            }

            # Build a single RAG text blob (what you'll embed)
            # Keep it structured so the model can cite/attribute.
            doc_text = self._build_doc_text(base_item, comments_text="")
            base_item["doc_text"] = doc_text

            # Optionally fetch comments for richer RAG chunks
            if self.include_comments and full_permalink and self.max_comments > 0:
                comments_url = f"{full_permalink}.json?raw_json=1&limit=50"
                yield scrapy.Request(
                    comments_url,
                    callback=self.parse_comments,
                    headers={"Accept": "application/json,text/plain,*/*"},
                    meta={"item": base_item},
                )
            else:
                yield base_item

        if after and self.count_by_sub[subreddit] < self.limit:
            req = self._make_request(subreddit=subreddit, after=after)
            if req:
                yield req

    def parse_comments(self, response):
        item = response.meta["item"]

        ct = (response.headers.get("Content-Type") or b"").decode("utf-8", errors="ignore").lower()
        if response.status in (401, 403, 429) or "application/json" not in ct:
            # return the post without comments rather than dropping it
            yield item
            return

        try:
            data = response.json()
        except Exception:
            yield item
            return

        # Reddit comments endpoint returns a list: [post_listing, comments_listing]
        if not isinstance(data, list) or len(data) < 2:
            yield item
            return

        comments_listing = data[1] or {}
        comments = ((comments_listing.get("data") or {}).get("children") or [])

        top = []
        for c in comments:
            if len(top) >= self.max_comments:
                break
            if (c.get("kind") != "t1"):
                continue
            cd = c.get("data") or {}
            body = (cd.get("body") or "").strip()
            if not body:
                continue
            if body in ("[deleted]", "[removed]"):
                continue

            score = cd.get("score")
            author = cd.get("author") or ""
            top.append(f"- ({score}) {author}: {body}")

        comments_text = "\n".join(top).strip()
        item["top_comments"] = comments_text

        # rebuild doc_text including comments
        item["doc_text"] = self._build_doc_text(item, comments_text=comments_text)

        yield item

    def _build_doc_text(self, item: dict, comments_text: str):
        parts = []
        parts.append(f"Source: Reddit r/{item.get('subreddit','')}")
        parts.append(f"Query: {item.get('query','')}")
        parts.append(f"Title: {item.get('title','')}".strip())

        flair = item.get("link_flair_text") or ""
        if flair:
            parts.append(f"Flair: {flair}")

        selftext = (item.get("selftext") or "").strip()
        if selftext:
            parts.append("Post:")
            parts.append(selftext)

        if comments_text:
            parts.append("Top comments:")
            parts.append(comments_text)

        # Helpful metadata to keep in the embedded text
        created = item.get("created_iso") or ""
        if created:
            parts.append(f"Created: {created}")
        parts.append(f"Score: {item.get('score')}, Comments: {item.get('num_comments')}")

        return "\n".join(parts).strip()
