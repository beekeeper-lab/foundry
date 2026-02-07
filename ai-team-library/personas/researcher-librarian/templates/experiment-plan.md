# Experiment Plan

## Metadata

| Field         | Value                                       |
|---------------|---------------------------------------------|
| Date          | [YYYY-MM-DD]                                |
| Owner         | [Researcher name / role]                     |
| Related links | [Research memo, decision matrix, issue/ticket]|
| Status        | Draft / Reviewed / Approved                 |

## Hypothesis

*State what you believe to be true and what this experiment will validate or invalidate.*

[If we do X, then Y will happen, because Z.]

## Success Criteria

*Define measurable outcomes that determine whether the hypothesis is confirmed.*

- [ ] [Criterion 1 -- specific, measurable result that indicates success]
- [ ] [Criterion 2 -- e.g., "Response time under 200ms at 100 concurrent requests"]
- [ ] [Criterion 3 -- e.g., "Integration completes without manual data transformation"]

## Time Box

*Set a hard limit to prevent scope creep.*

- **Maximum duration**: [e.g., 2 days, 4 hours, 1 sprint]
- **Start date**: [YYYY-MM-DD]
- **Hard stop**: [YYYY-MM-DD]
- **Check-in point**: [Midway date -- assess progress and decide whether to continue]

## Approach

*Describe what you will build, configure, or test. Keep it minimal -- just enough to validate the hypothesis.*

[High-level description of the spike, prototype, or test. Include what is in scope and explicitly what is out of scope.]

## Resources Needed

*List what you need before starting.*

- [Access to a specific system or environment]
- [Sample data or test fixtures]
- [Collaboration from a specific person or team]
- [Budget approval for a service or tool trial]

## Steps

*Numbered sequence of actions to run the experiment.*

1. [Set up the environment or test harness]
2. [Implement the minimum necessary to test the hypothesis]
3. [Run the test or exercise the prototype]
4. [Collect measurements and observations]
5. [Compare results against success criteria]
6. [Document findings]

## Expected Artifacts

*What this experiment will produce, regardless of outcome.*

- [Working prototype / throwaway code (specify if it should be kept or discarded)]
- [Performance measurements or benchmark data]
- [Written summary of findings]
- [Updated recommendation in research memo or decision matrix]

## Decision After Experiment

*Define what happens based on the outcome.*

- **If hypothesis confirmed**: [Next steps -- e.g., proceed to implementation, write ADR, update decision matrix]
- **If hypothesis rejected**: [Next steps -- e.g., evaluate next option, revise approach, abandon this direction]
- **If inconclusive**: [Next steps -- e.g., extend time box by X, narrow scope, escalate for input]

## Risks

*What could go wrong with the experiment itself.*

| Risk | Impact | Mitigation |
|------|--------|------------|
| [Time box exceeded without results] | [Delayed decision] | [Hard stop with findings documented regardless] |
| [Test environment differs from production] | [Results may not transfer] | [Document assumptions and environment differences] |
| [Key dependency unavailable] | [Experiment blocked] | [Identify backup approach or alternative resource] |

## Definition of Done

- [ ] Hypothesis is clearly stated and testable
- [ ] Success criteria are measurable
- [ ] Time box is set and respected
- [ ] Steps are completed or time box is reached
- [ ] Results are documented against success criteria
- [ ] Decision is made and communicated based on outcome
