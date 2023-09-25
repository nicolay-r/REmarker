from arekit.common.pipeline.context import PipelineContext
from arekit.contrib.utils.pipelines.items.sampling.base import BaseSerializerPipelineItem


class AREkitSerializerPipelineItem(BaseSerializerPipelineItem):
    """ This is a local version of the AREkit sampler, which additionally provides
        hosting of the results into input_data structure.
    """

    def apply_core(self, input_data, pipeline_ctx):
        assert(isinstance(input_data, PipelineContext))
        super(AREkitSerializerPipelineItem, self).apply_core(input_data=input_data,
                                                             pipeline_ctx=pipeline_ctx)

        # Host samples into the result for further pipeline items.
        input_data.update("samples_io", self._samples_io)
