import torch
from transformers import PreTrainedTokenizerFast, BartForConditionalGeneration


class Summarizer:
    def __init__(self, model_name='digit82/kobart-summarization'):
        self.tokenizer = PreTrainedTokenizerFast.from_pretrained(model_name)
        self.model = BartForConditionalGeneration.from_pretrained(model_name)

    def summarize(self, texts, max_length=512, num_beams=4):
        summaries = []

        for text in texts:
            raw_input_ids = self.tokenizer.encode(text)
            input_ids = [self.tokenizer.bos_token_id] + raw_input_ids + [self.tokenizer.eos_token_id]

            summary_ids = self.model.generate(torch.tensor([input_ids]), num_beams=num_beams, max_length=max_length,
                                              eos_token_id=1)
            summary = self.tokenizer.decode(summary_ids.squeeze().tolist(), skip_special_tokens=True)

            summaries.append(summary)

        return summaries
