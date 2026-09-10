---
name: ucc-add-field
description: Add a new field (entity) to an existing input or configuration tab in a Splunk UCC add-on's globalConfig.json, with the right component type and validators, and wire it into the matching Python code. Use when the user asks to add a new field, add a new setting, add a property, or add a parameter to an existing UCC input or configuration tab.
---

# UCC Add-on: Add a Field to an Existing Input or Tab

Adds a new field (`entity`) to an existing modular input service or configuration tab in `globalConfig.json`, choosing an appropriate [UCC component type](https://splunk.github.io/addonfactory-ucc-generator/entity/components/) and [validators](https://splunk.github.io/addonfactory-ucc-generator/entity/validators/), and updates the Python code that consumes it.

## When to Use

- User asks to "add a field to X input", "add a new setting", "add a checkbox/dropdown/text box for Y", or "add a parameter" to an existing service (`pages.inputs.services[]`) or configuration tab (`pages.configuration.tabs[]`) in `globalConfig.json`.
- Not for creating a brand-new input from scratch — use the `ucc-add-input` skill.
- Not for creating a brand-new configuration tab — use the `ucc-add-config-tab` skill.

## Prerequisites

- Find the target service/tab in `globalConfig.json` by `name`. If there are multiple candidates or the name is ambiguous, ask the user which one.
- Check existing `field` names in that service/tab's `entity` array to avoid collisions.

## Procedure

1. **Clarify the field's purpose** if not already clear: what value does it hold, is it required, does it have a small fixed set of choices (→ `singleSelect`/`radio`/`checkbox`), free text (→ `text`/`textarea`), a number/port/range, a secret (→ mark `encrypted: true` and consider `password`-style handling), a file upload, or multiple values (→ `multipleSelect`/`checkboxGroup`).

2. **Pick the component type** from the supported list — do not invent new `type` values:

   | Need | Component `type` |
   |---|---|
   | Free text / name | `text` |
   | Multi-line text | `textarea` |
   | One choice from a list (dropdown, optionally editable) | `singleSelect` |
   | Multiple choices from a list | `multipleSelect` |
   | Small fixed set, shown as buttons | `radio` |
   | On/off toggle | `checkbox` |
   | Group of related checkboxes | `checkboxGroup` / `checkboxTree` |
   | Date | `date` |
   | File upload | `file` |
   | Modular input collection interval | `interval` |
   | Splunk index picker | `index` |
   | Link/help text only | `helpLink` |

3. **Add the entity** to the service/tab's `entity` array, e.g.:
   ```json
   {
       "type": "singleSelect",
       "label": "Log Level",
       "field": "log_level",
       "help": "Select the logging verbosity for this input.",
       "options": {
           "disableSearch": true,
           "autoCompleteFields": [
               { "value": "DEBUG", "label": "Debug" },
               { "value": "INFO", "label": "Info" },
               { "value": "ERROR", "label": "Error" }
           ]
       },
       "defaultValue": "INFO",
       "required": true
   }
   ```

4. **Always include validators appropriate to the type**, or an explicit empty array if none apply:
   - Text/textarea: `string` (min/max length) and/or `regex`.
   - Numbers/ports: `number` with `range` (and `isInteger` if applicable).
   - URLs/emails/IPs: `url` / `email` / `ipv4`.
   - Combine validators in the array when more than one applies (e.g. `url` + `regex` for "https only").
   - If a field is validated/encapsulated elsewhere and genuinely needs no validator, add `"validators": []` rather than omitting the key, and mention this suggestion to the user rather than blocking the edit if they decline.
   - For secret/credential fields, set `"encrypted": true` and check whether the field belongs on an `account` tab instead of a plain input field.

5. **Update the table (optional)**: if the field should be visible in the Inputs/Configuration list view, add it to `table.header` on the same service/tab:
   ```json
   { "field": "log_level", "label": "Log Level" }
   ```

6. **Wire the field into Python code**:
   - If the service uses an `inputHelperModule`, read the value from `definition.parameters["<field>"]` (or `inputs.inputs[stanza]["<field>"]` in `stream_events`) inside that module — do not touch UCC-generated input files directly.
   - If the service uses a custom input script already copied into `package/bin/<input_name>.py`, add the equivalent parameter read there.
   - For configuration-tab fields (e.g. account/proxy/custom tab), the value is normally read via `solnlib`/`splunktaucclib` conf helpers (e.g. `<addon>_settings` or the account's REST endpoint) — locate the existing pattern used for other fields in that tab and follow it rather than introducing a new access pattern.
   - Grep the codebase for the tab/service's existing `field` names to find where sibling fields are already consumed, and mirror that style.

7. **Re-validate**: confirm the file still matches the UCC JSON schema (editor diagnostics), field names are unique within the entity array, and the field's `field` name matches exactly what the Python code reads.

8. **Tell the user next steps**: run `ucc-gen build` to regenerate `inputs.conf.spec` / `<addon>_settings.conf.spec` with the new parameter, and use **Preview globalConfig.json** to sanity-check the form rendering.

## Notes

- Field `type: "custom"` requires a companion React component (custom control) — flag this to the user rather than silently scaffolding UI code, since it's a larger effort outside this skill's scope.
- Never duplicate a `field` name within the same entity array — UCC will not distinguish them.
- Prefer the built-in `index` and `interval` types over hand-rolled `text` + validators when the field represents a Splunk index or collection interval.
