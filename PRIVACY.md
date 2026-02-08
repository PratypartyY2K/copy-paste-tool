Security & Privacy

Defaults:

- secret-safe mode: ON by default. The app will avoid persisting likely secrets (JWTs / long base64 tokens). If secret-safe mode is enabled, detected tokens are stored temporarily and auto-deleted after a short window.
- persistence: OFF by default. Users must opt in through Settings to enable persistent storage to disk.
- common sensitive apps are pre-blocklisted (1Password, LastPass, Bitwarden, Keychain, etc.) and will not be captured while secret-safe mode is enabled.

Privacy tips:

- The app does not transmit clipboard contents anywhere. Persistence writes are local-only.
- If you grant Accessibility permissions (macOS), the app can better attribute clipboard events to the source app; this requires macOS Privacy settings > Accessibility.
- To completely avoid any storage, keep persistence disabled and secret-safe enabled in Settings.

I keep Secret-safe mode on by default, and persistence off by default. You can enable persistence and edit the blocklist in Settings.

Last updated: 2026-02-07
