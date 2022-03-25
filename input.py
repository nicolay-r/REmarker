# Every example represents a list of strings (sentences), where
# each sentence may consist of particular words or `[named entities]`

EXAMPLES = {
    "simple": ["... [сша] намерена ввести санкции против [роccии] ...",
               "... При этом [Москва] неоднократно подчеркивала, что ее активность "
               "на балтике является ответом именно на действия [НАТО] и эскалацию "
               "враждебного подхода к [Росcии] вблизи ее восточных границ ..."],
    "no_entities": [
               "США намерена ввести санкции против Роccии. "
               "При этом Москва неоднократно подчеркивала, что ее активность "
               "на балтике является ответом именно на действия НАТО и эскалацию "
               "враждебного подхода к Росcии вблизи ее восточных границ."]
}