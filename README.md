# build-config.json template
```json
{
    "parent-dir": ".",
    "vars": [
        {
            "replaceFrom": "key",
            "replaceWith": "value"
        }
    ],
    "pages": [
        "/test.html",
        {
            "path": "/index.html",
            "prefetches": ["https://example.com/resource.txt", "..."]
        }
    ],
    "line-end": "\n"
}

```