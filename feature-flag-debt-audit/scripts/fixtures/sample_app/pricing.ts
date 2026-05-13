export function priceMode(flags: Record<string, boolean>) {
  if (flags["pricing_migration_guard"]) {
    return "dual-write";
  }
  return "single-write";
}
