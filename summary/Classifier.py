import torch
from transformers import BertTokenizer, BertForSequenceClassification
import torch.nn.functional as F

class EmotionClassifier:
    def __init__(self, model_name="kykim/bert-kor-base"):
        self.model = BertForSequenceClassification.from_pretrained(model_name, num_labels=2)
        self.tokenizer = BertTokenizer.from_pretrained(model_name)

    def classify_emotion(self, text):
        tokens = self.tokenizer(text, padding=True, truncation=True, return_tensors="pt")

        with torch.no_grad():
            prediction = self.model(**tokens)

        prediction = F.softmax(prediction.logits, dim=1)
        output = prediction.argmax(dim=1).item()
        return output  # Return the predicted class label (0 or 1)

    def predict_and_calculate_ratio(self, input_sentences):
        # Classify emotions for each input sentence
        predictions = [self.classify_emotion(sentence) for sentence in input_sentences]

        # Calculate the ratio of 1s in the predictions
        ratio_of_ones = sum(predictions) / len(predictions)

        return ratio_of_ones * 100
