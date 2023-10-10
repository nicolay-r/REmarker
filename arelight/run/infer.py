import argparse
from os.path import join, dirname

from arekit.common.data import const
from arekit.common.data.input.providers.text.single import BaseSingleTextProvider
from arekit.common.docs.entities_grouping import EntitiesGroupingPipelineItem
from arekit.common.experiment.data_type import DataType
from arekit.common.labels.base import NoLabel
from arekit.common.labels.scaler.single import SingleLabelScaler
from arekit.common.pipeline.base import BasePipeline
from arekit.common.synonyms.grouping import SynonymsCollectionValuesGroupingProviders
from arekit.common.text.parser import BaseTextParser
from arekit.contrib.bert.input.providers.text_pair import PairTextProvider
from arekit.contrib.utils.data.readers.jsonl import JsonlReader
from arekit.contrib.utils.data.storages.row_cache import RowCacheStorage
from arekit.contrib.utils.data.writers.json_opennre import OpenNREJsonWriter
from arekit.contrib.utils.io_utils.samples import SamplesIO
from arekit.contrib.utils.pipelines.items.text.terms_splitter import TermsSplitterParser
from arekit.contrib.utils.processing.lemmatization.mystem import MystemWrapper
from arekit.contrib.utils.synonyms.simple import SimpleSynonymCollection
from arekit.contrib.utils.synonyms.stemmer_based import StemmerBasedSynonymCollection

