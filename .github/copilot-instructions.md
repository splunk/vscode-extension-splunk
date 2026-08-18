# Copilot Instructions: Semantic Rules Spec Review

This file guides Copilot cloud agent sessions that review `.spec` files against `resources/semantic_rules.json` after a spec pull. It covers two related but distinct tasks with different risk profiles.

## Project Structure

| Path                                   | Purpose                                                              |
| -------------------------------------- | -------------------------------------------------------------------- |
| `spec_files/<version>/`                | Official Splunk spec files (e.g., `spec_files/10.4/props.conf.spec`) |
| `package.json`                         | Extension manifest (includes `splunk.spec.FileVersion` enum)         |
| `resources/semantic_rules.json`        | Semantic linting rules                                               |
| `resources/semantic_rules.schema.json` | JSON schema for rules validation                                     |
| `out/semanticRules.js`                 | Rule evaluation engine                                               |
| `scripts/update-spec-files.js`         | Spec file automation script (also updates package.json)              |
| `scripts/validate-rule-ids.js`         | Rule ID uniqueness validator                                         |

## Automated Workflow

When the `update-spec-files.yaml` workflow runs, it automatically:

1. **Downloads new spec files** to `spec_files/<version>/`
2. **Updates `package.json`** - adds new versions to `splunk.spec.FileVersion` enum and sets the newest as default
3. **Runs deprecation analysis** and generates semantic rules
4. **Creates a PR** with all changes
5. **Creates a Copilot review issue** for manual review of semantic rules

The `package.json` update ensures users can immediately select new Splunk versions in VS Code settings after updating the extension.

## Task A: Coverage Gap Analysis (Low Risk)

**Goal:** Identify settings in `.spec` files with no corresponding trigger in `semantic_rules.json`.

### Steps

1. For each `.spec` file relevant to a conf file in `semantic_rules.json`, extract every setting name.

2. Extract every setting referenced in `semantic_rules.json` triggers (`settings`, `settings_regex`, `settings_equal`, `setting_exists`, `setting_missing`, `with_any`, `with_all`, `without`, `value_less_than`, `value_greater_than`, `value_not_equal`). For `with_any_prefix`/`without_prefix`, treat the prefix as covering any setting starting with it.

3. Report settings with zero references, grouped by conf file. Note whether settings are newly added (diff against previous spec version) vs. pre-existing uncovered.

4. **Do not propose a rule for every gap.** Only propose where the `.spec` prose describes a real behavioral consequence (performance cost, data loss, conflict with another setting, required companion). If silent on consequences, list as "uncovered, no rule proposed".

## Task B: Deprecation Detection (Medium Risk)

**Goal:** Find settings marked deprecated in `.spec` comments and create `warning`-severity rules.

### Steps

1. Scan `.spec` comments for deprecation language: `DEPRECATED`, `deprecated in`, `no longer has any effect`, `use X instead`.

2. For each deprecated setting, determine:
   - The exact deprecated setting name
   - Replacement setting (only if explicitly stated - do not guess)
   - Version deprecated as of

3. Check if the setting appears in multiple conf files and add rules to each relevant section.

4. Author rules using the pattern below.

## Trigger Primitives

| Primitive            | Type    | Description                                           |
| -------------------- | ------- | ----------------------------------------------------- |
| `stanza_pattern`     | regex   | Match stanza name                                     |
| `settings`           | object  | Exact key-value matches (case-insensitive by default) |
| `settings_regex`     | object  | Regex matches for values                              |
| `setting_exists`     | string  | Fire if setting present                               |
| `setting_missing`    | string  | Fire if setting absent                                |
| `with_any`           | array   | Fire if any setting exists                            |
| `with_all`           | array   | Fire if all settings exist                            |
| `without`            | array   | Suppress if any setting exists                        |
| `value_less_than`    | object  | Numeric comparison                                    |
| `value_greater_than` | object  | Numeric comparison                                    |
| `value_not_equal`    | object  | Exclude specific numeric values                       |
| `settings_equal`     | array   | Fire if all named settings have equal values          |
| `with_any_prefix`    | array   | Fire if any key starts with prefix                    |
| `without_prefix`     | array   | Suppress if any key starts with prefix                |
| `case_sensitive`     | boolean | Case-sensitive comparisons (default: false)           |

