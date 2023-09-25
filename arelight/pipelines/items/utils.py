from os.path import join, exists

from arekit.common.utils import download
from arekit.common.docs.base import Document
from arekit.common.docs.sentence import BaseDocumentSentence

from arelight.run.utils import logger


def input_to_docs(input_data, sentence_parser):
    """ input_data: list
        sentence_splitter: object
            how data is suppose to be separated onto sentences.
            str -> list(str)
    """
    assert(input_data is not None)

    docs = []

    for doc_id, contents in enumerate(input_data):
        # setup input data.
        sentences = sentence_parser(contents)
        sentences = list(map(lambda text: BaseDocumentSentence(text), sentences))
        # Documents.
        docs.append(Document(doc_id=doc_id, sentences=sentences))

    return docs


def try_download_predefined_checkpoints(checkpoint, dir_to_download):
    """ This is for the simplicity of using the framework straightaway.
    """
    assert(isinstance(checkpoint, str))
    assert(isinstance(dir_to_download, str))

    predefined_checkponts = {
        "ra4-rsr1_DeepPavlov-rubert-base-cased_cls.pth.tar":
            "https://www.dropbox.com/scl/fi/rwjf7ag3w3z90pifeywrd/ra4-rsr1_DeepPavlov-rubert-base-cased_cls.pth.tar?rlkey=p0mmu81o6c2u6iboe9m20uzqk&dl=1"
    }

    if checkpoint in predefined_checkponts:
        url = predefined_checkponts[checkpoint]
        target_path = join(dir_to_download, checkpoint)

        logger.info("Found predefined checkpoint: {}".format(checkpoint))

        # No need to do anything, file has been already downloaded.
        if exists(target_path):
            return

        logger.info("Downloading checkpoint to: {}".format(target_path))

        download(dest_file_path=target_path, source_url=url)
