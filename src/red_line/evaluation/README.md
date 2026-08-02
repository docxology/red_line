# evaluation

The evaluation package contains the core policy function. It normalizes declared scope, checks the evidence-bearing intake, matches the live registry, and returns a single classification.

## Usage

```python
from red_line import ProposedAction, evaluate_action

assessment = evaluate_action(action)
print(assessment.classification)
```

## Related

- [../README.md](../README.md)
- [../../../docs/evaluator-semantics.md](../../../docs/evaluator-semantics.md)
- [../../../tests/evaluation/test_evaluator.py](../../../tests/evaluation/test_evaluator.py)

See [AGENTS.md](AGENTS.md) for the working contract.