## Deprecation Rule Pattern

```json
{
  "id": "conffile_setting_name_deprecated",
  "trigger": {
    "setting_exists": "old_setting",
    "without": ["new_setting"]
  },
  "suggestion": {
    "severity": "warning",
    "title": "old_setting deprecated in Splunk X.Y+",
    "message": "old_setting is deprecated starting in Splunk X.Y. Add new_setting for forward compatibility.",
    "documentation": "https://docs.splunk.com/Documentation/Splunk/latest/Admin/Conffile.conf",
    "deprecated_in": "X.Y",
    "replacement": "new_setting"
  }
}
```

**Note:** Trigger shape is `setting_exists` on deprecated, `without` on replacement. If no replacement exists, drop the `without` clause and omit `replacement`.

## Rule ID Naming

- **Format:** `{conffile}_{setting_name}_{type}`
- **Examples:** `inputs_python_version_deprecated`, `props_extract_without_report`
- **Rule IDs must be globally unique** across all conf files
- Use snake_case, replace dots with underscores

## Verification (Required Before PR)

Run all checks and fix failures before opening a PR:

```bash
# 1. JSON validity (semantic rules)
node -e "require('./resources/semantic_rules.json'); console.log('✅ Valid JSON')"

# 2. JSON validity (package.json)
node -e "require('./package.json'); console.log('✅ Valid package.json')"

# 3. Schema conformance (if ajv installed)
npx ajv validate -s resources/semantic_rules.schema.json -d resources/semantic_rules.json

# 4. Rule ID uniqueness
node scripts/validate-rule-ids.js

# 5. Verify package.json FileVersion enum matches spec_files directories
node -e "const pkg = require('./package.json'); const fs = require('fs'); const dirs = fs.readdirSync('./spec_files').filter(d => /^\d+\.\d+$/.test(d)); const enum_ = pkg.contributes.configuration.properties['splunk.spec.FileVersion'].enum; const missing = dirs.filter(d => !enum_.includes(d)); if (missing.length) { console.error('Missing from enum:', missing); process.exit(1); } console.log('✅ FileVersion enum is complete');"

# 6. Run tests
npm test
```

### Fixture Tests

For every new/modified rule, write at least two synthetic stanza fixtures:

- One that **should fire** the rule
- One that **should not fire**

Test by requiring `out/semanticRules.js` directly against a minimal fake VS Code document object.

## Scope Limits

**Do not:**

- Modify `out/semanticRules.js` unless a rule genuinely cannot be expressed with existing primitives. If hitting this case, describe the gap in the PR instead of guessing.
- Add a `fix` block that changes data shape without conservative justification. Default to suggestion-only when unsure.
- Attempt to fix known engine gaps: line continuation parsing, duplicate stanza merging, `[default]` inheritance, cache invalidation.

**Do:**

- Bump the `version` field in `semantic_rules.json` (patch for additions/fixes)
- List in PR description: uncovered settings (with rationale), deprecated settings found, any engine gaps affecting new rules

## Worked Example

Existing rule in `semantic_rules.json`:

```json
{
  "id": "commands_python_version_deprecated",
  "trigger": {
    "setting_exists": "python.version",
    "without": ["python.required"]
  },
  "suggestion": {
    "severity": "warning",
    "title": "python.version deprecated in Splunk 10.2+",
    "message": "python.version is deprecated starting in Splunk 10.2. Add python.required for forward compatibility. When both are set, python.required takes precedence on 10.2+ while python.version serves as fallback for older versions.",
    "documentation": "https://docs.splunk.com/Documentation/Splunk/latest/Admin/Commands.conf",
    "deprecated_in": "10.2",
    "replacement": "python.required"
  }
}
```
