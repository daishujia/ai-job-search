---
name: nas-storage
description: Report home NAS capacity and what is using space, browse its folders, and review the omics dataset catalog (CATALOG.tsv / PROVENANCE.md). Use for "how full is my NAS", "what's taking space", "what datasets do I have on the NAS", "where did X get saved", or before planning a large download.
---

# nas-storage

Read-only by default. Needs the `nas` MCP server.

- **Capacity.** Run `nas_storage_overview`. Report used and free space per volume, and flag anything
  above 80% (the tool marks it).
- **What's using space.** Run `nas_folder_usage(path)`, starting at the omics root and drilling into
  the largest children. On very large trees it stops after about 20 s; say that the numbers are partial.
- **Browse.** `nas_list_folders(path, depth)`.
- **Dataset inventory.** Each verified download is a row in `CATALOG.tsv` under the omics root, with a
  `PROVENANCE.md` (source, version, licence or DUA reference, checksum result) in its folder.
  `nas_list_jobs` shows recent and in-flight downloads.
- **Before a big download.** Compare the plan's `total_bytes_known` against free space minus the
  reserve (default 5%), and warn early.
- **Never delete.** nas-mcp has no delete tool on purpose. If the user wants space back, list the
  candidate folders and sizes, and let them delete through the fnOS web UI.