from arelight.doc_provider import InMemoryDocProvider
from arelight.pipelines.data.annot_pairs_nolabel import create_neutral_annotation_pipeline
from arelight.pipelines.demo.infer_bert import demo_infer_texts_bert_pipeline
from arelight.pipelines.demo.result import PipelineResult
from arelight.pipelines.items.entities_default import TextEntitiesParser
from arelight.pipelines.items.entities_ner_dp import DeepPavlovNERPipelineItem
from arelight.pipelines.items.utils import input_to_docs
from arelight.run import cmd_args
from arelight.run.entities.factory import create_entity_formatter
from arelight.run.entities.types import EntityFormattersService
from arelight.run.utils import merge_dictionaries, iter_group_values, translate_value, read_files
from arelight.samplers.bert import create_bert_sample_provider
from arelight.samplers.types import SampleFormattersService
from arelight.utils import IdAssigner

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Text inference example")

    # Providing arguments.
    cmd_args.FromDataframeArg.add_argument(parser)
    cmd_args.SentenceParserArg.add_argument(parser)
    cmd_args.TermsPerContextArg.add_argument(parser, default=50)
    parser.add_argument('--text', dest='input_text', type=str, default=None, nargs='?', help='Input text for processing')
    parser.add_argument('--from-files', dest='from_files', type=str, default=None, nargs='+')
    parser.add_argument('--ner-model-name', dest='ner_model_name', type=str, default="ner_ontonotes_bert_mult")
    parser.add_argument('--synonyms-filepath', dest='synonyms_filepath', type=str, default=None, help="List of synonyms provided in lines of the source text file.")
    parser.add_argument('--stemmer', dest='stemmer', type=str, default=None, choices=[None, "mystem"])
    parser.add_argument('--sampling-framework', dest='sampling_framework', type=str, choices=[None, "arekit"], default=None)
    parser.add_argument('--ner-types', dest='ner_types', type=str, default="ORG|PERSON|LOC|GPE", help="Filters specific NER types; provide with `|` separator")
    parser.add_argument("--ner-framework", dest="ner_framework", type=str, choices=[None, "deeppavlov"], default="deeppavlov")
    parser.add_argument('--translate-entity', dest='translate_entity', type=str, default=None)
    parser.add_argument("--docs-limit", dest="docs_limit", type=int, default=None)
    parser.add_argument('--entity-fmt', dest='entity_fmt', type=str, choices=list(EntityFormattersService.iter_names()), default="hidden-bert-styled")
    parser.add_argument('--text-b-type', dest='text_b_type', type=str, default="nli_m", choices=list(SampleFormattersService.iter_names()))
    parser.add_argument('--pretrained-bert', dest='pretrained_bert', type=str, default=None)
    parser.add_argument('--batch-size', dest='batch_size', type=int, default=10, nargs='?')
    parser.add_argument('--tokens-per-context', dest='tokens_per_context', type=int, default=128, nargs='?')
    parser.add_argument("--bert-framework", dest="bert_framework", type=str, default=None, choices=[None, "opennre", "deeppavlov"])
    parser.add_argument("--bert-torch-checkpoint", dest="bert_torch_checkpoint", type=str)
    parser.add_argument("--device-type", dest="device_type", type=str, default="cpu", choices=["cpu", "gpu"])
    parser.add_argument("--backend", dest="backend", type=str, default=None, choices=[None, "brat", "d3js_graphs"])
    parser.add_argument("--d3js-host", dest="d3js_host", default=None, type=str)
    parser.add_argument('-o', dest='output_template', type=str, default=None, nargs='?')

    # Parsing arguments.
    args = parser.parse_args()

    # Reading text-related parameters.
    sentence_parser = cmd_args.SentenceParserArg.read_argument(args)
    texts_from_files = read_files(args.from_files)
    text_from_arg = args.input_text
    texts_from_dataframe = cmd_args.FromDataframeArg.read_argument(args)
    ner_framework = args.ner_framework
    ner_model_name = args.ner_model_name
    ner_object_types = args.ner_types
    terms_per_context = cmd_args.TermsPerContextArg.read_argument(args)
    actual_content = [text_from_arg] if text_from_arg is not None else \
        texts_from_files if texts_from_files is not None else texts_from_dataframe
    docs_limit = args.docs_limit
    output_template = args.output_template
    output_dir = dirname(args.output_template) if dirname(args.output_template) != "" else args.output_template

    labels_scaler = SingleLabelScaler(NoLabel())

    sampling_engines_setup = {
        None: {},
        "arekit": {
            "rows_provider": create_bert_sample_provider(
                provider_type=SampleFormattersService.name_to_type(args.text_b_type),
                # We annotate everything with NoLabel.
                label_scaler=SingleLabelScaler(NoLabel()),
                entity_formatter=create_entity_formatter(EntityFormattersService.name_to_type(args.entity_fmt))),
            "samples_io": SamplesIO(target_dir=output_dir,
                                    prefix="samples",
                                    reader=JsonlReader(),
                                    writer=OpenNREJsonWriter(
                                        text_columns=[BaseSingleTextProvider.TEXT_A, PairTextProvider.TEXT_B],
                                        keep_extra_columns=True,
                                        # `0` basically.
                                        na_value=str(labels_scaler.label_to_uint(NoLabel())))),
            "storage": RowCacheStorage(
                force_collect_columns=[const.ENTITIES, const.ENTITY_VALUES, const.ENTITY_TYPES, const.SENT_IND]),
            "save_labels_func": lambda data_type: data_type != DataType.Test
        }
    }

    stemmer_types = {
        None: lambda: None,
        "mystem": lambda: MystemWrapper()
    }

    stemmer = stemmer_types[args.stemmer]()

    def __entity_display_value(entity_value):
        """ This function describes how the result entity is expected to be visualized
            and passed for further components of the pipeline after serialization.
        """

        display_value = entity_value

        if stemmer is not None:
            display_value = stemmer.lemmatize_to_str(display_value)

        if args.translate_entity is not None:
            src, dest = args.translate_entity.split(':')
            display_value = translate_value(display_value, src=src, dest=dest)

        return display_value

    entity_parsers = {
        # Default parser.
        None: lambda: TextEntitiesParser(id_assigner=IdAssigner(),
                                         display_value_func=__entity_display_value),
        # Parser based on DeepPavlov backend.
        "deeppavlov": lambda: DeepPavlovNERPipelineItem(
            obj_filter=None if ner_object_types is None else lambda s_obj: s_obj.ObjectType in ner_object_types,
            ner_model_name=ner_model_name,
            id_assigner=IdAssigner(),
            display_value_func=__entity_display_value)
    }

    infer_engines_setup = {
        None: {},
        "opennre": {
            "pretrained_bert": args.pretrained_bert,
            "checkpoint_path": args.bert_torch_checkpoint,
            "device_type": args.device_type,
            "max_seq_length": args.tokens_per_context,
            "batch_size": args.batch_size,
            "pooler": "cls",
        },
        "deeppavlov": {
            "pretrained_bert": args.pretrained_bert,
            "batch_size": args.batch_size,
            "max_seq_length": args.tokens_per_context,
        }
    }

    backend_setups = {
        None: {},
        "d3js_graphs": {
            "operation_type": "SAME",
            "graph_min_links": 1,
            "op_min_links": 0.1,
            "ui_output": ["radial", "force"],
            "graph_a_labels": None,
            "graph_b_labels": None,
            "weights": True,
        }
    }

    # Setup main pipeline.
    pipeline = demo_infer_texts_bert_pipeline(
        sampling_engines={key: sampling_engines_setup[key] for key in [args.sampling_framework]},
        infer_engines={key: infer_engines_setup[key] for key in [args.bert_framework]},
        backend_engines={key: backend_setups[key] for key in [args.backend]})

    pipeline = BasePipeline(pipeline)

    # Settings.
    settings = []

    if args.sampling_framework == "arekit":

        synonyms_setup = {
            None: lambda: SimpleSynonymCollection(
                iter_group_values_lists=iter_group_values(args.synonyms_filepath),
                is_read_only=False),
            "lemmatized": lambda: StemmerBasedSynonymCollection(
                iter_group_values_lists=iter_group_values(args.synonyms_filepath),
                stemmer=stemmer,
                is_read_only=False)
        }

        # Create Synonyms Collection.
        synonyms = synonyms_setup["lemmatized" if args.stemmer is not None else None]()

        # Setup text parser.
        text_parser = BaseTextParser(pipeline=[
            TermsSplitterParser(),
            entity_parsers[ner_framework](),
            EntitiesGroupingPipelineItem(
                lambda value: SynonymsCollectionValuesGroupingProviders.provide_existed_or_register_missed_value(
                    synonyms=synonyms, value=value))
        ])

        # Setup data annotation pipeline.
        docs = input_to_docs(actual_content, sentence_parser=sentence_parser, docs_limit=docs_limit)
        doc_provider = InMemoryDocProvider(docs)
        data_pipeline = create_neutral_annotation_pipeline(
            synonyms=synonyms,
            dist_in_terms_bound=terms_per_context,
            doc_provider=doc_provider,
            terms_per_context=terms_per_context,
            text_parser=text_parser)

        settings.append({
            "data_type_pipelines": {DataType.Test: data_pipeline},
            "doc_ids": list(range(len(doc_provider)))
        })

    if args.backend == "brat":
        settings.append({
            "backend_template": output_template,
            "template_filepath": join(output_dir, "brat_template.html"),
            "brat_url": "http://localhost:8001/",
            "brat_vis_fp": "{}.html".format(output_template) if output_template is not None else None,
        })

    # Launch application.
    pipeline.run(
        input_data=PipelineResult({
            # We provide this settings for inference.
            "predict_filepath": join(output_dir, "predict.tsv.gz"),
            "samples_io": sampling_engines_setup["arekit"]["samples_io"],
            "d3js_graph_output_dir": output_dir,
            "d3js_graph_do_save": True,
            "d3js_graph_launch_server": args.d3js_host,
            "d3js_host": args.d3js_host,
        }),
        params_dict=merge_dictionaries(settings))
