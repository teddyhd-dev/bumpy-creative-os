---
contract: creative
version: 1
path: brain/creatives/<code in lowercase>-<name>.md
id_format: "the concept code from the v5 ad name, unique ignoring case (core/naming-ad-v5.md); file name lowercase so it is safe on a Mac"
front_matter: [contract, code, name, decoded]
optional_front_matter: [aliases]
sections: [Decode]
decode_fields: [First second, Hook, Message, Format, Why it stops the thumb, Full breakdown, Snapshot, Decoded by]
generated_blocks: [facts]
written_by:
  Decode: brainstormer, with the strategist or designer (snapshot images in brain/creatives/img/)
  decoded: brainstormer (true once First second, Hook, Message and Why it stops the thumb are filled)
  facts block: engine/brain_sync.py, every Monday
read_by: [brainstormer, report]
---
# Contract: creative (version 1)

One file per concept (all its variants share the code). File name: the code in lowercase plus the concept
name, e.g. `k4rm9p-datingcontest.md`. Old ad names sometimes wrote one code with different letter case
(a2Ef3y / a2Ef3Y); when the name is the same they share one file and the other spellings are listed in
`aliases` for the creative lead to confirm. New codes must be unique ignoring case. It records **what the viewer sees** — the
first second, the hook, the message — once, so nobody is asked twice. Why it works *for a particular
audience* is written in that mind's history (`decode` entry), because the same creative can win in one
mind for one reason and fail in another.

The Monday run creates a file for every coded concept that becomes an adset's #1 (with `decoded: false`)
and keeps "Where it ran" current. The brainstormer asks for a decode when it meets `decoded: false` on a
current or past #1 of the mind it is working on. The first-second snapshot doubles as the thumbnail in
the weekly report.

## Template
```markdown
---
contract: creative/1
code: k4Rm9p
name: datingcontest
decoded: false
---
# k4Rm9p · datingcontest

## Decode
- First second:
- Hook:
- Message:
- Format:
- Why it stops the thumb:
- Full breakdown:
- Snapshot:
- Decoded by:

<!-- generated:start facts -->
<!-- generated:end facts -->
```
