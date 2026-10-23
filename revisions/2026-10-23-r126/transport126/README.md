# Immutable byte transport for the R126 author package

Some canonical files exceed the publication connector's JSON request size. This transport divides those **unchanged bytes** into ordered parts no larger than 8 MiB. Base64 expansion of an individual part remains below the connector's 16 MiB JSON-request limit. This is a publication mechanism, not a new scientific experiment, compression choice, model, sample or retimed result.

`../DATA_TRANSPORT126.json` binds the canonical data path, byte count, SHA256, computed Git blob identity, and the ordered parts under `parts/data/`. The scientific file remains `results126c/primary01/records126c.jsonl.gz`; its original 17,758,865 bytes have SHA256 `026c9281696ead25a524046cecdb15366a26208cf66bcf2e3a1b11271ad8e2a5` and Git blob identity `1a334aade35280e7afe76c7b5a5440bf558f5094`.

## Restore data from a repository checkout

Run from `revisions/2026-10-23-r126/`, using a new receipt directory:

```bash
python transport126/restore126.py --output replication126/transport-check
```

`--data` is an accepted explicit spelling of the default behavior. The index and parts are located relative to the script's revision directory. If the canonical file already exists, the script verifies its full byte count, SHA256 and Git blob identity and retains it **without requiring any parts**. This is the normal case for the extracted canonical referee archive, which contains the original scientific data and omits the redundant data fragments.

If the canonical file is absent, every part is verified and reassembled into a private temporary file in the destination directory. The complete byte count, SHA256 and Git blob identity are checked before an atomic hard-link publication creates the canonical name. An unequal existing file is never overwritten. A racing existing file must itself match. Only the private assembly file is removed. Failed attempts have their own `START126.json` and `EXECUTION126.json`; a refusal is not reported as a successful restoration.

`--destination-root <directory>` permits a separate destination layout for verification. It does not change the location from which indexes and fragments are read. No network, Git mutation, fitting, economics or scientific calculation occurs.

## Restore the separately transported compressed release container

After the final archive has been created, `release126/ARCHIVE_TRANSPORT126.json` binds its canonical path and fragments under `release126/parts/`. These transport files are outside the canonical archive, avoiding a self-inclusion cycle.

```bash
python transport126/restore126.py --archive --output replication126/transport-with-archive
```

This restores default data and additionally requires the archive transport index. A missing archive index is an error only with `--archive`. A checkout that receives only fragments can therefore reconstruct both the unchanged data file and the exact release container. An extracted archive does not need to contain or reconstruct its own compressed container; use the default command there.

## Create transport indexes and parts

The publication maintainer can generate the data transport with:

```bash
python transport126/make_transport126.py --output transport126/attempts/data-make01
```

Only after the final canonical archive has been assembled and verified:

```bash
python transport126/make_transport126.py --archive --output release126/archive-make01
```

The archive flag on the **maker** creates only archive parts. Its post-assembly attempt receipt is placed under `release126/` so it cannot become a new canonical-package member after the archive has been assembled. Existing equal parts/indexes are retained. Unequal parts or indexes cause a recorded refusal instead of an overwrite. Original source bytes are checked before and after fragmentation; the ordered parts are also hashed as the entire original file. Canonical package assembly includes the data index and restoration utilities, but excludes `transport126/parts/` and all `release126/` transport content.

## Index schema and actual validation

Both indexes use schema `nbo-r126-immutable-byte-transport-v1`, a `kind` of `data` or `archive`, and `max_part_bytes: 8388608`. Each `files` entry has `path`, `bytes`, `sha256`, `git_blob`, and `parts`. Each part has a one-based `index`, zero-based byte `offset`, revision-relative `path`, `bytes`, `sha256`, and `git_blob`. Parts must form a contiguous ordered cover of the canonical file. Git blob identities are SHA1 of the standard `blob <length>\0` header followed by the exact bytes; no Git database is needed to compute them.

`VALIDATION126.json` records the actual tests and source/index hashes. The data restoration was tested in a fresh external temporary directory, then with the canonical file present and all part files absent. Additional expected-failure tests require an unequal canonical file to remain unchanged and a corrupt fragment to produce no canonical output. Only generated temporary duplicates are removed; original scientific data and every publication attempt remain preserved.
