import unittest

from arelight.third_party.transformers import init_token_classification_model, annotate_ner


class TestLoadModel(unittest.TestCase):

    model_names = [
        "dbmdz/bert-large-cased-finetuned-conll03-english",
        "dslim/bert-base-NER",
        "Babelscape/wikineural-multilingual-ner"
    ]

    def test(self):
        text = "My name is Sylvain, and I work at Hugging Face in Brooklyn."
        model, tokenizer = init_token_classification_model(self.model_names[0])
        results = annotate_ner(model=model, tokenizer=tokenizer, text=text)
        print(results)


if __name__ == '__main__':
    unittest.main()
