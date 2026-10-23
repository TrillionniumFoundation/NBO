# Publication transport attempts

These are publication transport events, not economic experiments or changes to the scientific evidence.

On 23 October 2026, before the separate 512-bin independent follow-up was published or executed:

1. The 4,564,717-byte original primary record gzip was uploaded successfully as Git blob `7150091631c6dca77dfa00bc03e888867a7bceb2`.
2. The original independent checks and action evaluations were uploaded successfully as blobs `be9fb738a5a8b6a2e78d24f79de6aec2f806294e` and `a95b33cb6ac4fc2c6742fb0248aba79ea4d0d6a5`.
3. A local chunk-read attempt was interrupted by a temporarily unavailable execution environment. No follow-up evaluation ran and no branch reference changed.
4. Two subsequent attempts to upload the original 13,869,944-byte independent terminal-witness gzip were rejected by the connector's HTTP request-size limit: base64 encoding exceeds its 16 MiB request-body maximum. The reported failure was `HTTP 400: MCP request body is invalid or exceeds the 16 MiB limit`.
5. The follow-up freeze was therefore prepared with transport-only binary parts and an exact byte/hash materializer. The original witness gzip is unchanged; its SHA-256 is `2d89295e6591c23db04292a68a6466e11aaa727a8be0f9aadb1a456c00e02304`. This transport change precedes the follow-up's publication and economic execution. It changes no primary, timing, or original independent result, and no original F125 frozen scientific file.

The final addendum manifest and remote-readback receipt, rather than these failed transport attempts, determine the follow-up's actual source boundary.
