# Elicit a rule encoding

**Goal:** turn a written rule the expert knows cold into executable code with its edge cases.
**Output:** a decision table, an implementation, and a set of adversarial test cases.
**Never** a summary of the rule.

## Why we do it this way

The rule text is public. What is not public is which parts practitioners actually fight
over, which edge cases arise in practice, and which readings are wrong-but-plausible. That
tacit layer is the asset, and this session's whole purpose is to extract it into code.

## Session structure

### 1. Name the rule and its output type
What exactly does this rule produce — a date, a dollar amount, a code, a binary decision?
If the expert cannot state the output type in one sentence, the scope is too broad. Split it.

### 2. Enumerate the inputs
Every fact the rule consumes. For each: its type, its legal values, and **who supplies it**.
Inputs a practitioner would have to go look up are a signal the scope is still too broad.

### 3. Build the decision table
Walk input combinations to outputs. Write it as a table, live, in front of the expert.

Ask at every row: *"Is there a case where this row is wrong?"* The answer is where the value
is.

### 4. Hunt the edges — the part that matters
Push specifically on:
- Boundaries. What happens exactly at the threshold? On the day itself?
- Interactions. Which rules override this one, and when?
- Weekends, holidays, and end-of-period rollovers.
- Cases the expert has seen argued, or has personally gotten wrong.
- Cases where the plausible reading is the wrong one — **these are the highest-value test
  cases**, because they are exactly where a model will fail.

### 5. Encode it
Write the implementation during the session. Show the expert its output on their edge cases.
Every correction becomes a test.

### 6. Adversarial pass
Ask directly: *"How would a smart but lazy junior get this wrong in a way that looks right?"*

That answer becomes a red-team policy for the pack — the naive-calendar policy in
`legal/docket-deadlines` came from exactly this question.

## Deliverables

- [ ] `rules/<rule_id>.py` — the encoding
- [ ] `tests/test_<rule_id>.py` — one test per edge case, expert-attributed in a comment
- [ ] A red-team policy sketch from step 6
- [ ] Open questions logged explicitly — an unresolved question is a finding, not a failure

## Anti-patterns

- Producing prose. The artifact is code.
- Accepting "it depends" without decomposing what it depends on.
- Encoding only the happy path. The happy path is what a model already gets right.
- Letting the expert grade model outputs. That is `expert-review-verifier.md`, and it is a
  much lower-leverage use of their time.
