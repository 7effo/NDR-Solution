# Security Dashboards

This directory contains OpenSearch Dashboards export files (`.ndjson`) that can be imported to visualize security data.

## How to Import

The `../scripts/dashboard_setup.sh` script will automatically import any `.ndjson` files found in this directory.

## Creating New Dashboards

1. Log in to OpenSearch Dashboards.
2. Create visualizations and dashboards.
3. Go to **Management > Stack Management > Saved Objects**.
4. Select your dashboard and related objects.
5. Click **Export**.
6. Save the `.ndjson` file to this directory.
7. Run `../scripts/dashboard_setup.sh` to re-import or share with other deployments.

## Default Index Patterns

The setup script automatically creates the following index patterns:

- `zeek-*`
- `suricata-*`
- `alerts-*`
