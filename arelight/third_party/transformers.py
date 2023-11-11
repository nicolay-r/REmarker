import numpy as np
import torch
from transformers import BertTokenizerFast, BertForTokenClassification


def init_token_classification_model(model_path):
    model = BertForTokenClassification.from_pretrained(model_path)
    tokenizer = BertTokenizerFast.from_pretrained(model_path)
    return model, tokenizer


def annotate_ner(model, tokenizer, text):
    """ This code is related to collection of the annotated objects from texts.

        return: list of dict
            every dict object contains entity, entity_group, location of the object
    """
    # Tokenize the text and get the offset mappings (start and end character positions for each token)
    inputs = tokenizer(text, return_tensors="pt", truncation=True)
    inputs_with_offsets = tokenizer(text, return_offsets_mapping=True)
    offsets = inputs_with_offsets["offset_mapping"]

    # Passing inputs into the model.
    outputs = model(**inputs)
    predictions = outputs.logits.argmax(dim=-1)[0].tolist()
    probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)[0].tolist()

    results = []
    idx = 0

    while idx < len(predictions):

        pred = predictions[idx]
        label = model.config.id2label[pred]

        if label != "O":
            label = label[2:]

            start, _ = offsets[idx]

            # Grab all the tokens labeled with I-label
            all_scores = []
            while (
                    idx < len(predictions)
                    and model.config.id2label[predictions[idx]] in [f"I-{label}", f"B-{label}"]
            ):
                all_scores.append(probabilities[idx][pred])
                _, end = offsets[idx]
                idx += 1

            score = np.mean(all_scores).item()
            word = text[start:end]

            results.append({
                    "entity_group": label,
                    "score": score,
                    "word": word,
                    "start": start,
                    "end": end
                }
            )
        idx += 1

    return results
