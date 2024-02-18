"""This module should not be used directly as its API is subject to change. Instead,
please use the `gr.Interface.from_pipeline()` function."""

from __future__ import annotations

from typing import Any

from gradio.pipelines_helpers import (
    _handle_diffusers_pipeline,
    _handle_transformers_pipeline,
)


def load_from_pipeline(pipeline: Any) -> dict:
    """
    Gets the appropriate Interface kwargs for a given Hugging Face transformers.Pipeline.
    pipeline (transformers.Pipeline): the transformers.Pipeline from which to create an interface
    Returns:
    (dict): a dictionary of kwargs that can be used to construct an Interface object
    """


    # module of pipeline will look like this:
    # for transformers.pipelines: transformers.pipelines.xxxxxx.xxxx
    # for diffusers.pipelines: diffusers.pipelines.xxxxx.xxxx
    if str(type(pipeline).__module__).startswith("transformers.pipelines"):
        pipeline_info = _handle_transformers_pipeline(pipeline)

    elif str(type(pipeline).__module__).startswith("diffusers.pipelines"):
        pipeline_info = _handle_diffusers_pipeline(pipeline)

    else:
        raise ValueError(
            "pipeline must be a transformers.pipeline or diffusers.pipeline"
        )

    # define the function that will be called by the Interface
    def fn(*params):
        data = pipeline_info["preprocess"](*params)
        if str(type(pipeline).__module__).startswith("transformers.pipelines"):
            from transformers import pipelines

            # special cases that needs to be handled differently
            if isinstance(
                pipeline,
                (
                    pipelines.text_classification.TextClassificationPipeline,
                    pipelines.text2text_generation.Text2TextGenerationPipeline,
                    pipelines.text2text_generation.TranslationPipeline,
                ),
            ):
                data = pipeline(*data)
            else:
                data = pipeline(**data)
            # special case for object-detection
            # original input image sent to postprocess function
            if isinstance(
                pipeline,
                pipelines.object_detection.ObjectDetectionPipeline,
            ):
                output = pipeline_info["postprocess"](data, params[0])
            else:
                output = pipeline_info["postprocess"](data)
            return output

        elif str(type(pipeline).__module__).startswith("diffusers.pipelines"):
            data = pipeline(**data)
            output = pipeline_info["postprocess"](data)
            return output

    interface_info = pipeline_info.copy()
    interface_info["fn"] = fn
    del interface_info["preprocess"]
    del interface_info["postprocess"]

    # define the title/description of the Interface
    interface_info["title"] = (
        pipeline.model.__class__.__name__
        if str(type(pipeline).__module__).startswith("transformers.pipelines")
        else pipeline.__class__.__name__
    )

    return interface_info
