# Bun Installation Workaround for Hermes VM

## Problem

The Hermes Agent terminal VM may have **no direct internet access to GitHub**
(raw.githubusercontent.com, github.com both unreachable via curl/git), but
the **npm registry works** (registry.npmjs.org is reachable).

The official bun install script (`curl -fsSL https://bun.sh/install | bash`)
fails because it downloads the binary from GitHub Releases.

## Solution: npm-based installation

```bash
# Step 1: Install the bun npm wrapper (pulls @oven/bun-darwin-aarch64 as optional dep)
npm install -g bun

# Step 2: The postinstall may fail due to rename errors with @oven/bun-*.
# Install the platform-specific binary package directly:
npm install -g @oven/bun-darwin-aarch64   # Apple Silicon Mac
# OR for other platforms:
# npm install -g @oven/bun-darwin-x64     # Intel Mac
# npm install -g @oven/bun-linux-x64      # Linux x64

# Step 3: Create symlink
BUN_BIN=$(npm root -g)/@oven/bun-darwin-aarch64/bin/bun
mkdir -p ~/.bun/bin
ln -sf "$BUN_BIN" ~/.bun/bin/bun
export PATH="$HOME/.bun/bin:$PATH"

# Step 4: Verify
bun --version
```

## Verification

```bash
bun --version                        # Should print version (e.g. 1.3.14)
export PATH="$HOME/.bun/bin:$PATH"
which bun                            # Should show ~/.bun/bin/bun
```

## Why This Works

The `bun` npm package (v1.3.14+) bundles the real Bun binary inside
`@oven/bun-{platform}` optional dependencies hosted on npm's CDN, not
GitHub. npm's registry is typically reachable even when GitHub is blocked
in restricted VM environments.

## Known Issues

- The `postinstall` script in the `bun` npm package may fail with `ENOENT`
  during rename operations. This is harmless if the `@oven/bun-*` binary
  package was installed separately.
- `npm install -g bun` alone usually doesn't produce a working `bun` command
  because the postinstall script fails silently. Always install the
  platform-specific `@oven/bun-*` package explicitly.
