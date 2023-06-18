import aws_cdk as core
import aws_cdk.assertions as assertions
from codepipeline_cdk_sample.codepipeline_cdk_sample_stack import CodepipelineCdkSampleStack


def test_sqs_queue_created():
    app = core.App()
    stack = CodepipelineCdkSampleStack(app, "codepipeline-cdk-sample")
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("AWS::SQS::Queue", {
        "VisibilityTimeout": 300
    })


def test_sns_topic_created():
    app = core.App()
    stack = CodepipelineCdkSampleStack(app, "codepipeline-cdk-sample")
    template = assertions.Template.from_stack(stack)

    template.resource_count_is("AWS::SNS::Topic", 1)
