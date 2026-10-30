# Rejected cross-encoder experiment

After candidate 01's independent cases became diagnostic data, we tested the official Apache-2.0 `cross-encoder/ms-marco-MiniLM-L6-v2` ONNX model, revision `233902d25c440f23af6f7d6e94d2946bac0bee0a`, on the top twelve hybrid candidates.

It helped some literal questions but assigned very negative logits to several relevant literary paraphrases. It also ranked a historical storm paragraph as relevant to a question about tomorrow's forecast. It therefore could not serve as a trustworthy answerability gate. We rejected it rather than add another 91 MB model and imply that relevance establishes an answer.

Actual per-query outputs are in `reranker-diagnostic.json`; artifact provenance is in `reranker-manifest.json`. These are a development experiment, not a blind benchmark. The application does not load this model, and its setup script does not download it. The experimental local cache is excluded from the source package.
