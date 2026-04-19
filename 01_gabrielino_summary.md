# Gabrielino Summary

## Counts

- Tournaments found involving Gabrielino in this Tabroom pass: 12
- Tournaments with extemp events identified: 11 definite, 1 uncertain (`Loyola Invitational`)
- Candidate extemp round-results pages identified: 83
- Usable round-results pages after filtering: 83

## Category Criteria

- `state qualifier`: tournament title explicitly includes `State Quals` or clearly functions as a state-qualifying league tournament. In this pass, `SCDL State Quals SPEECH` was treated as a state qualifier.
- `state`: tournament title or organizing context would need to indicate a state championship or state finals tournament. No Gabrielino-attended state championship tournament with clearly retrievable extemp round-results pages was confirmed in this pass.
- `national-qualifying`: tournament title or invite text explicitly includes `NSDA`, `Nat Quals`, or equivalent district national-qualifying language. In this pass, both `East Los Angeles NSDA 2025 Nat Quals Speech` and `East Los Angeles NSDA 2026 Nat Quals Speech` met this criterion.
- `major national-circuit`: large invitational tournaments with national-circuit reputation and substantial extemp elimination structures on Tabroom. In this pass, `39th Annual Stanford Invitational` clearly qualified; `Loyola Invitational` was treated as a likely major-circuit tournament, but its extemp results surface was not resolved cleanly enough to retain candidate pages.

## Exact HTML Signals Used For Usability

- Event-specific results index heading such as `US Extemp Results`, `International Extemp Results`, `Open Extemporaneous Results`, or `A National Extemp - Varsity Results`
- Round page heading such as `Round 1 Results`, `Round 5 Results`, `Semifinals`, or `Finals`
- Table header cell `Speaker`
- Section header cell `Sec`
- Competitor metadata columns including `Name` and/or `Institution`
- Judge columns labeled like `J1 – <judge name>`
- Numeric judge rank entries in the body rows

## Ambiguities And Assumptions

- Seasons were mapped to academic years, so fall 2022 and spring 2023 are both labeled `2022-23`, fall 2025 and spring 2026 are both labeled `2025-26`, and so on.
- Only Tabroom evidence was used for attendance confirmation. I did not supplement with off-Tabroom rosters or school schedules.
- For `East Los Angeles NSDA 2025` and `East Los Angeles NSDA 2026`, attendance was confirmed from event-results school columns because the tournament `schools.mhtml` page was not cleanly available in this session.
- For some local invitationals, the first elimination link appeared before `Round 3/2/1` without the label surfacing in the initial grep. Those rows were labeled `Finals` based on event-index ordering and the surrounding results structure.
- `Loyola Invitational` attendance was confirmed, but the extemp results surface did not resolve cleanly under the same tournament id in this pass, so no candidate pages were retained from Loyola.
- Older Gabrielino-hosted invitationals in 2022 and 2023 exposed extemp event selectors, but only cumulative `event_results` pages were visible for extemp, not usable judge-level `round_results` pages.
