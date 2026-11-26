# Written review and transparency {#sec:review}

Turner uses a standing Review Body and a fixed vocabulary of findings
[@turner2026redline]. Red Line cannot recreate that institutional separation.
It keeps the durable local outputs: a written finding for each reviewed action
and a tally that makes classifications and escalations visible.

## Finding record

`review_engagement` returns a frozen `ReviewFinding` containing the engagement,
classification, implicated line ids, finding text, review date, declared scope,
tier, and ambiguity flag. The evaluator is run as of that review date, so a
finding cannot silently describe one date while evaluating freshness at another.
The finding preserves `INSUFFICIENT_INFORMATION` as a blocking result; it does
not turn incomplete intake into a policy judgment.

The result vocabulary is:

| Result | Meaning |
|---|---|
| `INSUFFICIENT_INFORMATION` | required context or evidence is unresolved; stop |
| `NON_COMPLIANT` | a line is implicated without a verified narrowing condition |
| `REQUIRES_MODIFICATION` | a verified exemption still has a dimension or tier problem |
| `COMPLIANT` | complete intake and verified exemption satisfy the local registry |
| `OUTSIDE_SCOPE` | complete intake, but no current registry line applies |

Outside scope is not a compliance certification. It says only that this
registry did not match the documented action. A transparency report aggregates
the findings supplied to it; it is not an automatic publication channel or a
third-party audit.

## Escalation is not permission

The former boolean override was too easy to misread as authorization. The new
`ReviewAuthorization` records `authorized_by`, `authority`, `rationale`, and
`recorded_on`. It is an escalation or remediation record. A finding remains
blocking when its classification is `NON_COMPLIANT`, `REQUIRES_MODIFICATION`,
or `INSUFFICIENT_INFORMATION`; the transparency report counts the named
authorization without changing that fact.

This is a deliberate difference from institutional governance. The author can
make an exception visible, but cannot make the personal “No” disappear by
calling it an override.
