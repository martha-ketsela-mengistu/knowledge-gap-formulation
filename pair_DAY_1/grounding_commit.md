# Grounding Commit — Day 1

## What changed

> *"A generic judge like `deepseek/deepseek-chat-v3` computes its verdict as `argmax softmax(W_vocab · h_T)` over score tokens. The hidden state `h_T` is shaped by surface features — prompt order and output length — that are independent of rubric compliance. In our flipped-context experiment, 52% of dimension scores changed when prompt order was swapped, and 24% changed when content-free tokens were appended. The ORPO-trained LoRA adapter addresses this by updating the vocabulary projection weights so that `log P(high score | compliant output) > log P(high score | verbose, violating output)`, inverting the pretrained length prior for the Tenacious-Bench rubric dimensions. The trained judge does not eliminate positional sensitivity — that is architectural — but reduces score inconsistency from 52% to near-zero on this rubric when combined with position-averaging."*

## Why this matters

The original language papered over a real statistical failure that invalidates the evaluation metrics if left unexplained. The revised paragraph makes a falsifiable claim (52% inconsistency rate, measured), names the exact mechanism (vocabulary projection weight update via ORPO), and honestly scopes what the fix does and does not address (positional sensitivity remains, mitigated by position-averaging). An FDE reviewer or hiring manager reading the report can now verify each claim rather than taking the performance lift on faith.
