# Moodle CLI cron on DirectAdmin

**Status: confirmed cron execution; custom certificate plugin warning unresolved.** The host was configured to invoke Moodle's `admin/cli/cron.php` each minute. Original environment used `/usr/local/php81/bin/php81`, which is server-specific; choose the PHP version supported by your current Moodle release.

## What worked
A new cron job was configured without overwriting two preexisting jobs. Multiple CLI log runs showed `Cron run completed correctly`. The `customcert` component logged `Invalid get_string() identifier: 'taskissuecertificate'`, then later showed the `mod_customcert\task\issue_certificates_task` scheduled task running/completing. A scheduled task completing does not guarantee the plugin's language string or certificate issuance is correct.

## Deployment runbook
1. Record the account's current crontab in **private** controlled storage.
2. Determine actual PHP CLI, Moodle root, correct restricted run-as user and existing cron entries.
3. Schedule the CLI cron for every minute. Never run as root in shared hosting.
4. Redirect output to an owner-readable log and configure rotation.
5. Review log completion markers plus Moodle Admin > Server > Tasks > Scheduled tasks.
6. Ask the LMS provider to investigate customcert language strings and plugin compatibility separately.

Example (placeholders must be replaced):
```cron
* * * * * /usr/local/php81/bin/php81 /home/ACCOUNT/domains/EXAMPLE_DOMAIN/public_html/admin/cli/cron.php >> /home/ACCOUNT/moodle-cron-cli.log 2>&1
```

## Read-only check
```bash
MOODLE_ROOT="$HOME/domains/EXAMPLE_DOMAIN/public_html" PHP_BIN=/usr/local/php81/bin/php81 LOG_FILE="$HOME/moodle-cron-cli.log" bash scripts/check-moodle-cron.sh
```

## Safety
Do not publish LMS student data, web roots, user names, full configuration exports or cron logs. Use [Moodle CLI guidance](https://docs.moodle.org/en/Administration_via_command_line) and [scheduled task guidance](https://docs.moodle.org/en/Scheduled_tasks) to confirm appropriate versions.

## Repository scope and operating boundaries

This standalone project separates the historical incident outcome from the
diagnostic tooling. The script collects a narrow set of checks; it does not
automatically perform the manual recovery steps described above. Start with a
nonproduction test and capture a baseline before proposing a configuration
change. Use the least-privileged approved identity and preserve rollback values
in private change records. Stop when required inputs or authorization are missing.

## Evidence and acceptance record

For any new investigation, record the product/runtime versions, UTC observation
time, expected behavior, actual result, exact approved change, rollback owner,
and follow-up observation window in private storage. Publish only a redacted
summary. Mark hypotheses as hypotheses. A successful diagnostic command or green
CI run does not prove the business workflow works. Keep unresolved acceptance
items open until an authorized tester verifies the end-user result.

## Quality, security and licensing

- [Tests and limitations](TESTING.md): syntax, hygiene and isolated regressions.
- [Security guidance](SECURITY.md): safe execution and evidence handling.
- [Source and rights](PROVENANCE.md) and [MIT license](LICENSE).
- [CI runs](https://github.com/IAmLegionVaal/Moodle-DirectAdmin-CLI-Cron/actions/workflows/validate.yml).
- [Central incident index](https://github.com/IAmLegionVaal/IT-Support-Toolkit-Launcher/blob/main/incident-projects/README.md).
- [Publication and follow-up tracker](https://github.com/IAmLegionVaal/IT-Support-Toolkit-Launcher/issues/1).

Contributions should include synthetic regression coverage and an explicit
statement of what was actually tested. Do not attach raw client evidence to
issues or pull requests. Preserve the historical status unless new evidence
supports a change.
