# Outer-code matrices

[H_15_9_3.txt](H_15_9_3.txt) and [H_15_6_5.txt](H_15_6_5.txt) define the outer codes in the headline comparison. Each row is a parity check over the repetition blocks indexed by its columns; entries are binary and arithmetic is modulo two.

Both are numerical transcriptions of Appendix C of the [Elevator Codes paper, version 2](https://arxiv.org/abs/2601.10786v2). [Provenance and SHA-256 checksums](../README.md) identify the inputs. [`codes.py`](../../elevator/codes.py) loads them and calculates their dimensions and distances; [tests](../../tests/test_core.py) check those parameters.
